import uuid
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.session_manager import session_manager
from app.services.llm_service import extract_slots, map_extracted_to_slots
from app.services.drg_service import drg_service

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    result: Optional[Dict[str, Any]] = None
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    session = session_manager.get_session(session_id)

    user_message = request.message.strip()

    # 如果正在等待确认
    if session.status == "AWAITING_CONFIRMATION":
        if user_message in ("确认", "是", "yes", "ok"):
            # 执行分组
            try:
                result = drg_service.group_from_structured(
                    main_diag=session.main_diag,
                    other_diags=session.other_diags,
                    main_proc=session.main_proc or "",
                    other_procs=session.other_procs,
                    age_days=session.age_days
                )
                session.status = "DONE"
                # 构造结果回复
                reply = f"分组完成！\nMDC: {result['MDC']}\nADRG: {result['ADRG']} {result.get('ADRG_NAME', '')}\nDRG: {result['DRG']} {result.get('DRG_NAME', '')}\n并发症等级: {result['COMPLICATION']}"
                return ChatResponse(reply=reply, result=result, session_id=session_id)
            except Exception as e:
                return ChatResponse(reply=f"分组失败: {str(e)}", session_id=session_id)
        else:
            # 用户未确认，可能想修改信息，回到收集状态
            session.status = "COLLECTING"
            # 可选择性清除已确认的槽位？我们保留现有槽位，让用户通过新消息修改
            # 但需要一种方式让用户指定修改哪个字段，暂时让大模型重新提取
            # 简化：直接进入收集状态，让用户重新输入完整信息
            return ChatResponse(
                reply="好的，请重新输入您的诊断和手术信息，或提供需要修改的内容。",
                session_id=session_id
            )

    # 收集状态：调用大模型提取槽位
    # 这里可以传入历史对话，但为了简化，只发送当前消息
    # 实际可维护一个消息列表，但我们的会话状态暂不保存历史
    extracted = extract_slots(user_message)
    if not extracted:
        return ChatResponse(reply="未能识别诊断信息，请提供主诊断和年龄。", session_id=session_id)

    slots = map_extracted_to_slots(extracted)

    # 处理冲突
    if slots.get("conflicts"):
        # 生成追问，例如“诊断‘xxx’对应多个编码：1. G91.900 2. G91.901，请选择序号”
        conflict_msgs = []
        for conflict in slots["conflicts"]:
            if conflict["options"]:
                opts = "\n".join([f"{i + 1}. {c}" for i, c in enumerate(conflict["options"])])
                conflict_msgs.append(f"{conflict['type']} '{conflict['name']}' 对应多个编码，请选择：\n{opts}")
            else:
                conflict_msgs.append(f"{conflict['type']} '{conflict['name']}' 未找到对应编码，请提供标准编码。")
        reply = "请确认以下信息：\n" + "\n".join(conflict_msgs)
        return ChatResponse(reply=reply, session_id=session_id)

    # 更新槽位
    update_data = {k: v for k, v in slots.items() if
                   k in ("main_diag", "other_diags", "main_proc", "other_procs", "age_days")}
    updated = session.update_slots(**update_data)

    if updated:
        # 所有必填字段已填，展示确认信息
        summary = f"主要诊断：{session.main_diag}\n次要诊断：{', '.join(session.other_diags) if session.other_diags else '无'}\n主要手术：{session.main_proc if session.main_proc else '无'}\n其他手术：{', '.join(session.other_procs) if session.other_procs else '无'}\n年龄：{session.age_days} 天"
        session.status = "AWAITING_CONFIRMATION"
        reply = f"请确认以下信息是否正确：\n{summary}\n\n回复“确认”开始分组，回复其他内容修改信息。"
    else:
        # 还有缺项，提示缺什么
        missing = []
        if session.main_diag is None: missing.append("主要诊断")
        if session.age_days is None: missing.append("年龄")
        reply = f"请补充以下信息：{', '.join(missing)}"
        if slots.get("age_days") is None and "年龄" not in user_message:
            reply += "\n例如：年龄 45 岁"

    return ChatResponse(reply=reply, session_id=session_id)
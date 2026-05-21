import uuid
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
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
    need_confirm: bool = False


class ClearRequest(BaseModel):
    session_id: str
    fields: Optional[List[str]] = None


class ClearResponse(BaseModel):
    reply: str
    session_id: str
    cleared_fields: List[str]
    is_complete: bool = False
    slots_summary: Optional[Dict[str, Any]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    session = session_manager.get_session(session_id)

    user_message = request.message.strip()

    # 如果正在等待确认
    if session.status == "AWAITING_CONFIRMATION":
        if user_message == "__CONFIRM__" or user_message in ("确认", "是", "yes", "ok"):
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

                # 检查STATUS是否为SUCCESS
                if result.get("STATUS") != "SUCCESS":
                    session.clear_slots()
                    session.status = "COLLECTING"
                    reply = "分组失败，已清除所有数据，请确认数据是否正确，并重新输入"
                    return ChatResponse(reply=reply, session_id=session_id)

                # 构造结果回复
                reply = f"分组完成！\nMDC: {result['MDC']}\nADRG: {result['ADRG']} {result.get('ADRG_NAME', '')}\nDRG: {result['DRG']} {result.get('DRG_NAME', '')}\n并发症等级: {result['COMPLICATION']}"
                return ChatResponse(reply=reply, result=result, session_id=session_id)
            except Exception as e:
                session.clear_slots()
                session.status = "COLLECTING"
                return ChatResponse(reply="分组失败，已清除所有数据，请确认数据是否正确，并重新输入", session_id=session_id)
        elif user_message == "__MODIFY__":
            # 用户点击修改按钮
            session.status = "COLLECTING"
            return ChatResponse(
                reply="好的，请输入需要修改的信息。",
                session_id=session_id
            )
        else:
            # 用户未确认，可能想修改信息，回到收集状态
            session.status = "COLLECTING"
            return ChatResponse(
                reply="好的，请重新输入您的诊断和手术信息，或提供需要修改的内容。",
                session_id=session_id
            )

    # 收集状态：调用大模型提取槽位
    extracted = extract_slots(user_message)
    if not extracted:
        return ChatResponse(reply="未能识别诊断信息，请提供主诊断和年龄。", session_id=session_id)

    slots = map_extracted_to_slots(extracted)

    # 处理冲突
    if slots.get("conflicts"):
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
        reply = f"请确认以下信息是否正确：\n{summary}"
        return ChatResponse(reply=reply, session_id=session_id, need_confirm=True)
    else:
        # 还有缺项，提示缺什么
        missing = []
        if session.main_diag is None: missing.append("主要诊断")
        if session.age_days is None: missing.append("年龄")
        reply = f"请补充以下信息：{', '.join(missing)}"
        if slots.get("age_days") is None and "年龄" not in user_message:
            reply += "\n例如：年龄 45 岁"

    return ChatResponse(reply=reply, session_id=session_id)


@router.post("/clear", response_model=ClearResponse)
async def clear_session(request: ClearRequest):
    """清除会话中的指定字段或全部字段"""
    session = session_manager.get_session(request.session_id)

    is_all_clear = request.fields is None or len(request.fields) == 0
    
    if is_all_clear:
        # 清除所有字段
        session.clear_slots()
        cleared = ["main_diag", "other_diags", "main_proc", "other_procs", "age_days"]
        reply = "已清除所有信息，请输入诊断信息。"
    else:
        session.clear_slots(request.fields)
        cleared = request.fields
        field_names = {
            "main_diag": "主要诊断",
            "other_diags": "次要诊断",
            "main_proc": "主要手术",
            "other_procs": "其他手术",
            "age_days": "年龄"
        }
        names = [field_names.get(f, f) for f in cleared]
        reply = f"已清除：{'、'.join(names)}"

    # 如果之前在等待确认状态，清除后重新进入收集状态
    session.status = "COLLECTING"

    # 检查是否满足分组条件
    is_complete = session.is_complete()
    
    if not is_all_clear and is_complete:
        # 满足分组条件，显示确认信息
        summary = f"主要诊断：{session.main_diag}\n次要诊断：{', '.join(session.other_diags) if session.other_diags else '无'}\n主要手术：{session.main_proc if session.main_proc else '无'}\n其他手术：{', '.join(session.other_procs) if session.other_procs else '无'}\n年龄：{session.age_days} 天"
        reply += f"\n请确认以下信息是否正确：\n{summary}"
        session.status = "AWAITING_CONFIRMATION"
    elif not is_all_clear and not is_complete:
        # 不满足分组条件，提示缺少的信息
        missing = []
        if session.main_diag is None: 
            missing.append("主要诊断")
        if session.age_days is None: 
            missing.append("年龄")
        if missing:
            reply += f"\n请补充以下信息：{', '.join(missing)}"

    return ClearResponse(
        reply=reply, 
        session_id=request.session_id, 
        cleared_fields=cleared,
        is_complete=is_complete,
        slots_summary=session.get_slots_summary()
    )

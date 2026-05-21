import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-api-key")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"

# 加载名称到编码映射
ENGINE_DIR = Path(__file__).parent.parent.parent.parent / "engine"
with open(ENGINE_DIR / "name2code.json", "r", encoding="utf-8") as f:
    NAME2CODE = json.load(f)


def call_deepseek(messages: list[dict]) -> str:
    """调用 DeepSeek 模型，返回文本回复"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 500
    }
    resp = requests.post(
        f"{DEEPSEEK_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def extract_slots(user_message: str, conversation_history: list[dict] = None) -> dict:
    """
    使用 DeepSeek 从用户消息中提取槽位。
    返回：{
        "main_diag_name": str,
        "main_diag_code": str,
        "other_diag_list": [{"name": str, "code": str}],
        "main_proc_name": str,
        "main_proc_code": str,
        "other_proc_list": [{"name": str, "code": str}],
        "age_days": int or null
    }
    """
    system_prompt = """你是一个医疗信息提取助手。从用户输入中提取以下字段，返回 JSON：
- main_diag_name: 主要诊断名称或编码，如“脑积水”
- main_diag_code: 如果用户直接提供了诊断编码，填写编码；否则为空字符串
- other_diag_list: 次要诊断列表，每个元素包含 name 和 code，code 若未提供则为空字符串
- main_proc_name: 主要手术名称或编码
- main_proc_code: 如果用户直接提供了手术编码，填写编码；否则为空字符串
- other_proc_list: 其他手术列表，每个元素包含 name 和 code
- age_days: 年龄天数（数字），如果用户说“35岁”，则填 35*365。若未提到年龄则为 null。

注意：只返回 JSON 对象，不要其他文字。"""

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    reply = call_deepseek(messages)
    # 尝试解析 JSON
    try:
        # 可能包含反引号，去掉
        clean = reply.replace("```json", "").replace("```", "").strip()
        extracted = json.loads(clean)
    except json.JSONDecodeError:
        # 如果失败，返回空槽位
        extracted = {}
    return extracted


def resolve_code(name: str, field_type: str) -> Optional[str]:
    """根据名称查找唯一编码，若多个则返回 None（需要用户选择）"""
    if name in NAME2CODE:
        codes = NAME2CODE[name]
        if len(codes) == 1:
            return codes[0]
        else:
            return None  # 多个编码，需要追问
    return None


def map_extracted_to_slots(extracted: dict) -> dict:
    """
    将 LLM 提取结果映射为槽位，尽可能转换名称到编码。
    返回：{ main_diag, other_diags, main_proc, other_procs, age_days, conflicts }
    conflicts 是冲突列表，如 [{"type":"diagnosis","name":"xxx","options":["code1","code2"]}]
    
    注意：只有当用户明确提供信息时才设置字段，未提到的字段不包含在返回结果中。
    空列表 [] 表示用户明确想清空该字段。
    """
    slots = {}
    conflicts = []

    # 处理主诊断
    main_diag_code = extracted.get("main_diag_code")
    main_diag_name = extracted.get("main_diag_name")
    # 只有当用户明确提供了主诊断信息时才设置
    if main_diag_code or main_diag_name:
        if main_diag_code:
            slots["main_diag"] = main_diag_code
        elif main_diag_name:
            code = resolve_code(main_diag_name, "diagnosis")
            if code:
                slots["main_diag"] = code
            else:
                if main_diag_name in NAME2CODE:
                    conflicts.append({"type": "diagnosis", "name": main_diag_name, "options": NAME2CODE[main_diag_name]})
                else:
                    conflicts.append({"type": "diagnosis", "name": main_diag_name, "options": []})

    # 处理其他诊断 - 只有当用户明确提供了内容时才设置
    other_diag_list = extracted.get("other_diag_list")
    if other_diag_list and len(other_diag_list) > 0:
        other_diags = []
        for item in other_diag_list:
            code = item.get("code")
            name = item.get("name")
            if code:
                other_diags.append(code)
            elif name:
                res = resolve_code(name, "diagnosis")
                if res:
                    other_diags.append(res)
                else:
                    if name in NAME2CODE:
                        conflicts.append({"type": "other_diagnosis", "name": name, "options": NAME2CODE[name]})
                    else:
                        conflicts.append({"type": "other_diagnosis", "name": name, "options": []})
        slots["other_diags"] = other_diags

    # 处理主手术 - 只有当用户明确提供了信息时才设置
    main_proc_code = extracted.get("main_proc_code")
    main_proc_name = extracted.get("main_proc_name")
    if main_proc_code or main_proc_name:
        if main_proc_code:
            slots["main_proc"] = main_proc_code
        elif main_proc_name:
            code = resolve_code(main_proc_name, "procedure")
            if code:
                slots["main_proc"] = code
            else:
                if main_proc_name in NAME2CODE:
                    conflicts.append(
                        {"type": "main_procedure", "name": main_proc_name, "options": NAME2CODE[main_proc_name]})
                else:
                    conflicts.append({"type": "main_procedure", "name": main_proc_name, "options": []})

    # 处理其他手术 - 只有当用户明确提供了内容时才设置
    other_proc_list = extracted.get("other_proc_list")
    if other_proc_list and len(other_proc_list) > 0:
        other_procs = []
        for item in extracted.get("other_proc_list", []):
            code = item.get("code")
            name = item.get("name")
            if code:
                other_procs.append(code)
            elif name:
                res = resolve_code(name, "procedure")
                if res:
                    other_procs.append(res)
                else:
                    if name in NAME2CODE:
                        conflicts.append({"type": "other_procedure", "name": name, "options": NAME2CODE[name]})
                    else:
                        conflicts.append({"type": "other_procedure", "name": name, "options": []})
        slots["other_procs"] = other_procs

    # 处理年龄 - 只有当用户明确提供了信息时才设置
    age = extracted.get("age_days")
    if age is not None:
        try:
            slots["age_days"] = int(age)
        except (ValueError, TypeError):
            pass

    slots["conflicts"] = conflicts
    return slots
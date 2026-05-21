import re
import json
from pathlib import Path
from typing import List, Dict, Any

# 使用相对路径导入分组引擎
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from engine.ruzu import group_full

# 获取 engine 目录路径（使用相对路径）
ENGINE_DIR = Path(__file__).parent.parent.parent.parent / "engine"

# 加载 JSON 规则表
with open(ENGINE_DIR / "adrg_rules.json", "r", encoding="utf-8") as f:
    DRG_DATA = json.load(f)

with open(ENGINE_DIR / "drg_table.json", "r", encoding="utf-8") as f:
    DRG_TABLE = json.load(f)

with open(ENGINE_DIR / "mcc_table.json", "r", encoding="utf-8") as f:
    MCC_TABLE = json.load(f)

with open(ENGINE_DIR / "cc_table.json", "r", encoding="utf-8") as f:
    CC_TABLE = json.load(f)

with open(ENGINE_DIR / "exclusion_table.json", "r", encoding="utf-8") as f:
    EXCLUSION_TABLE = json.load(f)


def build_code_to_table_map(table_data: dict) -> dict:
    result = {}
    for table_name, entries in table_data.items():
        for entry in entries:
            code = entry.get("code")
            if code:
                result[code] = table_name
    return result


def build_exclusion_map(exclusion_data: dict) -> dict:
    result = {}
    for table_name, entries in exclusion_data.items():
        codes = [entry.get("code") for entry in entries if entry.get("code")]
        result[table_name] = codes
    return result


MCC_CODE_TO_TABLE = build_code_to_table_map(MCC_TABLE)
CC_CODE_TO_TABLE = build_code_to_table_map(CC_TABLE)
EXCLUSION_MAP = build_exclusion_map(EXCLUSION_TABLE)


def parse_raw_text(text: str) -> dict:
    result = {
        "main_diag": "",
        "other_diags": [],
        "main_proc": "",
        "other_procs": [],
        "age_days": 0
    }

    main_match = re.search(r'主诊断[：:]\s*(\S+)', text)
    if main_match:
        result["main_diag"] = main_match.group(1).strip()

    other_match = re.search(r'其他诊断[：:]\s*(.+?)(?=\n\n|\n[^\n]+[：:]|\Z)', text, re.DOTALL)
    if other_match:
        diags_str = other_match.group(1)
        diags = re.split(r'[，,、\s\n]+', diags_str)
        result["other_diags"] = [d.strip() for d in diags if d.strip()]

    proc_match = re.search(r'主要手术[：:]\s*(\S*)', text)
    if proc_match and proc_match.group(1):
        result["main_proc"] = proc_match.group(1).strip()

    other_proc_match = re.search(r'其他手术[：:]\s*(.+?)(?=\n\n|\n[^\n]+[：:]|\Z)', text, re.DOTALL)
    if other_proc_match:
        procs_str = other_proc_match.group(1)
        procs = re.split(r'[，,、\s\n]+', procs_str)
        result["other_procs"] = [p.strip() for p in procs if p.strip()]

    age_match = re.search(r'年龄[：:]\s*(\d+)', text)
    if age_match:
        age_years = int(age_match.group(1))
        result["age_days"] = age_years * 365

    return result


class DRGService:
    def group_from_text(self, raw_text: str) -> Dict[str, Any]:
        parsed = parse_raw_text(raw_text)

        if not parsed["main_diag"]:
            raise ValueError("未找到主诊断编码，请确保文本中包含：主诊断：编码")

        if parsed["age_days"] == 0:
            raise ValueError("未找到年龄，请确保文本中包含：年龄：数字")

        result = group_full(
            main_diag=parsed["main_diag"],
            other_diags=parsed["other_diags"],
            main_proc=parsed["main_proc"],
            other_procs=parsed["other_procs"],
            age_days=parsed["age_days"],
            drg_data=DRG_DATA,
            drg_table=DRG_TABLE,
            mcc_code_to_table=MCC_CODE_TO_TABLE,
            cc_code_to_table=CC_CODE_TO_TABLE,
            exclusion_table=EXCLUSION_MAP
        )

        return result

    def group_from_structured(
            self,
            main_diag: str,
            other_diags: List[str],
            main_proc: str,
            other_procs: List[str],
            age_days: int
    ) -> Dict[str, Any]:
        result = group_full(
            main_diag=main_diag,
            other_diags=other_diags,
            main_proc=main_proc,
            other_procs=other_procs,
            age_days=age_days,
            drg_data=DRG_DATA,
            drg_table=DRG_TABLE,
            mcc_code_to_table=MCC_CODE_TO_TABLE,
            cc_code_to_table=CC_CODE_TO_TABLE,
            exclusion_table=EXCLUSION_MAP
        )
        return result


drg_service = DRGService()
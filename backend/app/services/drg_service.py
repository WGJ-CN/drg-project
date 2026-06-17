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


class DRGService:
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
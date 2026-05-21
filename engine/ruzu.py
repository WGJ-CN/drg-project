import json
import re
from typing import List, Dict, Any, Optional, Tuple

# ==================== 辅助函数 ====================

def extract_codes(items: Any) -> List[str]:
    if not isinstance(items, list):
        return []
    return [item["code"] for item in items if isinstance(item, dict) and "code" in item]

def get_all_diag_lists(entry: Dict[str, Any]) -> Dict[str, List[str]]:
    """提取所有诊断条件字段（用于 MDC 粗筛）"""
    diag_fields = [
        "包含以下主要诊断",
        "包含以下诊断",
        "包含以下主要诊断或其他诊断",
        "包含以下其他诊断",
        "或包含以下其他诊断",
        "主要诊断", "主要诊断1", "主要诊断2",
        "其他诊断", "其他诊断1", "其他诊断2"
    ]
    result = {}
    for field in diag_fields:
        if field in entry:
            codes = extract_codes(entry[field])
            if codes:
                result[field] = codes
    return result

def get_primary_proc_lists(entry: Dict[str, Any]) -> Dict[str, List[str]]:
    """提取要求‘主要手术操作’的条件字段"""
    fields = ["包含以下主要手术或操作", "主要手术或操作"] + \
             [f"主要手术或操作{i}" for i in range(1, 6)]
    result = {}
    for field in fields:
        if field in entry:
            codes = extract_codes(entry[field])
            if codes:
                result[field] = codes
    return result

def get_any_proc_lists(entry: Dict[str, Any]) -> Dict[str, List[str]]:
    """提取要求‘所有手术操作’的条件字段（不含 and_group）"""
    fields = [f"手术或操作{i}" for i in range(1, 6)]
    result = {}
    for field in fields:
        if field in entry:
            codes = extract_codes(entry[field])
            if codes:
                result[field] = codes
    return result

def get_and_groups(entry: Dict[str, Any]) -> List[List[str]]:
    """提取‘同时包含以下手术或操作’中的 and_group"""
    field_val = entry.get("同时包含以下手术或操作")
    if not isinstance(field_val, list):
        return []
    and_groups = []
    for group in field_val:
        if isinstance(group, dict) and "and_group" in group:
            codes = extract_codes(group["and_group"])
            if codes:
                and_groups.append(codes)
    return and_groups

def match_all_and_groups(all_procs: List[str], and_groups: List[List[str]]) -> bool:
    if not and_groups:
        return True
    proc_set = set(all_procs)
    for group_codes in and_groups:
        if not proc_set.intersection(group_codes):
            return False
    return True

def get_all_proc_codes(entry: dict) -> set:
    """提取一个条目中所有手术/操作编码（用于跨ADRG引用）"""
    codes = set()
    for key in ["包含以下主要手术或操作", "主要手术或操作", "手术或操作",
                "主要手术或操作1", "手术或操作1", "手术或操作2", "手术或操作3"]:
        if key in entry:
            codes.update(extract_codes(entry[key]))
    for group in get_and_groups(entry):
        codes.update(group)
    return codes

# ==================== 简单 ADRG 条件检查（与关系） ====================

def check_simple_adrg_match(
    entry: Dict[str, Any],
    main_diag: str,
    other_diags: List[str],
    main_proc: str,
    other_procs: List[str]
) -> bool:
    all_diags = [main_diag] + other_diags
    all_diags_set = set(all_diags)
    other_diags_set = set(other_diags)
    all_procs = ([main_proc] if main_proc else []) + other_procs
    all_procs_set = set(all_procs)

    # 1. 诊断条件
    if "包含以下主要诊断" in entry:
        codes = extract_codes(entry["包含以下主要诊断"])
        if codes and main_diag not in codes:
            return False
    if "主要诊断" in entry:
        codes = extract_codes(entry["主要诊断"])
        if codes and main_diag not in codes:
            return False
    for suf in ["1", "2"]:
        field = f"主要诊断{suf}"
        if field in entry:
            codes = extract_codes(entry[field])
            if codes and main_diag not in codes:
                return False

    if "包含以下诊断" in entry:
        codes = extract_codes(entry["包含以下诊断"])
        if codes and not all_diags_set.intersection(codes):
            return False
    if "包含以下主要诊断或其他诊断" in entry:
        codes = extract_codes(entry["包含以下主要诊断或其他诊断"])
        if codes and not all_diags_set.intersection(codes):
            return False

    if "包含以下其他诊断" in entry:
        codes = extract_codes(entry["包含以下其他诊断"])
        if codes and not other_diags_set.intersection(codes):
            return False
    if "其他诊断" in entry:
        codes = extract_codes(entry["其他诊断"])
        if codes and not other_diags_set.intersection(codes):
            return False
    for suf in ["1", "2"]:
        field = f"其他诊断{suf}"
        if field in entry:
            codes = extract_codes(entry[field])
            if codes and not other_diags_set.intersection(codes):
                return False
    if "或包含以下其他诊断" in entry:
        codes = extract_codes(entry["或包含以下其他诊断"])
        if codes and not other_diags_set.intersection(codes):
            return False

    # 2. 主要手术条件（仅由主要手术满足）
    primary_proc = get_primary_proc_lists(entry)
    for codes in primary_proc.values():
        if not main_proc or (codes and main_proc not in codes):
            return False

    # 3. 所有手术条件（可由任意手术满足）
    any_proc = get_any_proc_lists(entry)
    for codes in any_proc.values():
        if codes and not all_procs_set.intersection(codes):
            return False

    # 4. ‘同时包含’条件
    and_groups = get_and_groups(entry)
    if and_groups and not match_all_and_groups(all_procs, and_groups):
        return False

    return True

# ==================== 复杂 ADRG 硬编码判断 ====================

def check_complex_adrg(
    adrg: str,
    entry: dict,
    main_diag: str,
    other_diags: List[str],
    main_proc: str,
    other_procs: List[str],
    drg_data: dict
) -> bool:
    all_diags = [main_diag] + other_diags
    all_procs = ([main_proc] if main_proc else []) + other_procs
    proc_set = set(all_procs)

    # ---- AH2 有创呼吸机支持≥96小时 ----
    if adrg == "AH2":
        diag_codes = extract_codes(entry.get("其他诊断", []))
        proc1_codes = extract_codes(entry.get("手术或操作1", []))
        proc2_codes = extract_codes(entry.get("手术或操作2", []))
        cond_a = (any(d in other_diags for d in diag_codes) or
                  any(p in all_procs for p in proc1_codes))
        cond_b = any(p in all_procs for p in proc2_codes)
        return cond_a and cond_b

    # ---- CB2 / CB3 / WJ1 引用其他ADRG手术 ----
    if adrg == "CB2":
        return (any(p in proc_set for p in get_all_proc_codes(drg_data.get("CB4", {}))) and
                any(p in proc_set for p in get_all_proc_codes(drg_data.get("CB5", {}))))
    if adrg == "CB3":
        return (any(p in proc_set for p in get_all_proc_codes(drg_data.get("CB5", {}))) and
                any(p in proc_set for p in get_all_proc_codes(drg_data.get("CB6", {}))))
    if adrg == "WJ1":
        wb_procs = set()
        for wb in ["WB1", "WB2", "WB3"]:
            wb_procs.update(get_all_proc_codes(drg_data.get(wb, {})))
        return wb_procs.issubset(proc_set)

    # ---- WB1/WB2/WB3 烧伤组 ----
    if adrg in ("WB1", "WB2"):
        diag1 = extract_codes(entry.get("主要诊断", []))
        other1 = extract_codes(entry.get("其他诊断1", []))
        other2 = extract_codes(entry.get("其他诊断2", []))
        proc_main = extract_codes(entry.get("主要手术或操作", []))
        cond1 = (main_diag in diag1 and any(d in other_diags for d in other1) and
                 main_proc in proc_main) if (diag1 and other1 and proc_main) else False
        cond2 = (any(d in other_diags for d in other2) and main_proc in proc_main) if (other2 and proc_main) else False
        return cond1 or cond2

    if adrg == "WB3":
        diag = extract_codes(entry.get("主要诊断", [])) + extract_codes(entry.get("其他诊断", []))
        proc_main = extract_codes(entry.get("主要手术或操作", []))
        return (any(d in all_diags for d in diag) and main_proc in proc_main) if (diag and proc_main) else False

    # ---- SB1/TB1/XJ1/YC1 全部手术或操作（实际为只要有手术） ----
    if adrg in ("SB1", "TB1", "XJ1", "YC1"):
        return len(all_procs) > 0

    # ---- IB1 复杂脊柱 ----
    if adrg == "IB1":
        diag = extract_codes(entry.get("主要诊断", []))
        main_proc1 = extract_codes(entry.get("主要手术或操作1", []))
        main_proc2 = extract_codes(entry.get("主要手术或操作2", []))
        proc3 = extract_codes(entry.get("手术或操作3", []))
        proc4 = extract_codes(entry.get("手术或操作4", []))
        cond1 = (main_diag in diag and main_proc in main_proc1) if (diag and main_proc1) else False
        cond2 = (main_proc in main_proc2) if main_proc2 else False
        cond3 = (any(p in all_procs for p in proc3) and any(p in all_procs for p in proc4)) if (proc3 and proc4) else False
        return cond1 or cond2 or cond3

    # ---- JA1 乳房重建 ----
    if adrg == "JA1":
        diag = extract_codes(entry.get("主要诊断", []))
        p1 = extract_codes(entry.get("手术或操作1", []))
        p2 = extract_codes(entry.get("手术或操作2", []))
        p3 = extract_codes(entry.get("手术或操作3", []))
        p4 = extract_codes(entry.get("手术或操作4", []))
        p5 = extract_codes(entry.get("手术或操作5", []))
        cond1 = (main_diag in diag and any(p in all_procs for p in p1) and any(p in all_procs for p in p2))
        cond2 = (main_diag in diag and any(p in all_procs for p in p1) and any(p in all_procs for p in p3) and any(p in all_procs for p in p4))
        cond3 = (main_diag in diag and any(p in all_procs for p in p4) and any(p in all_procs for p in p5))
        return cond1 or cond2 or cond3

    # ---- JA2 乳房切除 ----
    if adrg == "JA2":
        diag = extract_codes(entry.get("主要诊断", []))
        main_p1 = extract_codes(entry.get("主要手术或操作1", []))
        p2 = extract_codes(entry.get("手术或操作2", []))
        p3 = extract_codes(entry.get("手术或操作3", []))
        cond1 = (main_diag in diag and main_proc in main_p1) if (diag and main_p1) else False
        cond2 = (main_diag in diag and any(p in all_procs for p in p2) and any(p in all_procs for p in p3))
        return cond1 or cond2

    # ---- NA1 女性生殖恶性肿瘤 ----
    if adrg == "NA1":
        diag = extract_codes(entry.get("主要诊断", []))
        main_p1 = extract_codes(entry.get("主要手术或操作1", []))
        p2 = extract_codes(entry.get("手术或操作2", []))
        p3 = extract_codes(entry.get("手术或操作3", []))
        cond1 = (main_diag in diag and main_proc in main_p1) if (diag and main_p1) else False
        cond2 = (main_diag in diag and any(p in all_procs for p in p2) and any(p in all_procs for p in p3))
        return cond1 or cond2

    # ---- OF1 中期引产 ----
    if adrg == "OF1":
        d1 = extract_codes(entry.get("主要诊断1", []))
        d2 = extract_codes(entry.get("主要诊断2", []))
        other = extract_codes(entry.get("其他诊断", []))
        main_proc_codes = extract_codes(entry.get("主要手术或操作", []))
        cond1 = (main_diag in d1 and main_proc in main_proc_codes) if (d1 and main_proc_codes) else False
        cond2 = (main_diag in d2 and any(d in other_diags for d in other) and
                 main_proc in main_proc_codes) if (d2 and other and main_proc_codes) else False
        return cond1 or cond2

    # ---- ZZ1 多发性重要创伤无手术 ----
    if adrg == "ZZ1":
        return len(all_procs) == 0

    # 未定义则保守返回 False
    return False

# ==================== MDC 判断 ====================

def determine_mdc(
    main_diag: str,
    other_diags: List[str],
    main_proc: str,
    other_procs: List[str],
    age_days: int,
    drg_data: Dict[str, Any]
) -> str:
    all_diags = [main_diag] + other_diags
    all_diags_set = set(all_diags)
    all_procs = ([main_proc] if main_proc else []) + other_procs
    all_procs_set = set(all_procs)

    # ---------- 1. MDCA ----------
    a_keys = [k for k in drg_data if k.startswith('A') and len(k) == 3]
    for key in a_keys:
        entry = drg_data[key]

        # ========== 修改开始 ==========
        # 之前是：if "入组条件" in entry: continue
        # 现在：无论有没有入组条件，都检查诊断和手术的擦边匹配
        # 只要诊断或手术命中列表，就认为可能属于MDCA（后续ADRG匹配会精确判断）
        diag_lists = get_all_diag_lists(entry)
        prim_proc = get_primary_proc_lists(entry)
        any_proc = get_any_proc_lists(entry)

        diag_match = any(all_diags_set.intersection(codes) for codes in diag_lists.values())
        proc_match = any(all_procs_set.intersection(codes) for codes in {**prim_proc, **any_proc}.values())

        if diag_match or proc_match:
            return "MDCA"
        # ========== 修改结束 ==========

    # ---------- 2. MDCP ----------
    if age_days < 29:
        return "MDCP"
    p_keys = [k for k in drg_data if k.startswith('P') and len(k) == 3]
    for key in p_keys:
        entry = drg_data[key]
        diag_lists = get_all_diag_lists(entry)
        if any(all_diags_set.intersection(codes) for codes in diag_lists.values()):
            return "MDCP"

    # ---------- 3. MDCY ----------
    mdcy_key = "MDCY HIV 感染疾病及相关操作 诊断表"
    if mdcy_key in drg_data:
        entry = drg_data[mdcy_key]
        diag_lists = get_all_diag_lists(entry)
        if any(all_diags_set.intersection(codes) for codes in diag_lists.values()):
            return "MDCY"

    # ---------- 4. MDCZ ----------
    mdz_keys = [
        "MDCZ头颈部创伤", "MDCZ腹部创伤", "MDCZ泌尿系统创伤", "MDCZ生殖系统创伤",
        "MDCZ躯干、脊柱创伤", "MDCZ上肢创伤", "MDCZ下肢创伤", "MDCZ骨盆创伤","MDCZ胸部创伤"
    ]
    hit_parts = set()
    for key in mdz_keys:
        if key not in drg_data:
            continue
        entry = drg_data[key]
        diag_lists = get_all_diag_lists(entry)
        if any(all_diags_set.intersection(codes) for codes in diag_lists.values()):
            hit_parts.add(key)
    if len(hit_parts) >= 2:
        return "MDCZ"

    # ---------- 5. 常规 MDC ----------
    mdc_main_keys = [k for k in drg_data if "主诊表" in k and not k.startswith("MDCY")]
    for key in mdc_main_keys:
        entry = drg_data[key]
        main_diag_list = entry.get("包含以下主要诊断", [])
        codes = extract_codes(main_diag_list)
        if main_diag in codes:
            return key.split()[0]

    return "UNKNOWN"
# ==================== ADRG 匹配（整合简单组与复杂组） ====================

def get_mdc_prefix(mdc_code: str) -> str:
    if mdc_code == "UNKNOWN" or len(mdc_code) < 4:
        return ""
    return mdc_code[3]

def get_adrg_priority(adrg_code: str) -> int:
    if len(adrg_code) < 2:
        return 4
    second = adrg_code[1].upper()
    if 'A' <= second <= 'J':
        return 1
    elif 'K' <= second <= 'Q':
        return 2
    elif 'R' <= second <= 'Z':
        return 3
    return 4

def match_adrg(
    mdc_code: str,
    main_diag: str,
    other_diags: List[str],
    main_proc: str,
    other_procs: List[str],
    drg_data: Dict[str, Any]
) -> Tuple[Optional[str], Optional[str]]:
    """返回 (ADRG编码, ADRG名称) 或 (None, None)"""
    prefix = get_mdc_prefix(mdc_code)
    if not prefix:
        return None, None

    adrg_keys = [k for k in drg_data if k.startswith(prefix) and len(k) == 3]
    adrg_keys.sort(key=get_adrg_priority)

    for key in adrg_keys:
        entry = drg_data[key]
        name = entry.get("name", key)

        if "入组条件" in entry:
            # 复杂 ADRG：硬编码判断
            if check_complex_adrg(key, entry, main_diag, other_diags, main_proc, other_procs, drg_data):
                return key, name
        else:
            # 简单 ADRG：条件全部满足
            if check_simple_adrg_match(entry, main_diag, other_diags, main_proc, other_procs):
                return key, name
    return None, None

# ==================== 并发症等级判断 ====================

def determine_complication_level(
    main_diag: str,
    other_diags: List[str],
    mcc_code_to_table: Dict[str, str],
    cc_code_to_table: Dict[str, str],
    exclusion_table: Dict[str, List[str]]
) -> str:
    # MCC
    for diag in other_diags:
        if diag in mcc_code_to_table:
            tbl = mcc_code_to_table[diag]
            if tbl == "无排除表":
                return "MCC"
            if tbl in exclusion_table and main_diag not in exclusion_table[tbl]:
                return "MCC"
            if tbl not in exclusion_table:
                return "MCC"
    # CC
    for diag in other_diags:
        if diag in cc_code_to_table:
            tbl = cc_code_to_table[diag]
            if tbl == "无排除表":
                return "CC"
            if tbl in exclusion_table and main_diag not in exclusion_table[tbl]:
                return "CC"
            if tbl not in exclusion_table:
                return "CC"
    return "NONE"

# ==================== DRG 选择 ====================

def select_drg(adrg: str, complication_level: str, drg_table: Dict[str, List[Dict[str, str]]]) -> Optional[str]:
    if adrg not in drg_table:
        return None
    candidates = drg_table[adrg]
    if len(candidates) == 1 and '，' not in candidates[0]["name"]:
        return candidates[0]["code"]

    target = {"MCC": "伴严重", "CC": "伴一般", "NONE": "不伴"}[complication_level]
    for item in candidates:
        if target in item["name"]:
            return item["code"]
    if complication_level in ("MCC", "CC"):
        for item in candidates:
            if "不伴" in item["name"]:
                return item["code"]
    return candidates[0]["code"] if candidates else None

# ==================== 完整分组入口 ====================

def group_full(
    main_diag: str,
    other_diags: List[str],
    main_proc: str,
    other_procs: List[str],
    age_days: int,
    drg_data: Dict[str, Any],
    drg_table: Dict[str, List[Dict[str, str]]],
    mcc_code_to_table: Dict[str, str],
    cc_code_to_table: Dict[str, str],
    exclusion_table: Dict[str, List[str]]
) -> Dict[str, Any]:
    result = {
        "MDC": None,
        "ADRG": None,
        "ADRG_NAME": None,
        "DRG": None,
        "DRG_NAME": None,
        "COMPLICATION": "NONE",
        "STATUS": "UNKNOWN"
    }

    mdc = determine_mdc(main_diag, other_diags, main_proc, other_procs, age_days, drg_data)
    result["MDC"] = mdc
    if mdc == "UNKNOWN":
        result["STATUS"] = "MDC_NOT_FOUND"
        return result

    adrg, adrg_name = match_adrg(mdc, main_diag, other_diags, main_proc, other_procs, drg_data)
    if adrg:
        result["ADRG"] = adrg
        result["ADRG_NAME"] = adrg_name
        result["STATUS"] = "ADRG_MATCHED"
    else:
        result["STATUS"] = "ADRG_NOT_FOUND"
        return result

    complication = determine_complication_level(
        main_diag, other_diags, mcc_code_to_table, cc_code_to_table, exclusion_table
    )
    result["COMPLICATION"] = complication

    drg = select_drg(adrg, complication, drg_table)
    if drg:
        result["DRG"] = drg
        for item in drg_table[adrg]:
            if item["code"] == drg:
                result["DRG_NAME"] = item["name"]
                break
        result["STATUS"] = "SUCCESS"
    else:
        if adrg in drg_table and drg_table[adrg]:
            result["DRG"] = drg_table[adrg][0]["code"]
            result["DRG_NAME"] = drg_table[adrg][0]["name"]
            result["STATUS"] = "DRG_FALLBACK"
        else:
            result["STATUS"] = "DRG_NOT_FOUND"

    return result

# ==================== 测试用例 ====================
if __name__ == "__main__":
    # 加载数据（路径请按实际修改）
    drg_data = json.load(open("adrg_rules.json", "r", encoding="utf-8"))
    drg_table = json.load(open("drg_table.json", "r", encoding="utf-8"))


    def load_mcc_cc_map(path):
        data = json.load(open(path, "r", encoding="utf-8"))
        mapping = {}
        for table, entries in data.items():
            for entry in entries:
                mapping[entry["code"]] = table
        return mapping


    mcc_map = load_mcc_cc_map("mcc_table.json")
    cc_map = load_mcc_cc_map("cc_table.json")
    exclusion = json.load(open("exclusion_table.json", "r", encoding="utf-8"))
    exclusion_clean = {k: [e["code"] for e in v] for k, v in exclusion.items()}

    # ---- 测试1：AH2 有创呼吸机支持≥96小时 ----
    # 场景：其他诊断有气管造口状态，手术操作包含呼吸机治疗≥96小时
    res_ah2 = group_full(
        main_diag="J12.800",  # 主诊断可为任意（如病毒性肺炎）
        other_diags=["Z93.000"],  # 气管造口状态
        main_proc="96.7201",  # 呼吸机治疗≥96小时 (主要手术)
        other_procs=[],  # 也可再加一个气管切开，但不是必须
        age_days=50 * 365,
        drg_data=drg_data,
        drg_table=drg_table,
        mcc_code_to_table=mcc_map,
        cc_code_to_table=cc_map,
        exclusion_table=exclusion_clean
    )
    print("测试 AH2 (有创呼吸机支持≥96小时)")
    print(f"  MDC: {res_ah2['MDC']}, ADRG: {res_ah2['ADRG']}, DRG: {res_ah2['DRG']}")
    print(f"  状态: {res_ah2['STATUS']}")
    expected_ah2 = ("MDCA", "AH2")
    ok_ah2 = (res_ah2['MDC'] == "MDCA" and res_ah2['ADRG'] == "AH2")
    print(f"  结果: {'✓ 通过' if ok_ah2 else '✗ 未通过，请检查'}\n")

    # ---- 测试2：ZZ1 多发性重要创伤无手术 ----
    # 需先满足 MDCZ（至少两个创伤子章节命中），且无任何手术操作
    # 使用您提供的编码：S01.800x011（头颈部）和 S21.100x002（躯干/脊柱）
    res_zz1 = group_full(
        main_diag="S01.800x011",  # 开放性脑损伤（头颈部）
        other_diags=["S21.100x002"],  # 胸部开放性损伤（躯干）
        main_proc="",  # 无手术
        other_procs=[],
        age_days=35 * 365,
        drg_data=drg_data,
        drg_table=drg_table,
        mcc_code_to_table=mcc_map,
        cc_code_to_table=cc_map,
        exclusion_table=exclusion_clean
    )
    print("测试 ZZ1 (多发性重要创伤无手术)")
    print(f"  MDC: {res_zz1['MDC']}, ADRG: {res_zz1['ADRG']}, DRG: {res_zz1['DRG']}")
    print(f"  状态: {res_zz1['STATUS']}")
    expected_zz1 = ("MDCZ", "ZZ1")
    ok_zz1 = (res_zz1['MDC'] == "MDCZ" and res_zz1['ADRG'] == "ZZ1")
    print(f"  结果: {'✓ 通过' if ok_zz1 else '✗ 未通过，可能创伤诊断未命中两个子章节，请检查MDCZ子章节的编码表'}")
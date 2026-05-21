import pdfplumber
import re
import json

# ========== ADRG 列表（完整） ==========
ADRG_LIST = [
    "AA1", "AA2", "AB1", "AC1", "AD1", "AE1", "AF1", "AG1", "AG2", "AG3",
    "AH1", "AH2", "BB1", "BB2", "BB3", "BB4", "BB5", "BC1", "BD1", "BD2",
    "BE1", "BE2", "BJ1", "BL1", "BM1", "BR1", "BR2", "BS1", "BT1", "BT2",
    "BT3", "BU1", "BU2", "BU3", "BV1", "BV2", "BV3", "BW1", "BW2", "BX1",
    "BX2", "BY1", "BY2", "BZ1", "CB1", "CB2", "CB3", "CB4", "CB5", "CB6",
    "CB7", "CD1", "CD2", "CD3", "CJ1", "CR1", "CS1", "CT1", "CU1", "CV1",
    "CW1", "CX1", "CZ1", "DB1", "DB2", "DC1", "DC2", "DC3", "DC4", "DD1",
    "DE1", "DE2", "DF1", "DF2", "DG1", "DG2", "DH1", "DH2", "DH3", "DH4",
    "DJ1", "DK1", "DR1", "DS1", "DT1", "DT2", "DU1", "DV1", "DW1", "DZ1",
    "EB1", "EB2", "EC1", "EC2", "ED1", "EJ1", "EK1", "EK2", "ER1", "ER2",
    "ES1", "ES2", "ES3", "ET1", "ET2", "EU1", "EV1", "EW1", "EX1", "EX2",
    "EZ1", "FB1", "FB2", "FC1", "FD1", "FD2", "FE1", "FE2", "FF1", "FF2",
    "FF3", "FJ1", "FK1", "FK2", "FK3", "FK4", "FL1", "FL2", "FL3", "FL4",
    "FM1", "FM2", "FM3", "FM4", "FM5", "FN1", "FN2", "FP1", "FR1", "FR2",
    "FR3", "FR4", "FR5", "FT1", "FT2", "FT3", "FT4", "FU1", "FU2", "FV1",
    "FV2", "FV3", "FW1", "FW2", "FZ1", "GB1", "GB2", "GB3", "GC1", "GC2",
    "GC3", "GD1", "GE1", "GE2", "GF1", "GF2", "GF3", "GG1", "GG2", "GH1",
    "GJ1", "GK1", "GK2", "GK3", "GR1", "GS1", "GT1", "GU1", "GU2", "GV1",
    "GW1", "GZ1", "HB1", "HC1", "HC2", "HC3", "HJ1", "HK1", "HL1", "HL2",
    "HR1", "HS1", "HS2", "HS3", "HT1", "HT2", "HU1", "HZ1", "HZ2", "HZ3",
    "IB1", "IB2", "IB3", "IC1", "IC2", "IC3", "IC4", "ID1", "ID2", "IE1",
    "IE2", "IE3", "IE4", "IE5", "IE6", "IF1", "IG1", "IH1", "IJ1", "IR1",
    "IR2", "IS1", "IS2", "IT1", "IT2", "IT3", "IU1", "IU2", "IU3", "IV1",
    "IZ1", "IZ2", "JA1", "JA2", "JB1", "JB2", "JB3", "JC1", "JD1", "JD2",
    "JJ1", "JR1", "JR2", "JS1", "JS2", "JT1", "JU1", "JV1", "JV2", "JZ1",
    "KB1", "KC1", "KD1", "KD2", "KE1", "KJ1", "KR1", "KS1", "KT1", "KU1",
    "KV1", "KZ1", "LA1", "LA2", "LB1", "LB2", "LC1", "LD1", "LE1", "LF1",
    "LJ1", "LL1", "LR1", "LS1", "LT1", "LU1", "LV1", "LW1", "LX1", "LZ1",
    "MA1", "MB1", "MC1", "MD1", "MJ1", "MR1", "MS1", "MZ1", "NA1", "NA2",
    "NB1", "NC1", "ND1", "NE1", "NF1", "NG1", "NJ1", "NR1", "NS1", "NZ1",
    "OB1", "OC1", "OC2", "OD1", "OD2", "OE1", "OF1", "OF2", "OJ1", "OR1",
    "OS1", "OS2", "OT1", "OZ1", "PB1", "PC1", "PD1", "PJ1", "PK1", "PR1",
    "PS1", "PS2", "PS3", "PS4", "PU1", "PV1", "QB1", "QJ1", "QR1", "QR2",
    "QS1", "QS2", "QS3", "QS4", "QS5", "QT1", "RA1", "RA2", "RA3", "RA4",
    "RK1", "RK2", "RL1", "RL2", "RM1", "RN1", "RN2", "RP1", "RR1", "RS1",
    "RS2", "RT1", "RT2", "RU1", "RW1", "RW2", "SB1", "SR1", "SS1", "ST1",
    "SU1", "SV1", "SZ1", "TB1", "TR1", "TR2", "TS1", "TS2", "TT1", "TT2",
    "TU1", "TV1", "TW1", "TX1", "TY1", "UR1", "US1", "VB1", "VC1", "VJ1",
    "VR1", "VS1", "VS2", "VT1", "VZ1", "WB1", "WB2", "WB3", "WJ1", "WR1",
    "WR2", "XJ1", "XR1", "XR2", "XR3", "XS1", "XS2", "XT1", "XT2", "XT3",
    "YC1", "YR1", "YR2", "ZB1", "ZC1", "ZD1", "ZJ1", "ZZ1"
]


# ========== 辅助函数 ==========
def chinese_count(s):
    return len(re.findall(r'[\u4e00-\u9fff]', s))


def is_diagnosis_code_line(line):
    return bool(re.match(r'^([A-Z0-9\.\*x\+]*\d+[A-Z0-9\.\*x\+]*)\s+', line))


def is_adrg_line(line):
    m = re.match(r'^([A-Z]{2}\d+)\s+(.+)$', line)
    return m and m.group(1) in ADRG_LIST


def is_field_name(line):
    if not (line.endswith('：') or line.endswith(':')):
        return False
    if is_diagnosis_code_line(line):
        return False
    return True


# ========== 跨行合并 ==========
def merge_adrg_lines(lines):
    merged = []
    i = 0
    while i < len(lines):
        line = lines[i]
        adrg_match = re.match(r'^([A-Z]{2}\d+)\s+(.+)$', line)
        if adrg_match and adrg_match.group(1) in ADRG_LIST:
            adrg_code = adrg_match.group(1)
            name_part = adrg_match.group(2)
            if chinese_count(name_part) >= 10 and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if not is_field_name(next_line) and not re.match(r'^[A-Z]{2}\d+', next_line):
                    if '：' not in next_line and ':' not in next_line and '包含' not in next_line:
                        new_line = f"{adrg_code} {name_part}{next_line}"
                        merged.append(new_line)
                        i += 2
                        continue
        merged.append(line)
        i += 1
    return merged


def merge_diagnosis_lines(lines):
    merged = []
    i = 0
    while i < len(lines):
        line = lines[i]
        diag_match = re.match(r'^([A-Z0-9\.\*x\+]+)\s+(.+)$', line)
        if diag_match and i + 1 < len(lines):
            code = diag_match.group(1)
            name_part = diag_match.group(2)
            if chinese_count(name_part) >= 12:
                next_line = lines[i + 1].strip()
                next_is_diag = re.match(r'^([A-Z0-9\.\*x\+]+)\s+', next_line)
                if not next_is_diag and not is_field_name(next_line) and not re.match(r'^[A-Z]{2}\d+', next_line):
                    if '：' not in next_line and ':' not in next_line and '包含' not in next_line:
                        new_line = f"{code} {name_part}{next_line}"
                        merged.append(new_line)
                        i += 2
                        continue
        merged.append(line)
        i += 1
    return merged


# ========== 主解析函数 ==========
def parse_drg_rules(pdf_path):
    print(f"正在读取PDF: {pdf_path}")

    all_lines = []
    MAX_PAGE = 1156
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"PDF总页数: {total_pages}")
        end_page = min(MAX_PAGE, total_pages)
        for i in range(64, end_page):
            page = pdf.pages[i]
            w, h = page.width, page.height
            left = page.crop((0, 0, w * 0.5, h)).extract_text() or ""
            right = page.crop((w * 0.5, 0, w, h)).extract_text() or ""
            for line in left.split('\n'):
                line = line.strip()
                if line and not re.match(r'^四、核心疾病诊断相关分组', line):
                    all_lines.append(line)
            for line in right.split('\n'):
                line = line.strip()
                if line and not re.match(r'^四、核心疾病诊断相关分组', line):
                    all_lines.append(line)
            if (i + 1) % 50 == 0:
                print(f"已处理 {i + 1} 页...")
    print(f"提取完成，共 {len(all_lines)} 行")

    all_lines = merge_adrg_lines(all_lines)
    all_lines = merge_diagnosis_lines(all_lines)
    print(f"合并后共 {len(all_lines)} 行")

    adrg_data = {}
    current_adrg = None
    current_field = None
    current_field_values = []
    current_and_groups = []
    current_group = []
    is_in_simultaneous = False
    in_condition = False
    condition_text = ""
    in_subfield = False
    current_subfield = None
    in_mdc_diagnosis = False
    is_mdcz_mode = False

    idx = 0
    while idx < len(all_lines):
        line = all_lines[idx].strip()
        idx += 1
        if not line:
            continue

        if line == "1135":
            print("遇到终止标记 1135，停止解析")
            break

        if re.match(r'^\d+$', line) or re.match(r'^[\.\s]*\d+$', line):
            continue
        if re.match(r'^[\.]+', line) and re.search(r'\d+', line):
            continue

        # ========== 0. 优先处理 MDCZ 主行 ==========
        if 'MDCZ' in line and '多发严重创伤' in line:
            if current_adrg and current_field:
                _save_current_field(adrg_data, current_adrg, current_field, current_field_values,
                                    current_and_groups, current_group, condition_text)
            adrg_data[line] = _create_empty_adrg(line)
            current_adrg = line
            current_field = None
            current_field_values = []
            in_mdc_diagnosis = True
            is_mdcz_mode = True
            current_and_groups = []
            current_group = []
            is_in_simultaneous = False
            in_condition = False
            condition_text = ""
            continue

        # ========== 1. 处理普通 MDC 诊断表（排除 MDCZ 主行） ==========
        if re.match(r'^MDC[A-Z]', line) and not ('MDCZ' in line and '多发严重创伤' in line):
            mdc_lines = [line]
            temp_i = idx
            found = False
            for _ in range(5):  # 最多向后查找5行
                if temp_i >= len(all_lines):
                    break
                next_line = all_lines[temp_i].strip()
                if not next_line:
                    temp_i += 1
                    continue
                if next_line == '主诊表' or next_line == '诊断表':
                    mdc_lines.append(next_line)
                    idx = temp_i + 1
                    found = True
                    break
                else:
                    mdc_lines.append(next_line)
                    temp_i += 1
            if found:
                if current_adrg and current_field:
                    _save_current_field(adrg_data, current_adrg, current_field, current_field_values,
                                        current_and_groups, current_group, condition_text)
                combined = ' '.join(mdc_lines)
                adrg_data[combined] = _create_empty_adrg(combined)
                current_adrg = combined
                current_field = "包含以下主要诊断"
                current_field_values = []
                in_mdc_diagnosis = True
                is_mdcz_mode = False
                current_and_groups = []
                current_group = []
                is_in_simultaneous = False
                in_condition = False
                condition_text = ""
                continue
            else:
                # 没有找到主诊表/诊断表，跳过（如 MDCA 先期分组）
                continue

        # ========== 2. MDCZ 子章节 ==========
        if in_mdc_diagnosis and is_mdcz_mode:
            if not re.match(r'^[A-Z0-9]', line) and not re.match(r'^[A-Z]{2}\d+', line) and re.search(
                    r'[\u4e00-\u9fff]', line):
                if not is_field_name(line):
                    if current_adrg and current_field:
                        _save_current_field(adrg_data, current_adrg, current_field, current_field_values,
                                            current_and_groups, current_group, condition_text)
                    sub_key = f"MDCZ{line}"
                    adrg_data[sub_key] = _create_empty_adrg(line)
                    current_adrg = sub_key
                    current_field = None
                    current_field_values = []
                    current_and_groups = []
                    current_group = []
                    is_in_simultaneous = False
                    in_condition = False
                    condition_text = ""
                    continue
            elif re.match(r'^[A-Z]{2}\d+', line):
                if current_adrg and current_field:
                    _save_current_field(adrg_data, current_adrg, current_field, current_field_values,
                                        current_and_groups, current_group, condition_text)
                is_mdcz_mode = False
                in_mdc_diagnosis = False
                idx -= 1
                continue

        # ========== 3. ADRG 行 ==========
        if is_adrg_line(line):
            if current_adrg and current_field:
                _save_current_field(adrg_data, current_adrg, current_field, current_field_values,
                                    current_and_groups, current_group, condition_text)
            adrg_match = re.match(r'^([A-Z]{2}\d+)\s+(.+)$', line)
            adrg_code = adrg_match.group(1)
            adrg_name = adrg_match.group(2)
            adrg_data[adrg_code] = _create_empty_adrg(adrg_name)
            current_adrg = adrg_code
            current_field = None
            current_field_values = []
            current_and_groups = []
            current_group = []
            is_in_simultaneous = False
            in_condition = False
            condition_text = ""
            in_mdc_diagnosis = False
            is_mdcz_mode = False
            # 主动捕获下一行作为入组条件
            if idx < len(all_lines):
                next_line = all_lines[idx].strip()
                if next_line and not is_field_name(next_line) and not is_adrg_line(next_line) and not re.match(
                        r'^MDC[A-Z]', next_line) and not is_diagnosis_code_line(next_line):
                    current_field = "入组条件"
                    in_condition = True
                    condition_text = next_line
                    idx += 1
            continue

        # ========== 4. 字段名识别 ==========
        if is_field_name(line):
            if current_adrg and current_field:
                _save_current_field(adrg_data, current_adrg, current_field, current_field_values,
                                    current_and_groups, current_group, condition_text)
            field_name = line.rstrip('：:')
            if field_name == "同时包含以下手术或操作":
                current_field = field_name
                is_in_simultaneous = True
                in_condition = False
                current_and_groups = []
                current_group = []
            else:
                current_field = field_name
                is_in_simultaneous = False
                if "入组条件" in field_name:
                    in_condition = True
                    condition_text = ""
                else:
                    in_condition = False
            current_field_values = []
            colon_pos = line.find('：') if '：' in line else line.find(':')
            if colon_pos != -1 and colon_pos + 1 < len(line):
                after_colon = line[colon_pos + 1:].strip()
                if after_colon:
                    if in_condition:
                        condition_text = after_colon
                    else:
                        diag_match = re.match(r'^(\S+)\s+(.+)$', after_colon)
                        if diag_match:
                            current_field_values.append({"code": diag_match.group(1), "name": diag_match.group(2)})
                        else:
                            current_field_values.append(after_colon)
            continue

        # ========== 5. 同时包含模式下的“和” ==========
        if is_in_simultaneous and line == "和":
            if current_group:
                current_and_groups.append({"and_group": current_group})
                current_group = []
            continue

        # ========== 6. 数据行 ==========
        code_name_match = re.match(r'^(\S+)\s+(.+)$', line)
        if code_name_match and current_field and not in_condition:
            code = code_name_match.group(1)
            name = code_name_match.group(2)
            if re.match(r'^MDC[A-Z]', code) and not is_diagnosis_code_line(line):
                continue
            item = {"code": code, "name": name}
            if is_in_simultaneous:
                current_group.append(item)
            else:
                current_field_values.append(item)
            continue

        # ========== 7. 只有编码的行 ==========
        if current_field and not in_condition and not is_in_simultaneous:
            code_match = re.match(r'^(\S+)', line)
            if code_match:
                code = code_match.group(1)
                if re.match(r'^[A-Z0-9\.\*x]+$', code) and not re.match(r'^\d+$', code):
                    current_field_values.append({"code": code, "name": ""})
                    continue

        # ========== 8. 入组条件（备用） ==========
        if current_adrg and current_field is None and not in_condition:
            if not is_field_name(line) and not is_adrg_line(line) and not re.match(r'^MDC[A-Z]',
                                                                                   line) and not is_diagnosis_code_line(
                    line):
                current_field = "入组条件"
                in_condition = True
                condition_text = line
                continue

        if in_condition:
            if is_field_name(line) or is_adrg_line(line) or re.match(r'^MDC[A-Z]', line):
                if current_adrg and current_field:
                    _save_current_field(adrg_data, current_adrg, current_field, current_field_values,
                                        current_and_groups, current_group, condition_text)
                in_condition = False
                idx -= 1
                continue
            condition_text += " " + line
            continue

    if current_adrg and current_field:
        _save_current_field(adrg_data, current_adrg, current_field, current_field_values,
                            current_and_groups, current_group, condition_text)

    return adrg_data


def _create_empty_adrg(name):
    return {"name": name}


def _save_current_field(adrg_data, adrg_code, field_name, field_values, and_groups, current_group, condition_text):
    if adrg_code not in adrg_data:
        return
    if field_name == "同时包含以下手术或操作":
        if current_group:
            and_groups.append({"and_group": current_group})
        adrg_data[adrg_code][field_name] = and_groups if and_groups else []
    elif field_name == "入组条件":
        if condition_text:
            adrg_data[adrg_code][field_name] = condition_text.strip()
    else:
        if field_values:
            adrg_data[adrg_code][field_name] = field_values
        else:
            adrg_data[adrg_code][field_name] = []


if __name__ == "__main__":
    result = parse_drg_rules("按病组（DRG）付费分组方案（2.0版）.pdf")
    if result:
        with open("adrg_rules.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("\nJSON 已保存")
        # 检查 MDCZ 子章节
        mdcz_keys = [k for k in result.keys() if k.startswith('MDCZ') and '多发严重创伤' not in k]
        if mdcz_keys:
            print(f"\n✅ MDCZ 子章节已创建：{', '.join(mdcz_keys)}")
        else:
            print("\n❌ MDCZ 子章节未创建")
        print("\n✅ 解析完成")
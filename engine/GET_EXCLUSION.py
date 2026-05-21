import re
import json
import pdfplumber

def extract_exclusion_table(pdf_path, start_page=1508, end_page=1834, output_json="exclusion_table.json"):
    """
    提取排除表（表 6-3-xxx），按表号分组。
    处理两栏排版和诊断名称跨行。
    """
    exclusion_dict = {}
    raw_lines = []

    # 用于识别诊断编码的正则（宽松模式）
    diag_code_re = re.compile(r'^([A-Z]\d{2}\.\d{3}(?:x\d{3})?(?:\+[A-Z]\d{2}\.\d{3}\*)?)')
    table_header_re = re.compile(r'^表\s*6-3-\d{1,3}')   # 匹配表号
    page_num_re = re.compile(r'^\d{1,4}$')

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        start_idx = max(0, start_page - 1)
        end_idx = min(total_pages - 1, end_page - 1)

        print(f"开始提取排除表，页码范围: {start_page} - {end_page} (索引 {start_idx} - {end_idx})")

        for i in range(start_idx, end_idx + 1):
            page = pdf.pages[i]
            w, h = page.width, page.height

            # 处理两栏排版：左半页、右半页分别提取文本
            left_text = page.crop((0, 0, w * 0.5, h)).extract_text() or ""
            right_text = page.crop((w * 0.5, 0, w, h)).extract_text() or ""

            for text_part in [left_text, right_text]:
                lines = text_part.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line or page_num_re.match(line):
                        continue
                    raw_lines.append(line)

            if (i + 1) % 50 == 0:
                print(f"  已处理 {i + 1} 页...")

    print(f"原始行数: {len(raw_lines)}")

    # ---------- 合并跨行诊断名称 ----------
    merged_lines = []
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        match = diag_code_re.match(line)
        if match and i + 1 < len(raw_lines):
            # 如果下一行不是诊断编码、不是表号、不是页码，且不含特殊字符，则认为是名称续行
            next_line = raw_lines[i + 1]
            if (not diag_code_re.match(next_line) and
                not table_header_re.match(next_line) and
                not page_num_re.match(next_line) and
                '包含' not in next_line and
                '诊断' not in next_line and
                '手术' not in next_line and
                '表' not in next_line):   # 简单排除
                combined = f"{line}{next_line}"
                merged_lines.append(combined)
                i += 2
                continue
        merged_lines.append(line)
        i += 1

    print(f"合并后行数: {len(merged_lines)}")

    # ---------- 解析表号与诊断条目 ----------
    current_table = None
    for line in merged_lines:
        # 检查是否为表号行
        table_match = table_header_re.match(line)
        if table_match:
            table_name = table_match.group().replace(' ', '')  # 去空格，如 "表6-3-1"
            if table_name not in exclusion_dict:
                exclusion_dict[table_name] = []
            current_table = table_name
            continue

        # 尝试匹配诊断条目
        diag_match = re.match(r'^([A-Z]\d{2}\.\d{3}(?:x\d{3})?(?:\+[A-Z]\d{2}\.\d{3}\*)?)\s+(.+)$', line)
        if diag_match and current_table:
            code = diag_match.group(1)
            name = diag_match.group(2).strip()
            exclusion_dict[current_table].append({
                "code": code,
                "name": name
            })
        else:
            # 可能是标题、页码等，跳过
            pass

    # 保存
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(exclusion_dict, f, ensure_ascii=False, indent=2)

    total_entries = sum(len(v) for v in exclusion_dict.values())
    print(f"提取完成，共 {len(exclusion_dict)} 个排除表，条目总数 {total_entries}")
    return exclusion_dict

if __name__ == "__main__":
    pdf_file = "按病组（DRG）付费分组方案（2.0版）.pdf"   # 请替换为实际路径
    extract_exclusion_table(pdf_file, start_page=1508, end_page=1834)
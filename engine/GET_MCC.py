import re
import json
import pdfplumber

def extract_mcc_table(pdf_path, start_page=1208, end_page=1314, output_json="mcc_table.json"):
    """
    提取 MCC 表，按排除表号分组
    输出格式：{ "表 6-3-1": [{"code":"...", "name":"..."}], ... }
    """
    mcc_by_table = {}
    # 正则改进：匹配编码 + 名称 + 可选的“表 6-3-XXX”
    code_pattern = r'([A-Z]\d{2}\.\d{3}(?:x\d{3})?(?:\+[A-Z]\d{2}\.\d{3}\*)?)'
    line_re = re.compile(
        r'^' + code_pattern + r'\s+(.+?)(?:\s*(表\s*6-3-\d{1,3}))?\s*$'
    )
    skip_keywords = ["疾病编码", "疾病名称", "排除内容", "MCC", "合并症", "并发症"]
    page_num_re = re.compile(r'^\d{1,4}$')

    with pdfplumber.open(pdf_path) as pdf:
        start_idx = max(0, start_page - 1)
        end_idx = min(len(pdf.pages) - 1, end_page - 1)

        for i in range(start_idx, end_idx + 1):
            page = pdf.pages[i]
            text = page.extract_text()
            if not text:
                continue
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line or page_num_re.match(line):
                    continue
                # 跳过表头
                if line in skip_keywords or (len(line) < 10 and any(kw in line for kw in skip_keywords)):
                    continue

                match = line_re.match(line)
                if match:
                    code = match.group(1)
                    name = match.group(2).strip()
                    table_name = match.group(3)  # 如 "表 6-3-1"，可能为 None
                    if not table_name:
                        # 尝试在名称末尾查找“表 6-3-XXX”
                        tail = re.search(r'(表\s*6-3-\d{1,3})\s*$', name)
                        if tail:
                            table_name = tail.group(1)
                            name = name[:tail.start()].strip()
                    if table_name:
                        key = table_name.replace(' ', '')  # 去掉可能空格，统一为“表6-3-1”
                    else:
                        key = "无排除表"

                    if key not in mcc_by_table:
                        mcc_by_table[key] = []
                    mcc_by_table[key].append({
                        "code": code,
                        "name": name
                    })

    # 保存
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(mcc_by_table, f, ensure_ascii=False, indent=2)
    print(f"提取完成，共 {len(mcc_by_table)} 个排除表分组，MCC 条目总数 {sum(len(v) for v in mcc_by_table.values())}")
    return mcc_by_table

if __name__ == "__main__":
    pdf_file = "按病组（DRG）付费分组方案（2.0版）.pdf"
    extract_mcc_table(pdf_file, start_page=1208, end_page=1314)
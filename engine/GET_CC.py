import re
import json
import pdfplumber

def extract_cc_table(pdf_path, start_page=1316, end_page=1506, output_json="cc_table.json"):
    """
    提取 CC 表，按排除表号分组
    输出格式：{ "表 6-3-1": [{"code":"...", "name":"..."}], ... }
    """
    cc_by_table = {}
    code_pattern = r'([A-Z]\d{2}\.\d{3}(?:x\d{3})?(?:\+[A-Z]\d{2}\.\d{3}\*)?)'
    line_re = re.compile(
        r'^' + code_pattern + r'\s+(.+?)(?:\s*(表\s*6-3-\d{1,3}))?\s*$'
    )
    skip_keywords = ["疾病编码", "疾病名称", "排除内容", "CC", "合并症", "并发症"]
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
                    table_name = match.group(3)
                    if not table_name:
                        tail = re.search(r'(表\s*6-3-\d{1,3})\s*$', name)
                        if tail:
                            table_name = tail.group(1)
                            name = name[:tail.start()].strip()
                    if table_name:
                        key = table_name.replace(' ', '')
                    else:
                        key = "无排除表"

                    if key not in cc_by_table:
                        cc_by_table[key] = []
                    cc_by_table[key].append({
                        "code": code,
                        "name": name
                    })

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(cc_by_table, f, ensure_ascii=False, indent=2)
    print(f"提取完成，共 {len(cc_by_table)} 个排除表分组，CC 条目总数 {sum(len(v) for v in cc_by_table.values())}")
    return cc_by_table

if __name__ == "__main__":
    pdf_file = "按病组（DRG）付费分组方案（2.0版）.pdf"
    extract_cc_table(pdf_file, start_page=1316, end_page=1506)
import re
import json
import pdfplumber

def extract_drg_table(pdf_path, start_page=49, end_page=64, output_json="drg_table.json"):
    adrg_dict = {}
    current_adrg = None
    pending_drg_code = None   # 用于处理极少数名称跨行情况

    # 预编译正则：匹配 ADRG编码、DRG编码、名称
    line_pattern = re.compile(r'^([A-Z]{2}\d{1,2})\s+([A-Z]{2}\d{2,3})(?:\s+(.*))?$')
    page_num_pattern = re.compile(r'^\d{1,3}$')
    skip_keywords = ["ADRG", "编码", "DRG", "名称", "疾病诊断相关分组", "DRGs"]

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
                if not line:
                    continue
                # 跳过纯数字页码
                if page_num_pattern.match(line):
                    continue
                # 跳过表头行
                if any(kw in line for kw in skip_keywords):
                    continue

                # 尝试匹配 ADRG + DRG + 名称
                match = line_pattern.match(line)
                if match:
                    adrg_code = match.group(1)
                    drg_code = match.group(2)
                    drg_name = match.group(3) if match.group(3) else ""

                    # 如果 ADRG 发生变化，更新当前 ADRG，并确保键存在
                    if current_adrg != adrg_code:
                        current_adrg = adrg_code
                        if current_adrg not in adrg_dict:
                            adrg_dict[current_adrg] = []

                    # 如果有名称，直接添加
                    if drg_name:
                        adrg_dict[current_adrg].append({
                            "code": drg_code,
                            "name": drg_name
                        })
                        pending_drg_code = None
                    else:
                        # 名称空缺，可能下一行是名称（处理跨页或跨行特殊情况）
                        pending_drg_code = drg_code
                    continue

                # 如果上面没匹配，且存在待处理的 DRG 编码，本行视为名称
                if pending_drg_code and current_adrg:
                    adrg_dict[current_adrg].append({
                        "code": pending_drg_code,
                        "name": line
                    })
                    pending_drg_code = None

    # 保存
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(adrg_dict, f, ensure_ascii=False, indent=2)
    print(f"提取完成，共 {len(adrg_dict)} 个 ADRG，输出至 {output_json}")
    return adrg_dict

if __name__ == "__main__":
    pdf_file = "按病组（DRG）付费分组方案（2.0版）.pdf"  # 请替换为实际路径
    extract_drg_table(pdf_file, start_page=49, end_page=64)
import pdfplumber
import re
import json


# ========== 辅助函数 ==========
def chinese_count(s):
    """统计字符串中的中文字符数"""
    return len(re.findall(r'[一-鿿]', s))


def is_code_line(line):
    """判断是否以医学编码开头（ICD-10 诊断编码 或 ICD-9-CM-3 手术编码）"""
    # ICD-10: 字母开头 + 数字 + . + ... (如 B95.000, Z98.800x3)
    # ICD-9-CM-3: 数字开头 + . + ... (如 00.0101, 00.0900x001)
    return bool(re.match(r'^([A-Z0-9]\d+\.[A-Za-z0-9xX*+]+)\s+', line))


# ========== 跨行合并 ==========
def merge_wrapped_lines(lines):
    """
    合并跨行显示的名称。
    规则：如果当前行有编码且名称中文字数 >= 8，
    且下一行不是新编码行、不是章节标题，则合并。
    """
    merged = []
    i = 0
    while i < len(lines):
        line = lines[i]
        code_match = re.match(r'^([A-Z0-9]\d+\.[A-Za-z0-9xX*+]+)\s+(.+)$', line)
        if code_match and i + 1 < len(lines):
            code = code_match.group(1)
            name_part = code_match.group(2)
            if chinese_count(name_part) >= 8:
                next_line = lines[i + 1].strip()
                # 下一行不是新编码、不是章节标题、不含"不作为"
                if (not is_code_line(next_line)
                        and not re.match(r'^[一二三四五]、', next_line)
                        and not re.match(r'^\d+、', next_line)
                        and '不作为' not in next_line):
                    new_line = f"{code} {name_part}{next_line}"
                    merged.append(new_line)
                    i += 2
                    continue
        merged.append(line)
        i += 1
    return merged


# ========== 主提取函数 ==========
def extract_non_grouping_list(pdf_path, start_page=1158, end_page=1207,
                              output_json="non_grouping_list.json"):
    """
    从 PDF 中提取"不作为分组规则的疾病诊断和手术操作列表"。
    第 1158-1207 页，双栏布局。
    """
    print(f"正在读取PDF: {pdf_path}")
    print(f"提取范围: 第 {start_page} - {end_page} 页")

    # 需要跳过的关键词（章节标题、表头等）
    skip_keywords = [
        "不作为分组规则的疾病诊断和手术操作列表",
        "不作为分组规则的疾病诊断列表",
        "不作为分组规则的手术操作列表",
        "疾病编码",
        "疾病名称",
        "手术编码",
        "手术名称",
    ]
    page_num_re = re.compile(r'^\d{1,4}$')
    # 编码+名称的正则
    code_re = re.compile(r'^([A-Z0-9]\d+\.[A-Za-z0-9xX*+]+)\s+(.+)$')

    all_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        start_idx = max(0, start_page - 1)
        end_idx = min(end_page, total_pages)

        print(f"PDF总页数: {total_pages}，实际提取到第 {end_idx} 页")

        for i in range(start_idx, end_idx):
            page = pdf.pages[i]
            w, h = page.width, page.height

            # 双栏裁剪
            left = page.crop((0, 0, w * 0.5, h)).extract_text() or ""
            right = page.crop((w * 0.5, 0, w, h)).extract_text() or ""

            for line in left.split('\n'):
                line = line.strip()
                if line and not page_num_re.match(line):
                    all_lines.append(line)
            for line in right.split('\n'):
                line = line.strip()
                if line and not page_num_re.match(line):
                    all_lines.append(line)

            if (i + 1) % 10 == 0:
                print(f"已处理 {i + 1} 页...")

    print(f"原始提取完成，共 {len(all_lines)} 行")

    # 跨行合并
    all_lines = merge_wrapped_lines(all_lines)
    print(f"合并后共 {len(all_lines)} 行")

    # 解析编码-名称对
    results = []
    skipped = 0
    for line in all_lines:
        # 跳过章节标题
        if any(kw in line for kw in skip_keywords):
            skipped += 1
            continue

        match = code_re.match(line)
        if match:
            code = match.group(1)
            name = match.group(2).strip()
            if name:
                results.append({"code": code, "name": name})
        else:
            # 可能是无法识别的行，打印出来方便调试
            if line and not re.match(r'^[一二三四五六七八九十]、', line):
                print(f"  [跳过] {line[:80]}...")

    print(f"\n解析完成：")
    print(f"  有效记录: {len(results)} 条")
    print(f"  跳过行: {skipped} 条")

    # 保存
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"已保存到 {output_json}")

    # 打印前几条件为预览
    print("\n--- 前 5 条预览 ---")
    for item in results[:5]:
        print(f"  {item['code']} : {item['name']}")
    print("--- 最后 5 条预览 ---")
    for item in results[-5:]:
        print(f"  {item['code']} : {item['name']}")

    return results


if __name__ == "__main__":
    pdf_file = "按病组（DRG）付费分组方案（2.0版）.pdf"
    result = extract_non_grouping_list(pdf_file)
    print("\n✅ 提取完成")

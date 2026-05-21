import json
import os

def collect_code_name_pairs(data, pairs_set=None):
    """递归提取所有包含 code/name 的字典，返回 (code, name) 集合"""
    if pairs_set is None:
        pairs_set = set()
    if isinstance(data, dict):
        # 如果同时有 code 和 name 字段
        if "code" in data and "name" in data:
            pairs_set.add((data["code"], data["name"]))
        for value in data.values():
            collect_code_name_pairs(value, pairs_set)
    elif isinstance(data, list):
        for item in data:
            collect_code_name_pairs(item, pairs_set)
    return pairs_set

def main():
    files = [
        "adrg_rules.json",
        "mcc_table.json",
        "cc_table.json",
        "exclusion_table.json"
    ]
    pairs = set()
    for file in files:
        if not os.path.exists(file):
            print(f"警告：文件 {file} 不存在，跳过")
            continue
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        collect_code_name_pairs(data, pairs)
        print(f"已处理 {file}，当前总配对数量：{len(pairs)}")

    # 构建映射
    code2name = {}
    name2code = {}
    for code, name in pairs:
        if not code or not name:
            continue
        code2name[code] = name
        name2code.setdefault(name, []).append(code)

    # 保存
    with open("code2name.json", "w", encoding="utf-8") as f:
        json.dump(code2name, f, ensure_ascii=False, indent=2)
    with open("name2code.json", "w", encoding="utf-8") as f:
        json.dump(name2code, f, ensure_ascii=False, indent=2)

    print(f"生成 code2name.json：{len(code2name)} 条")
    print(f"生成 name2code.json：{len(name2code)} 条")

if __name__ == "__main__":
    main()
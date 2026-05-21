import json
with open("adrg_rules.json", "r", encoding="utf-8") as f:
    data = json.load(f)
# 打印 SB1 条目，保持缩进
print(json.dumps(data.get("SB1", {}), ensure_ascii=False, indent=2))
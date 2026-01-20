import argparse
import json
import os
import csv
from datetime import datetime

# 配置文件名
DATA_FILE = "expenses.json"

# --- 数据持久化逻辑 ---

def load_expenses():
    """从 JSON 文件加载数据"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_expenses(expenses):
    """保存数据到 JSON 文件"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=4, ensure_ascii=False)

# --- 核心业务功能 ---

def add_expense(description, amount, category="通用"):
    """添加支出"""
    if amount <= 0:
        print("? 错误：金额必须大于 0。")
        return
    
    expenses = load_expenses()
    new_id = expenses[-1]['id'] + 1 if expenses else 1
    
    new_expense = {
        "id": new_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": description,
        "amount": amount,
        "category": category
    }
    
    expenses.append(new_expense)
    save_expenses(expenses)
    print(f"? 支出添加成功 (ID: {new_id})")

def update_expense(expense_id, description=None, amount=None):
    """更新现有支出"""
    expenses = load_expenses()
    for exp in expenses:
        if exp["id"] == expense_id:
            if description: exp["description"] = description
            if amount: 
                if amount <= 0:
                    print("? 错误：金额必须大于 0。")
                    return
                exp["amount"] = amount
            save_expenses(expenses)
            print(f"? ID {expense_id} 更新成功")
            return
    print(f"? 错误：未找到 ID 为 {expense_id} 的记录。")

def delete_expense(expense_id):
    """删除支出"""
    expenses = load_expenses()
    updated = [e for e in expenses if e['id'] != expense_id]
    
    if len(expenses) == len(updated):
        print(f"? 错误：未找到 ID 为 {expense_id} 的记录。")
    else:
        save_expenses(updated)
        print(f"?? 支出 ID {expense_id} 已删除。")

def list_expenses():
    """查看所有支出"""
    expenses = load_expenses()
    if not expenses:
        print("? 暂无支出记录。")
        return
    
    print(f"{'ID':<5} {'日期':<12} {'分类':<10} {'描述':<15} {'金额':<10}")
    print("-" * 55)
    for exp in expenses:
        category = exp.get("category", "无")
        print(f"{exp['id']:<5} {exp['date']:<12} {category:<10} {exp['description']:<15} ${exp['amount']:<10}")

def show_summary(month=None):
    """查看支出汇总"""
    expenses = load_expenses()
    now = datetime.now()
    
    if month:
        if not 1 <= month <= 12:
            print("? 错误：月份必须在 1-12 之间。")
            return
        filtered = [e for e in expenses if datetime.strptime(e['date'], "%Y-%m-%d").month == month 
                    and datetime.strptime(e['date'], "%Y-%m-%d").year == now.year]
        total = sum(e['amount'] for e in filtered)
        print(f"? {month} 月总支出: ${total}")
    else:
        total = sum(e['amount'] for e in expenses)
        print(f"? 累计总支出: ${total}")

def export_to_csv(filename="expenses.csv"):
    """导出为 CSV 文件"""
    expenses = load_expenses()
    if not expenses:
        print("? 没有记录可供导出。")
        return
    
    keys = ["id", "date", "description", "amount", "category"]
    try:
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            # 只写入 keys 中定义的字段，防止旧数据缺少字段导致报错
            for exp in expenses:
                row = {k: exp.get(k, "") for k in keys}
                writer.writerow(row)
        print(f"? 数据已成功导出至：{filename}")
    except Exception as e:
        print(f"? 导出失败：{e}")

# --- 命令行界面 ---

def main():
    parser = argparse.ArgumentParser(description="Expense Tracker - 个人记账命令行工具")
    subparsers = parser.add_subparsers(dest="command")

    # add
    add_parser = subparsers.add_parser("add", help="添加支出记录")
    add_parser.add_argument("--description", required=True, help="描述")
    add_parser.add_argument("--amount", type=float, required=True, help="金额")
    add_parser.add_argument("--category", default="通用", help="分类")

    # list
    subparsers.add_parser("list", help="查看所有记录")

    # update
    upd_parser = subparsers.add_parser("update", help="更新记录")
    upd_parser.add_argument("--id", type=int, required=True, help="记录 ID")
    upd_parser.add_argument("--description", help="新描述")
    upd_parser.add_argument("--amount", type=float, help="新金额")

    # delete
    del_parser = subparsers.add_parser("delete", help="删除记录")
    del_parser.add_argument("--id", type=int, required=True, help="记录 ID")

    # summary
    sum_parser = subparsers.add_parser("summary", help="总结支出")
    sum_parser.add_argument("--month", type=int, help="特定月份 (1-12)")

    # export
    exp_parser = subparsers.add_parser("export", help="导出 CSV")
    exp_parser.add_argument("--filename", default="expenses.csv", help="输出文件名")

    args = parser.parse_args()

    if args.command == "add":
        add_expense(args.description, args.amount, args.category)
    elif args.command == "list":
        list_expenses()
    elif args.command == "update":
        update_expense(args.id, args.description, args.amount)
    elif args.command == "delete":
        delete_expense(args.id)
    elif args.command == "summary":
        show_summary(args.month)
    elif args.command == "export":
        export_to_csv(args.filename)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
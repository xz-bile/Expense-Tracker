# -*- coding: utf-8 -*-
import argparse
import json
import os
import csv
import hashlib
import getpass
from datetime import datetime

# 配置文件
EXPENSE_FILE = "expenses.json"
USER_FILE = "users.json"

# --- 数据持久化与安全逻辑 ---

def load_json(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def hash_password(password):
    """使用 SHA-256 算法对密码进行哈希加密"""
    return hashlib.sha256(password.encode()).hexdigest()

# --- 用户管理模块 ---

def register():
    username = input("请输入新用户名: ").strip()
    users = load_json(USER_FILE)
    if username in users:
        print("❌ 错误：该用户名已被注册。")
        return
    password = getpass.getpass("请输入新密码: ")
    confirm = getpass.getpass("请再次输入密码: ")
    if password != confirm:
        print("❌ 错误：两次输入密码不一致。")
        return
    users[username] = hash_password(password)
    save_json(USER_FILE, users)
    print(f"✅ 用户 {username} 注册成功！现在可以尝试登录。")

def authenticate():
    """用户登录验证"""
    username = input("用户名: ").strip()
    password = getpass.getpass("密码: ")
    users = load_json(USER_FILE)
    if username in users and users[username] == hash_password(password):
        return username
    print("❌ 错误：用户名或密码不正确。")
    return None

# --- 费用管理模块 (支持多用户隔离) ---

def add_expense(user, description, amount, category="通用"):
    if amount <= 0:
        print("❌ 错误：金额必须大于 0。")
        return
    
    all_data = load_json(EXPENSE_FILE)
    user_expenses = all_data.get(user, [])
    
    # 获取该用户下的新 ID
    new_id = user_expenses[-1]['id'] + 1 if user_expenses else 1
    
    new_expense = {
        "id": new_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": description,
        "amount": amount,
        "category": category
    }
    
    user_expenses.append(new_expense)
    all_data[user] = user_expenses
    save_json(EXPENSE_FILE, all_data)
    print(f"✅ {user} 的支出已添加 (ID: {new_id})")

def list_expenses(user):
    all_data = load_json(EXPENSE_FILE)
    user_expenses = all_data.get(user, [])
    
    if not user_expenses:
        print(f"📭 用户 {user} 暂无支出记录。")
        return
    
    print(f"\n--- {user} 的支出清单 ---")
    print(f"{'ID':<5} {'日期':<12} {'分类':<10} {'描述':<15} {'金额':<10}")
    print("-" * 55)
    for exp in user_expenses:
        print(f"{exp['id']:<5} {exp['date']:<12} {exp.get('category',''):<10} {exp['description']:<15} ${exp['amount']:<10}")

def show_summary(user, month=None):
    all_data = load_json(EXPENSE_FILE)
    user_expenses = all_data.get(user, [])
    now = datetime.now()
    
    if month:
        filtered = [e for e in user_expenses if datetime.strptime(e['date'], "%Y-%m-%d").month == month 
                    and datetime.strptime(e['date'], "%Y-%m-%d").year == now.year]
        total = sum(e['amount'] for e in filtered)
        print(f"📅 用户 {user} - {month}月总支出: ${total}")
    else:
        total = sum(e['amount'] for e in user_expenses)
        print(f"💰 用户 {user} - 累计总支出: ${total}")

def export_csv(user, filename="my_expenses.csv"):
    all_data = load_json(EXPENSE_FILE)
    user_expenses = all_data.get(user, [])
    if not user_expenses:
        print("❌ 没有记录可供导出。")
        return
    
    keys = ["id", "date", "description", "amount", "category"]
    try:
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for exp in user_expenses:
                writer.writerow({k: exp.get(k, "") for k in keys})
        print(f"🚀 {user} 的数据已导出至：{filename}")
    except Exception as e:
        print(f"❌ 导出失败：{e}")

# --- 主程序逻辑 ---

def main():
    parser = argparse.ArgumentParser(description="Expense Tracker Pro - 支持用户登录的记账工具")
    subparsers = parser.add_subparsers(dest="command")

    # 注册命令
    subparsers.add_parser("register", help="注册新账号")

    # 业务命令 (都需要登录)
    subparsers.add_parser("add", help="添加支出").add_argument("--description", required=True); \
    subparsers.add_parser("add").add_argument("--amount", type=float, required=True); \
    subparsers.add_parser("add").add_argument("--category", default="通用")

    subparsers.add_parser("list", help="查看记录")
    
    sum_parser = subparsers.add_parser("summary", help="汇总查询")
    sum_parser.add_argument("--month", type=int, help="月份 (1-12)")

    exp_parser = subparsers.add_parser("export", help="导出数据")
    exp_parser.add_argument("--filename", default="export.csv")

    args = parser.parse_args()

    if args.command == "register":
        register()
    elif args.command in ["add", "list", "summary", "export"]:
        # 执行业务操作前强制登录
        user = authenticate()
        if user:
            if args.command == "add":
                add_expense(user, args.description, args.amount, args.category)
            elif args.command == "list":
                list_expenses(user)
            elif args.command == "summary":
                show_summary(user, args.month)
            elif args.command == "export":
                export_csv(user, args.filename)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
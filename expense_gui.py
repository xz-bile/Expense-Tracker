# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import hashlib
from datetime import datetime

# 文件配置
EXPENSE_FILE = "expenses.json"
USER_FILE = "users.json"

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("个人财务管理系统 (GUI版)")
        self.root.geometry("700x550")
        self.current_user = None
        
        # 风格配置
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=25)
        
        self.show_login_screen()

    # --- 数据层逻辑 ---
    def load_json(self, filename):
        if not os.path.exists(filename): return {}
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}

    def save_json(self, filename, data):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def hash_pw(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # --- 界面工具 ---
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- 1. 登录界面 ---
    def show_login_screen(self):
        self.clear_screen()
        frame = tk.Frame(self.root)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="用户登录", font=("微软雅黑", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        tk.Label(frame, text="用户名:").grid(row=1, column=0, sticky="e", pady=5)
        self.u_login = tk.Entry(frame)
        self.u_login.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="密  码:").grid(row=2, column=0, sticky="e", pady=5)
        self.p_login = tk.Entry(frame, show="*")
        self.p_login.grid(row=2, column=1, pady=5)

        tk.Button(frame, text="登 录", bg="#4CAF50", fg="white", width=20, 
                  command=self.handle_login).grid(row=3, column=0, columnspan=2, pady=15)
        tk.Button(frame, text="没有账号？点击注册", fg="blue", bd=0, 
                  command=self.show_register_screen).grid(row=4, column=0, columnspan=2)

    def handle_login(self):
        username = self.u_login.get().strip()
        password = self.p_login.get()
        users = self.load_json(USER_FILE)
        
        if username in users and users[username] == self.hash_pw(password):
            self.current_user = username
            self.show_main_screen()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")

    # --- 2. 注册界面 (补全功能) ---
    def show_register_screen(self):
        self.clear_screen()
        frame = tk.Frame(self.root)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="新用户注册", font=("微软雅黑", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        tk.Label(frame, text="用户名:").grid(row=1, column=0, sticky="e", pady=5)
        self.u_reg = tk.Entry(frame)
        self.u_reg.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="新密码:").grid(row=2, column=0, sticky="e", pady=5)
        self.p_reg = tk.Entry(frame, show="*")
        self.p_reg.grid(row=2, column=1, pady=5)

        tk.Label(frame, text="确认密码:").grid(row=3, column=0, sticky="e", pady=5)
        self.p_confirm = tk.Entry(frame, show="*")
        self.p_confirm.grid(row=3, column=1, pady=5)

        tk.Button(frame, text="立即注册", bg="#2196F3", fg="white", width=20, 
                  command=self.handle_register).grid(row=4, column=0, columnspan=2, pady=15)
        tk.Button(frame, text="已有账号？返回登录", fg="gray", bd=0, 
                  command=self.show_login_screen).grid(row=5, column=0, columnspan=2)

    def handle_register(self):
        username = self.u_reg.get().strip()
        password = self.p_reg.get()
        confirm = self.p_confirm.get()

        if not username or not password:
            messagebox.showwarning("验证失败", "用户名和密码不能为空")
            return
        if password != confirm:
            messagebox.showwarning("验证失败", "两次输入的密码不一致")
            return

        users = self.load_json(USER_FILE)
        if username in users:
            messagebox.showerror("注册失败", "该用户名已存在")
            return

        users[username] = self.hash_pw(password)
        self.save_json(USER_FILE, users)
        messagebox.showinfo("成功", "注册成功！请返回登录")
        self.show_login_screen()

    # --- 3. 主功能界面 ---
    def show_main_screen(self):
        self.clear_screen()
        
        # 顶部栏
        top_bar = tk.Frame(self.root, bg="#f0f0f0")
        top_bar.pack(fill="x", padx=10, pady=5)
        tk.Label(top_bar, text=f"👤 当前用户: {self.current_user}", bg="#f0f0f0").pack(side="left")
        tk.Button(top_bar, text="退出登录", command=self.show_login_screen, bg="#f44336", fg="white").pack(side="right")

        # 输入区域
        input_frame = tk.LabelFrame(self.root, text="新增支出记录", padx=10, pady=10)
        input_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(input_frame, text="描述:").grid(row=0, column=0)
        self.desc_ent = tk.Entry(input_frame)
        self.desc_ent.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="金额:").grid(row=0, column=2)
        self.amt_ent = tk.Entry(input_frame)
        self.amt_ent.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="分类:").grid(row=0, column=4)
        self.cat_cb = ttk.Combobox(input_frame, values=["餐饮", "交通", "购物", "娱乐", "其他"], width=10)
        self.cat_cb.current(0)
        self.cat_cb.grid(row=0, column=5, padx=5)

        tk.Button(input_frame, text="添加支出", bg="#4CAF50", fg="white", command=self.add_expense).grid(row=0, column=6, padx=10)

        # 表格区域
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("id", "date", "cat", "desc", "amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="日期")
        self.tree.heading("cat", text="分类")
        self.tree.heading("desc", text="描述")
        self.tree.heading("amount", text="金额 ($)")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("amount", width=80, anchor="e")

        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.refresh_table()

    def add_expense(self):
        desc = self.desc_ent.get().strip()
        cat = self.cat_cb.get()
        try:
            amt = float(self.amt_ent.get())
        except ValueError:
            messagebox.showwarning("错误", "请输入有效的数字金额")
            return

        if not desc:
            messagebox.showwarning("错误", "描述不能为空")
            return

        data = self.load_json(EXPENSE_FILE)
        user_data = data.get(self.current_user, [])
        
        new_id = user_data[-1]['id'] + 1 if user_data else 1
        user_data.append({
            "id": new_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "category": cat,
            "description": desc,
            "amount": amt
        })
        
        data[self.current_user] = user_data
        self.save_json(EXPENSE_FILE, data)
        
        self.desc_ent.delete(0, tk.END)
        self.amt_ent.delete(0, tk.END)
        self.refresh_table()
        messagebox.showinfo("成功", "支出添加成功！")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        data = self.load_json(EXPENSE_FILE)
        user_data = data.get(self.current_user, [])
        for exp in user_data:
            self.tree.insert("", "end", values=(exp["id"], exp["date"], exp["category"], exp["description"], f"{exp['amount']:.2f}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()
"""
導流站更新器 — 合併版 GUI
支援栗子小姐姐 + 讚讚讚小姐姐，一個視窗切換
"""
import json
import logging
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import subprocess
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("seo_hub.update_gui")

# === 兩個帳號設定 ===
ACCOUNTS = {
    "讚讚讚小姐姐": {
        "articles_file": str(Path(__file__).parent.parent / "articles.txt"),
        "seo_hub_dir": str(Path(__file__).parent),
        "generate_script": str(Path(__file__).parent / "generate_site.py"),
        "site_url": "https://liz7788.github.io/zan-articles/",
        "vocus_url": "https://vocus.cc/salon/msliz7788",
        "color": "#e8734a",
        "output_dir": None,  # 讚讚讚目前沒有 output/ 結構
    },
    "栗子小姐姐": {
        "articles_file": str(Path("C:/Users/NEWE8/Desktop/vocus-writer/seo-hub/articles.txt")),
        "seo_hub_dir": str(Path("C:/Users/NEWE8/Desktop/vocus-writer/seo-hub")),
        "generate_script": str(Path("C:/Users/NEWE8/Desktop/vocus-writer/seo-hub/generate_site.py")),
        "site_url": "https://liz7788.github.io/chestnut-articles/",
        "vocus_url": "https://vocus.cc/salon/liz0821",
        "color": "#4a90d9",
        "output_dir": str(Path("C:/Users/NEWE8/Desktop/vocus-writer/output")),
    },
}


def get_account():
    """取得目前選擇的帳號設定"""
    name = account_var.get()
    return ACCOUNTS[name]


def load_existing():
    """讀取現有文章數量"""
    acc = get_account()
    count = 0
    if os.path.exists(acc["articles_file"]):
        with open(acc["articles_file"], "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and " | " in line:
                    count += 1
    return count


def parse_input(text):
    """解析輸入，支援兩種格式"""
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    articles = []

    if any(" | " in l for l in lines):
        for l in lines:
            if " | " in l:
                title, url = l.rsplit(" | ", 1)
                if url.startswith("http"):
                    articles.append((title.strip(), url.strip()))
    else:
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("http"):
                i += 1
                continue
            title = line
            i += 1
            while i < len(lines) and not lines[i].startswith("http"):
                i += 1
            if i < len(lines) and lines[i].startswith("http"):
                url = lines[i]
                if "vocus.cc" in url:
                    articles.append((title, url))
                i += 1

    return articles


def on_account_change(*args):
    """切換帳號時更新顯示"""
    acc = get_account()
    count = load_existing()
    count_label.config(text=f"目前已有 {count} 篇文章")
    btn_update.config(bg=acc["color"])
    root.title(f"導流站更新器 — {account_var.get()}")


def do_update():
    """新增文章並更新網站"""
    acc = get_account()
    text = input_box.get("1.0", tk.END).strip()

    if not text:
        run_generate_and_push("沒有新增文章，重新生成並更新現有頁面")
        return

    new_articles = parse_input(text)

    if not new_articles:
        messagebox.showwarning("格式錯誤",
            "沒有找到有效的文章。\n\n支援兩種格式：\n"
            "1. 從 Word 直接貼上（標題和網址交替）\n"
            "2. 標題 | 網址（一行一篇）")
        return

    # 讀取現有 URL 去重
    existing_urls = set()
    if os.path.exists(acc["articles_file"]):
        with open(acc["articles_file"], "r", encoding="utf-8") as f:
            for line in f:
                if " | " in line and "vocus.cc" in line:
                    _, url = line.rsplit(" | ", 1)
                    existing_urls.add(url.strip())

    added = [(t, u) for t, u in new_articles if u not in existing_urls]

    if not added:
        messagebox.showinfo("沒有新文章", "這些文章都已經在清單裡了")
        return

    # 寫入 articles.txt
    with open(acc["articles_file"], "a", encoding="utf-8") as f:
        f.write(f"\n# === 新增 ===\n")
        for title, url in added:
            f.write(f"{title} | {url}\n")

    run_generate_and_push(f"新增了 {len(added)} 篇文章")


def run_generate_and_push(msg):
    """生成頁面並推上 GitHub"""
    acc = get_account()
    status_label.config(text="正在更新...")
    root.update()

    try:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", acc["generate_script"]],
            capture_output=True, text=True, cwd=acc["seo_hub_dir"]
        )
        if result.returncode != 0:
            messagebox.showerror("生成失敗", result.stderr)
            status_label.config(text="生成失敗")
            return

        git_result = subprocess.run(
            ["git", "add", ".", "&&", "git", "commit", "-m", "Update articles", "&&", "git", "push"],
            capture_output=True, text=True, cwd=acc["seo_hub_dir"], shell=True
        )
        if git_result.returncode != 0:
            messagebox.showwarning("Git 推送失敗",
                f"網站已生成但 git push 失敗：\n{git_result.stderr}\n\n請手動推送。")

        total = load_existing()
        status_label.config(text=f"{msg}。目前共 {total} 篇。")
        input_box.delete("1.0", tk.END)

        messagebox.showinfo("更新完成",
            f"{msg}\n\n目前共 {total} 篇文章\n\n"
            f"網站會在 1-2 分鐘後更新：\n{acc['site_url']}")

    except Exception as e:
        messagebox.showerror("錯誤", str(e))
        status_label.config(text="發生錯誤")


# === GUI ===
root = tk.Tk()
root.title("導流站更新器")
root.geometry("620x560")
root.resizable(False, False)

# 帳號選擇
top_frame = tk.Frame(root)
top_frame.pack(pady=(10, 5), padx=15, fill="x")

tk.Label(top_frame, text="選擇帳號：", font=("Microsoft JhengHei", 11)).pack(side="left")

account_var = tk.StringVar(value="讚讚讚小姐姐")
account_menu = ttk.Combobox(top_frame, textvariable=account_var,
                            values=list(ACCOUNTS.keys()),
                            state="readonly", width=20,
                            font=("Microsoft JhengHei", 11))
account_menu.pack(side="left", padx=10)
account_var.trace_add("write", on_account_change)

# 標題
tk.Label(root, text="導流站更新器", font=("Microsoft JhengHei", 14, "bold")).pack(pady=(5, 3))

count_label = tk.Label(root, text="", font=("Microsoft JhengHei", 10), fg="#666")
count_label.pack()

# 說明
frame_info = tk.Frame(root)
frame_info.pack(padx=15, pady=(10, 5), fill="x")
tk.Label(frame_info, text="貼上文章標題和方格子網址（從 Word 直接貼上就好）：",
         font=("Microsoft JhengHei", 10), anchor="w").pack(fill="x")
tk.Label(frame_info, text="格式：標題一行、網址一行，交替排列。留空直接按更新 = 只重新生成頁面",
         font=("Microsoft JhengHei", 9), fg="#999", anchor="w").pack(fill="x")

# 輸入框
input_box = scrolledtext.ScrolledText(root, width=70, height=16, font=("Consolas", 10))
input_box.pack(padx=15, pady=5)

# 按鈕
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

btn_update = tk.Button(btn_frame, text="更新導流站", command=do_update,
                       font=("Microsoft JhengHei", 11, "bold"), bg="#e8734a", fg="white",
                       padx=20, pady=5)
btn_update.pack()

# 狀態列
status_label = tk.Label(root, text="", font=("Microsoft JhengHei", 9), fg="#666")
status_label.pack(pady=(5, 10))

# 初始化顯示
on_account_change()

root.mainloop()

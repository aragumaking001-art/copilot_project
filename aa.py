import tkinter as tk
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- ブラウザ起動 ---
options = webdriver.ChromeOptions()
options.binary_location = "/usr/bin/chromium"
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://gemini.google.com")

wait = WebDriverWait(driver, 30)

def request_gemini(question):
    search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor")))
    search_box.send_keys(question)
    search_box.send_keys("\n")
    answers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.markdown")))
    texts = [a.text.strip() for a in answers if a.text.strip()]
    return texts[-1] if texts else "回答が取得できませんでした"

# --- 角丸矩形描画関数 ---
def create_rounded_rect(canvas, x1, y1, x2, y2, r=20, **kwargs):
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1,
        x2, y1+r,
        x2, y2-r,
        x2, y2,
        x2-r, y2,
        x1+r, y2,
        x1, y2,
        x1, y2-r,
        x1, y1+r,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

# --- Tkinter UI ---
def show_answer():
    question = entry.get()
    answer = request_gemini(question)
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, answer)

root = tk.Tk()
root.title("Gemini Cyber UI")

bg_color = "#1e1e1e"
accent_color = "#00ffff"
root.configure(bg=bg_color)

canvas = tk.Canvas(root, width=800, height=500, bg=bg_color, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# アイコン（さらに左端に配置）
try:
    icon = tk.PhotoImage(file="yuruchara.png").subsample(4, 4)
    icon_label = tk.Label(root, image=icon, bg=bg_color)
    icon_label.image = icon
    icon_label.place(x=0, y=100)   # ← 左端に寄せる
except Exception:
    tk.Label(root, text="🤖", bg=bg_color, fg=accent_color,
             font=("Consolas", 20)).place(x=0, y=100)

# 回答欄の角丸枠（さらに右にシフト）
create_rounded_rect(canvas, 220, 20, 780, 300, r=25,
                    fill="#2b2b2b", outline=accent_color, width=3)
text_box = tk.Text(root, wrap="word", width=60, height=15,
                   bg="#2b2b2b", fg="lime", insertbackground=accent_color,
                   font=("Consolas", 12), relief="flat")
text_box.place(x=240, y=40, width=520, height=240)

# 入力欄の角丸枠
create_rounded_rect(canvas, 120, 340, 520, 380, r=15,
                    fill="#2b2b2b", outline=accent_color, width=3)
entry = tk.Entry(root, bg="#2b2b2b", fg=accent_color,
                 insertbackground="lime", font=("Consolas", 12),
                 relief="flat")
entry.place(x=140, y=345, width=360, height=30)

# ボタンの角丸枠
create_rounded_rect(canvas, 540, 340, 780, 380, r=15,
                    fill=accent_color, outline=accent_color, width=2)
btn = tk.Button(root, text="Geminiに送信", command=show_answer,
                bg=accent_color, fg="black", font=("Consolas", 12),
                relief="flat")
btn.place(x=550, y=345, width=220, height=30)

def on_enter(e): btn.configure(bg="lime", fg="black")
def on_leave(e): btn.configure(bg=accent_color, fg="black")
btn.bind("<Enter>", on_enter)
btn.bind("<Leave>", on_leave)

# 半角/全角キーで IME 切り替え
def remap_hankaku_zenkaku(event):
    subprocess.run(["/usr/bin/fcitx5-remote", "-t"])
    state = subprocess.run(["/usr/bin/fcitx5-remote"], capture_output=True, text=True)
    print("fcitx5 state:", state.stdout.strip())
    return "break"

entry.bind("<Control_L>", remap_hankaku_zenkaku)

root.mainloop()
driver.quit()

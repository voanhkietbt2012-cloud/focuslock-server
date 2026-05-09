import customtkinter as ctk
import subprocess
from winotify import Notification
from datetime import datetime, timedelta
import math
import sqlite3
import hashlib
import os
import sys
import winreg
import shutil
import sys
import os
import firebase_admin
from firebase_admin import credentials, db
from firebase_admin import db
import uuid
import smtplib
from email.mime.text import MIMEText

def create_unlock_request(parent_email):
    request_id = str(uuid.uuid4())

    data = {
        "status": "pending"
    }

    db.reference(f"unlock_requests/{request_id}").set(data)

    approve_link = f"http://YOUR_IP:5000/approve?id={request_id}"
    deny_link = f"http://YOUR_IP:5000/deny?id={request_id}"

    send_parent_email(parent_email, approve_link, deny_link)

    return request_id

def send_parent_email(parent_email, approve_link, deny_link):

    html = f"""
    <h2>Yêu cầu mở khóa FocusLock</h2>

    <a href="{approve_link}">
        <button style="padding:15px;background:green;color:white;">
            YES - Cho phép mở
        </button>
    </a>

    <br><br>

    <a href="{deny_link}">
        <button style="padding:15px;background:red;color:white;">
            NO - Không cho phép
        </button>
    </a>
    """

    msg = MIMEText(html, "html")
    msg["Subject"] = "FocusLock Unlock Request"
    msg["From"] = GMAIL_SENDER
    msg["To"] = parent_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(GMAIL_SENDER, GMAIL_PASSWORD)

    server.send_message(msg)
    server.quit()

def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, hoạt động cả trong môi trường dev và PyInstaller """
    try:
        # Khi đóng gói .exe, PyInstaller tạo thư mục tạm và lưu đường dẫn vào sys._MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

if getattr(sys, 'frozen', False):
    # chạy exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # chạy python
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LANG_PATH = os.path.join(BASE_DIR, "lang.txt")

def save_lang(lang):
    try:
        with open(LANG_PATH, "w") as f:
            f.write(lang)
    except:
        pass

def load_lang():
    try:
        with open(LANG_PATH, "r") as f:
            return f.read().strip()
    except:
        save_lang("vi")   # tạo file luôn
        return "vi"

LANG = load_lang()
TEXT = {
    "notify_remaining": {
        "vi": "Còn {m} phút trước khi khóa",
        "en": "{m} minutes left before lock"
    },

    
    "title_confirm": {"vi": "Xác nhận", "en": "Confirm"},
    "remaining": {"vi": "CÒN LẠI", "en": "REMAINING"},
    "unlock": {"vi": "MỞ", "en": "UNLOCK"},
    "lock": {"vi": "KHÓA", "en": "LOCK"},
    "logout": {"vi": "ĐĂNG XUẤT", "en": "LOGOUT"},
    "fullscreen": {"vi": "TOÀN MÀN HÌNH", "en": "FULLSCREEN"},
    # ===== AUTH =====
    "login": {"vi": "Đăng nhập", "en": "Login"},
    "register": {"vi": "Đăng ký", "en": "Register"},
    "email": {"vi": "Email", "en": "Email"},
    "password": {"vi": "Mật khẩu", "en": "Password"},
    "confirm_password": {"vi": "Nhập lại mật khẩu", "en": "Confirm password"},
    "forgot_password": {"vi": "Quên mật khẩu?", "en": "Forgot password?"},
    "no_account": {"vi": "Chưa có tài khoản? Đăng ký", "en": "Don't have an account? Register"},
    "back_login": {"vi": "<- Quay lại đăng nhập", "en": "<- Back to login"},

    # ===== VALIDATION =====
    "fill_all": {"vi": "Vui lòng nhập đầy đủ!", "en": "Please fill all fields!"},
    "invalid_email": {"vi": "Email không hợp lệ!", "en": "Invalid email!"},
    "wrong_password": {"vi": "Sai mật khẩu", "en": "Wrong password"},
    "password_short": {"vi": "Mật khẩu tối thiểu 6 ký tự!", "en": "Password must be at least 6 characters!"},
    "password_not_match": {"vi": "Mật khẩu không khớp!", "en": "Passwords do not match!"},

    # ===== BUTTON =====
    "start": {"vi": "▶ BẮT ĐẦU", "en": "▶ START"},
    "running": {"vi": "▶ ĐANG CHẠY...", "en": "▶ RUNNING..."},
    "send_email": {"vi": "GỬI EMAIL ĐỔI MẬT KHẨU", "en": "SEND RESET EMAIL"},

    # ===== TIMER =====
    "timer": {"vi": "HẸN GIỜ", "en": "TIMER"},
    "lock_time": {"vi": "THỜI GIAN KHÓA", "en": "LOCK TIME"},
    "hour": {"vi": "GIỜ", "en": "HOUR"},
    "minute": {"vi": "PHÚT", "en": "MIN"},
    "second": {"vi": "GIÂY", "en": "SEC"},

    # ===== STATUS =====
    "idle": {"vi": "SẴN SÀNG", "en": "IDLE"},
    "running_status": {"vi": "ĐANG CHẠY", "en": "RUNNING"},
    "locked": {"vi": "ĐÃ KHÓA", "en": "LOCKED"},
    "error_input": {"vi": "LỖI NHẬP", "en": "INPUT ERROR"},

    # ===== LOCK =====
    "locked_screen": {"vi": "MÀN HÌNH ĐÃ KHÓA", "en": "SCREEN LOCKED"},
    "session_end": {"vi": "Phiên làm việc đã kết thúc", "en": "Session finished"},
    "unlock_after": {"vi": "Mở khóa sau:", "en": "Unlock after:"},
    "restore_lock": {"vi": "Máy tính bật lại khi đang khóa", "en": "PC restarted while locked"},

    # ===== EDIT LOCK =====
    "unlock_edit": {"vi": "ĐÃ MỞ KHÓA CHỈNH SỬA", "en": "EDIT UNLOCKED"},
    "lock_edit": {"vi": "ĐÃ KHÓA CHỈNH SỬA", "en": "EDIT LOCKED"},

    # ===== DAILY =====
    "daily_mode": {"vi": "CHẾ ĐỘ HÀNG NGÀY", "en": "DAILY MODE"},

    # ===== NOTE =====
    "auto_lock_note": {"vi": "Màn hình sẽ khóa khi hết giờ", "en": "Screen will lock when time ends"},

    # ===== FORGOT PASSWORD =====
    "enter_email_reset": {"vi": "Nhập email để nhận link đổi mật khẩu", "en": "Enter email to receive reset link"},
    "sending": {"vi": "Đang gửi email...", "en": "Sending email..."},
    "email_sent": {"vi": "Nếu email tồn tại, link đã được gửi!", "en": "If email exists, reset link sent!"},
    "email_fail": {"vi": "Không thể gửi email! Thử lại sau.", "en": "Failed to send email! Try again."},

    # ===== REGISTER =====
    "register_success": {"vi": "Đăng ký thành công!", "en": "Register success!"},

    # ===== CONFIRM =====
    "enter_password": {"vi": "Nhập mật khẩu để xác nhận:", "en": "Enter password to confirm:"},
    "logout_confirm": {"vi": "Nhập mật khẩu để đăng xuất:", "en": "Enter password to logout:"}
}
def t(key):
    return TEXT.get(key, {}).get(LANG, key)

# ===== STARTUP =====
def add_to_startup_once():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )

        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__)

        winreg.SetValueEx(
            key,
            "FocusLock",
            0,
            winreg.REG_SZ,
            f'"{exe_path}"'
        )

        winreg.CloseKey(key)

    except Exception as e:
        print("Startup error:", e)
def set_taskmgr_enabled(enabled):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
            0, winreg.KEY_SET_VALUE
        )

        if enabled:
            try:
                winreg.DeleteValue(key, "DisableTaskMgr")
            except:
                pass
        else:
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)

        winreg.CloseKey(key)
    except Exception as e:
        print(e)

# ===== DAILY MODE =====
DAILY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_mode.txt")

def save_daily_mode(state):
    try:
        with open(DAILY_PATH, "w") as f:
            f.write("1" if state else "0")
    except:
        pass

def load_daily_mode():
    try:
        with open(DAILY_PATH, "r") as f:
            return f.read().strip() == "1"
    except:
        return False



ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

GMAIL_SENDER   = "your_email@gmail.com"
GMAIL_PASSWORD = "your_app_password"

ACCENT       = "#FCD34D"
ACCENT_DIM   = "#A16207"
BG_DARK      = "#1E1E2A"
BG_CARD      = "#2A2A3A"
BG_CARD2     = "#38384E"
BG_HOVER     = "#48486A"
TEXT_PRIMARY = "#FFFFFF"
TEXT_MUTED   = "#AAAACC"
DANGER       = "#FC8181"
SUCCESS      = "#6EE7B7"

API_KEY = "AIzaSyD38pK96ZFiiJiihJ_m9LNV1T2ehsHtgRY"
cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://focuslock-61fc0-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
BASE_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
LOCKSTATE_PATH = os.path.join(BASE_DIR, "lockstate.txt")
SESSION_PATH = os.path.join(BASE_DIR, "session.txt")
DB_PATH = os.path.join(BASE_DIR, "focuslock.db")
def save_timer_state(deadline, total):
    path = get_timerstate_path()
    with open(path, "w") as f:
        f.write(f"{deadline.isoformat()}|{total}")

def load_timer_state():
    path = get_timerstate_path()
    try:
        with open(path, "r") as f:
            deadline_str, total = f.read().split("|")
            deadline = datetime.fromisoformat(deadline_str)

        if deadline > datetime.now():
            return deadline, float(total)
        else:
            os.remove(path)
            return None, None
    except:
        return None, None

def clear_timer_state():
    path = get_timerstate_path()
    try:
        os.remove(path)
    except:
        pass
def get_timerstate_path():
    email, token = load_session()
    if not email:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "timerstate.txt")
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"timerstate_{email}.txt"
    )

def save_timer(username, h, m, s):
    path = f"timer_{username}.txt"
    with open(path, "w") as f:
        f.write(f"{h},{m},{s}")

def load_timer(username):
    path = f"timer_{username}.txt"
    try:
        with open(path, "r") as f:
            h, m, s = map(int, f.read().split(","))
            return h, m, s
    except:
        return 0, 0, 0

def save_lock_time(username, h, m, s):
    path = f"locktime_{username}.txt"
    with open(path, "w") as f:
        f.write(f"{h},{m},{s}")

def load_lock_time(username):
    path = f"locktime_{username}.txt"
    try:
        with open(path, "r") as f:
            h, m, s = map(int, f.read().split(","))
            return h, m, s
    except:
        return 0, 5, 0

def save_session(email, token):
    with open(SESSION_PATH, "w") as f:
        f.write(f"{email}|{token}")


def load_session():
    try:
        with open(SESSION_PATH, "r") as f:
            email, token = f.read().strip().split("|")
            return email, token
    except:
        return None, None



def clear_session():
    try:
        os.remove(SESSION_PATH)
    except:
        pass

def save_lock_state(lock_deadline):
    with open(LOCKSTATE_PATH, "w") as f:
        f.write(lock_deadline.isoformat())

def clear_lock_state():
    try:
        os.remove(LOCKSTATE_PATH)
    except:
        pass

def load_lock_state():
    try:
        with open(LOCKSTATE_PATH, "r") as f:
            deadline = datetime.fromisoformat(f.read().strip())
        if deadline > datetime.now():
            return deadline
        clear_lock_state()
        return None
    except:
        return None

# ── Database ──────────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email    TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")
    con.commit()
    con.close()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

import requests

def db_register(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        res = requests.post(url, json=payload)
        data = res.json()

        if "idToken" in data:
            return True, "OK"
        else:
            return False, data.get("error", {}).get("message", "Lỗi Firebase")

    except Exception as e:
        return False, str(e)




def db_login(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        res = requests.post(url, json=payload)
        data = res.json()

        if "idToken" in data:
            return True, data["idToken"]
        else:
            return False, data["error"]["message"]

    except Exception as e:
        return False, str(e)


def send_reset_email(email):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }

        res = requests.post(url, json=payload)
        data = res.json()

        if "email" in data:
            return True
        else:
            return False

    except:
        return False


# ═══════════════════════════════════════════════════════════
#  SCROLLABLE FRAME (thủ công — tránh bug yview của CTk)
# ═══════════════════════════════════════════════════════════
import tkinter as tk

class ScrollableFrame(ctk.CTkFrame):
    """
    CTkFrame bọc ngoài + Canvas + inner Frame bên trong.
    Luôn scroll về đầu ngay khi build xong.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)

        self._canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0,
                                 borderwidth=0)
        self._scrollbar = ctk.CTkScrollbar(self, orientation="vertical",
                                           command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self.inner = ctk.CTkFrame(self._canvas, fg_color="transparent",
                                  corner_radius=0)
        self._window_id = self._canvas.create_window((0, 0), window=self.inner,
                                                      anchor="nw")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_inner_configure(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        # scroll về đầu mỗi lần nội dung thay đổi
        self._canvas.yview_moveto(0)

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._window_id, width=event.width)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def scroll_top(self):
        self._canvas.yview_moveto(0)


# ═══════════════════════════════════════════════════════════
#  CIRCULAR TIMER
# ═══════════════════════════════════════════════════════════
class CircularTimer(ctk.CTkCanvas):
    def __init__(self, parent, size=160, **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=BG_DARK, highlightthickness=0, **kwargs)
        self.size = size; self.cx = size//2; self.cy = size//2
        self.radius = size//2 - 14
        self._draw(1.0, "--:--:--")

    def _draw(self, progress, label):
        self.delete("all")
        glow = ["#4A3C0A","#5A4C0C","#6A5C0E","#7A6C10"]
        for i in range(4, 0, -1):
            self.create_oval(self.cx-self.radius-i*3, self.cy-self.radius-i*3,
                             self.cx+self.radius+i*3, self.cy+self.radius+i*3,
                             outline=glow[4-i], width=1)
        self.create_oval(self.cx-self.radius, self.cy-self.radius,
                         self.cx+self.radius, self.cy+self.radius,
                         outline=BG_CARD2, width=8)
        extent = -360*progress
        if abs(extent) > 1:
            color = ACCENT if progress > 0.25 else DANGER
            self.create_arc(self.cx-self.radius, self.cy-self.radius,
                            self.cx+self.radius, self.cy+self.radius,
                            start=90, extent=extent, outline=color, width=8, style="arc")
            angle = math.radians(90+extent)
            dx = self.cx + self.radius*math.cos(angle)
            dy = self.cy - self.radius*math.sin(angle)
            self.create_oval(dx-5, dy-5, dx+5, dy+5, fill=color, outline="")
        inner_r = self.radius-16
        self.create_oval(self.cx-inner_r, self.cy-inner_r,
                         self.cx+inner_r, self.cy+inner_r, fill=BG_CARD, outline="")
        fs = 15 if len(label) >= 8 else 22
        self.create_text(self.cx, self.cy-8, text=label, fill=TEXT_PRIMARY,
                         font=("Courier New", fs, "bold"))
        self.create_text(self.cx, self.cy+14, text=t("remaining"), fill=TEXT_MUTED,
                         font=("Courier New", 7))

    def update_progress(self, progress, label):
        self._draw(progress, label)

# ═══════════════════════════════════════════════════════════
#  HELPER UI
# ═══════════════════════════════════════════════════════════
def make_spinbox(parent, lbl, max_val):
    col = ctk.CTkFrame(parent, fg_color="transparent")
    col.pack(side="left", padx=3)
    ctk.CTkLabel(col, text=lbl, text_color=TEXT_MUTED,
                 font=ctk.CTkFont(family="Courier New", size=8)).pack()
    up = ctk.CTkButton(col, text="▲", width=44, height=18, corner_radius=5,
                       fg_color=BG_CARD2, hover_color=BG_HOVER, text_color=ACCENT,
                       font=ctk.CTkFont(size=10))
    up.pack(pady=(1, 1))
    var = ctk.StringVar(value="00")
    box = ctk.CTkEntry(col, textvariable=var, width=44, height=36, justify="center",
                       font=ctk.CTkFont(family="Courier New", size=16, weight="bold"),
                       fg_color=BG_CARD2, border_color=BG_CARD2,
                       text_color=TEXT_PRIMARY, corner_radius=6)
    box.pack()
    col.box = box
    dn = ctk.CTkButton(col, text="▼", width=44, height=18, corner_radius=5,
                       fg_color=BG_CARD2, hover_color=BG_HOVER, text_color=ACCENT,
                       font=ctk.CTkFont(size=10))
    dn.pack(pady=(1, 0))
    col.up = up
    col.dn = dn
    def _clamp(v):
        v = max(0, min(max_val, v)); var.set(f"{v:02d}")
    def _get():
        try: return int(var.get())
        except: return 0
    up.configure(command=lambda: _clamp(_get()+1))
    dn.configure(command=lambda: _clamp(_get()-1))
    box.bind("<MouseWheel>", lambda e: _clamp(_get()+(1 if e.delta > 0 else -1)))
    col.var = var
    return col

def make_colon(parent):
    ctk.CTkLabel(parent, text=":", text_color=ACCENT,
                 font=ctk.CTkFont(family="Courier New", size=22, weight="bold")
                 ).pack(side="left", padx=1, pady=(12, 0))

def make_entry(parent, placeholder, show=None, width=320):
    return ctk.CTkEntry(parent, placeholder_text=placeholder,
                        width=width, height=42, show=show,
                        font=ctk.CTkFont(size=13),
                        fg_color=BG_CARD2, border_color=BG_CARD2,
                        text_color=TEXT_PRIMARY,
                        placeholder_text_color=TEXT_MUTED,
                        corner_radius=10)

def make_btn(parent, text, command, color=None, text_color=None, width=320):
    return ctk.CTkButton(parent, text=text, command=command,
                         width=width, height=44, corner_radius=12,
                         fg_color=color or ACCENT,
                         hover_color="#EAB308",
                         text_color=text_color or "#18181F",
                         font=ctk.CTkFont(size=13, weight="bold"))

def make_link(parent, text, command):
    lbl = ctk.CTkLabel(parent, text=text, text_color=ACCENT,
                       font=ctk.CTkFont(size=11, underline=True), cursor="hand2")
    lbl.bind("<Button-1>", lambda e: command())
    return lbl

# ═══════════════════════════════════════════════════════════
#  APP CHÍNH
# ═══════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.last_notify = -1
        set_taskmgr_enabled(True)
        self.iconbitmap(resource_path("icon.ico"))
        # FORCE reset session khi chạy exe
        

        self.lock_time_editable = False
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        add_to_startup_once()
        self.daily_mode = load_daily_mode()
        self.title("FocusLock")
        self.geometry("460x640")
        self.resizable(True, True)
        self.configure(fg_color=BG_DARK)

       

        self.running        = False
        self.locked         = False
        self.total          = 0
        self.deadline       = None
        self.is_fullscreen  = False
        self._current_frame = None

        saved_lock = load_lock_state()
        saved_timer, saved_total = load_timer_state()

        if saved_lock:
            self.lock_deadline = saved_lock
            self.after(200, self._restore_lock)

        elif saved_timer:
            self.deadline = saved_timer
            self.total = saved_total
            self.running = True
            self.after(500, self.show_main)
            self.after(800, self.tick)

        else:
            email, token = load_session()
            user = email
            if user:
                self.show_main()
            else:
                self.show_login()
        
    # ── Frame switcher dùng ScrollableFrame thủ công ──────────
    def _switch(self, frame_fn, height=640):
        if self._current_frame:
            self._current_frame.destroy()

        self.geometry(f"460x{height}")

        sf = ScrollableFrame(self)
        sf.pack(fill="both", expand=True)
        self._current_frame = sf

        # build vào sf.inner (không phải sf trực tiếp)
        frame_fn(sf.inner)

        # scroll về đầu sau khi layout xong
        self.after(50, sf.scroll_top)

    def _logo(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(pady=(16, 0))
        ctk.CTkLabel(row, text="⏳ FOCUS", text_color=ACCENT,
                     font=ctk.CTkFont(family="Courier New", size=20, weight="bold")).pack(side="left")
        ctk.CTkLabel(row, text="LOCK", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(family="Courier New", size=20, weight="bold")).pack(side="left", padx=(4, 0))

    def _msg_label(self, parent):
        lbl = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=11),
                           text_color=DANGER, wraplength=300)
        lbl.pack(pady=(4, 0))
        return lbl

    def set_lock_editable(self, state):
        self.lock_time_editable = state

        widgets = [
            self.lock_h.up, self.lock_h.dn,
            self.lock_m.up, self.lock_m.dn,
            self.lock_s.up, self.lock_s.dn
        ]

        # chỉnh nút tăng giảm
        for w in widgets:
            w.configure(state="normal" if state else "disabled")

        # chỉnh ô nhập (quan trọng)
        mode = "normal" if state else "readonly"

        self.lock_h.box.configure(state=mode)
        self.lock_m.box.configure(state=mode)
        self.lock_s.box.configure(state=mode)

        # khoá preset luôn
        for btn in getattr(self, "lock_presets", []):
            btn.configure(state="normal" if state else "disabled")

    def hide_window(self):
        self.withdraw()
    def show_register(self):
        def build(f):
            self._logo(f)

            global e_email, e_pass, e_pass2, msg

            e_email = make_entry(f, t("email"))
            e_email.pack(pady=6)

            e_pass = make_entry(f, t("password"), show="*")
            e_pass.pack(pady=6)

            e_pass2 = make_entry(f, t("confirm_password"), show="*")
            e_pass2.pack(pady=6)

            msg = self._msg_label(f)

            make_btn(f, t("register"), self.do_register).pack(pady=10)
            make_link(f, t("back_login"), self.show_login).pack()

        self._switch(build, height=420)

    def toggle_language(self):
        global LANG
        LANG = "en" if LANG == "vi" else "vi"
        save_lang(LANG)

        email, token = load_session()

        if email and token:
            self.show_main()
        else:
            self.show_login()

    # ══════════════════════════════════════════════════════
    #  ĐĂNG NHẬP
    # ═══════════════════════════════ ═══════════════════════
    def show_login(self):
        def build(f):
            lang_frame = ctk.CTkFrame(f, fg_color="transparent")
            lang_frame.pack(anchor="ne", padx=20, pady=(5, 0))

            ctk.CTkButton(
                lang_frame,
                text="EN" if LANG == "vi" else "VI",
                width=40,
                height=28,
                command=self.toggle_language
            ).pack()
            self._logo(f)

            global e_user, e_pass, msg

            e_user = make_entry(f, t("email") )
            e_user.pack(pady=6)

            e_pass = make_entry(f, t("password"), show="*")
            e_pass.pack(pady=6)

            msg = self._msg_label(f)

            make_btn(f, t("login"), self.do_login).pack(pady=10)
            make_link(f, t("forgot_password"), self.show_forgot).pack()
            make_link(f, t("no_account"), self.show_register).pack(pady=(6,0))
        
        self._switch(build, height=400)

    def do_login(self):
        email = e_user.get().strip()
        p = e_pass.get().strip()

        if not email or not p:
            msg.configure(text=t("fill_all"), text_color=DANGER)
            return

        ok, result = db_login(email, p)

        if ok:
            save_session(email, result)  # lưu token
            self.show_main()
        else:
            msg.configure(text=result, text_color=DANGER)



    # ══════════════════════════════════════════════════════
    #  ĐĂNG KÝ
    # ══════════════════════════════════════════════════════
    def do_register(self):
        em = e_email.get().strip()
        p  = e_pass.get().strip()
        p2 = e_pass2.get().strip()

        if not em or not p or not p2:
            msg.configure(text=t("fill_all"), text_color=DANGER); return

        import re

        if not re.match(r"[^@]+@[^@]+\.[^@]+", em):
            msg.configure(text=t("invalid_email"), text_color=DANGER)
            return


        if len(p) < 6:
            msg.configure(text=t("password_short"), text_color=DANGER); return

        if p != p2:
            msg.configure(text=t("password_not_match"), text_color=DANGER); return

        ok, err = db_register(em, p)

        if ok:
            msg.configure(text=t("register_success"), text_color=SUCCESS)
            self.after(1200, self.show_login)
        else:
            msg.configure(text=err, text_color=DANGER)


    # ══════════════════════════════════════════════════════
    #  QUÊN MẬT KHẨU
    # ══════════════════════════════════════════════════════
    def show_forgot(self):
        def build(f):
            self._logo(f)

            ctk.CTkLabel(f, text=t("forgot_password"), text_color=TEXT_MUTED,
                         font=ctk.CTkFont(size=12)).pack(pady=(4, 16))

            ctk.CTkLabel(f, text=t("enter_email_reset"),
                         text_color=TEXT_MUTED,
                         font=ctk.CTkFont(size=11)).pack(pady=(0, 12))

            e_email = make_entry(f, t("email"))
            e_email.pack(pady=(0, 4))

            msg = self._msg_label(f)

            def do_send():
                em = e_email.get().strip()

                if not em:
                    msg.configure(text=t("fill_all"), text_color=DANGER)
                    return

                msg.configure(text=t("email_sent"), text_color=TEXT_MUTED)
                f.update()

                ok = send_reset_email(em)

                if ok:
                    msg.configure(
                        text=t("send_email"),
                        text_color=SUCCESS
                )
                else:
                    msg.configure(
                        text=t("back_login"),
                        text_color=DANGER
                    )

            make_btn(f, t("send_email"), do_send).pack(pady=(12, 0))
            make_link(f, t("back_login"), self.show_login).pack(pady=(12, 20))

        self._switch(build, height=380)

    def emergency_unlock(self):

        parent_email = "mailphuhuynh@gmail.com"

        request_id = create_unlock_request(parent_email)

        self._set_status("Đã gửi yêu cầu phụ huynh", ACCENT)

        self.check_unlock_response(request_id) 

    def check_unlock_response(self, request_id):

        status = db.reference(
            f"unlock_requests/{request_id}/status"
        ).get()

        if status == "approved":
            self.unlock()
            return

        elif status == "denied":
            self._set_status("Phụ huynh từ chối", "red")
            return

        self.after(3000, lambda: self.check_unlock_response(request_id))  

    

    

    # ══════════════════════════════════════════════════════
    #  GIAO DIỆN CHÍNH
    # ══════════════════════════════════════════════════════
    def show_main(self):
        def build(f):
            header = ctk.CTkFrame(f, fg_color="transparent")
            header.pack(fill="x", padx=24, pady=(16, 0))
            lang_btn = ctk.CTkButton(
                header,
                text="EN" if LANG == "vi" else "VI",
                width=40,
                height=28,
                command=self.toggle_language
            )
            lang_btn.pack(side="right", padx=(6, 0))


            tf = ctk.CTkFrame(header, fg_color="transparent")
            tf.pack(side="left")
            ctk.CTkLabel(tf, text="⏳ FOCUS", text_color=ACCENT,
                         font=ctk.CTkFont(family="Courier New", size=13, weight="bold")).pack(side="left")
            ctk.CTkLabel(tf, text="LOCK", text_color=TEXT_MUTED,
                         font=ctk.CTkFont(family="Courier New", size=13, weight="bold")).pack(side="left", padx=(3, 0))

            right = ctk.CTkFrame(header, fg_color="transparent")
            right.pack(side="right")

            self.fs_btn = ctk.CTkButton(right, text="⛶", width=30, height=30,
                corner_radius=8, fg_color=BG_CARD2, hover_color=BG_HOVER,
                text_color=TEXT_MUTED, font=ctk.CTkFont(size=14),
                command=self._toggle_fullscreen)
            self.fs_btn.pack(side="right", padx=(6, 0))

            ctk.CTkButton(right, text="⏏", width=30, height=30,
                corner_radius=8, fg_color=BG_CARD2, hover_color=BG_HOVER,
                text_color=TEXT_MUTED, font=ctk.CTkFont(size=14),
                command=self._logout).pack(side="right", padx=(0, 4))

            self.status_dot = ctk.CTkLabel(right, text="●", text_color=TEXT_MUTED,
                                           font=ctk.CTkFont(size=9))
            self.status_dot.pack(side="right")

            self.status_label = ctk.CTkLabel(right, text=t("idle"),
                                             text_color=TEXT_MUTED,
                                             font=ctk.CTkFont(family="Courier New", size=9))
            self.status_label.pack(side="right", padx=(0, 4))

            ctk.CTkFrame(f, height=1, fg_color=BG_CARD2).pack(fill="x", padx=24, pady=(10, 0))

            self.circle = CircularTimer(f, size=160)
            self.circle.pack(pady=(14, 4))

            # ===== HẸN GIỜ =====
            card = ctk.CTkFrame(f, fg_color=BG_CARD, corner_radius=16)
            card.pack(fill="x", padx=28, pady=(4, 0))

            ctk.CTkLabel(card, text=t("timer"), text_color=TEXT_MUTED,
                         font=ctk.CTkFont(family="Courier New", size=9)).pack(anchor="w", padx=16, pady=(10, 2))

            sr = ctk.CTkFrame(card, fg_color="transparent")
            sr.pack(pady=(0, 6))

            self.var_h = make_spinbox(sr, t("hour"), 99)
            make_colon(sr)
            self.var_m = make_spinbox(sr, t("minute"), 59)
            make_colon(sr)
            self.var_s = make_spinbox(sr, t("second"), 59)

            pr = ctk.CTkFrame(card, fg_color="transparent")
            pr.pack(pady=(0, 10))

            for lbl, secs in [("5ph",300),("25ph",1500),("1 gio",3600),("2 gio",7200)]:
                ctk.CTkButton(pr, text=lbl, width=62, height=22,
                    corner_radius=6, fg_color=BG_CARD2, hover_color=BG_HOVER,
                    text_color=TEXT_MUTED,
                    font=ctk.CTkFont(family="Courier New", size=9),
                    command=lambda s=secs: self._set_timer_preset(s)
                ).pack(side="left", padx=(0, 5))

            # ===== KHÓA =====
            lc = ctk.CTkFrame(f, fg_color=BG_CARD, corner_radius=16)
            lc.pack(fill="x", padx=28, pady=(8, 0))

            ctk.CTkLabel(lc, text=t("lock_time"), text_color=TEXT_MUTED,
                         font=ctk.CTkFont(family="Courier New", size=9)
                         ).pack(anchor="w", padx=16, pady=(10, 2))

            ls = ctk.CTkFrame(lc, fg_color="transparent")
            ls.pack(pady=(0, 6))

            self.lock_h = make_spinbox(ls, t("hour"), 23)
            make_colon(ls)
            self.lock_m = make_spinbox(ls, t("minute"), 59)
            make_colon(ls)
            self.lock_s = make_spinbox(ls, t("second"), 59)
            self.lock_m.var.set("05")

            lpr = ctk.CTkFrame(lc, fg_color="transparent")
            lpr.pack(pady=(0, 10))

            self.lock_presets = []

            for lbl, secs in [("30s",30),("1ph",60),("3ph",180),("5ph",300),("15ph",900),("30ph",1800)]:
                btn = ctk.CTkButton(
                    lpr,
                    text=lbl,
                    width=52,
                    height=22,
                    corner_radius=6,
                    fg_color=BG_CARD2,
                    hover_color=BG_HOVER,
                    text_color=TEXT_MUTED,
                    font=ctk.CTkFont(family="Courier New", size=9),
                    command=lambda s=secs: self._set_lock_preset(s)
                )

                btn.pack(side="left", padx=(0, 5))

                self.lock_presets.append(btn)

            # ===== MỞ/KHOÁ =====
            def unlock_edit():
                if self.verify_password():
                    self.set_lock_editable(True)
                    self._set_status(t("unlock_edit"), SUCCESS)
                else:
                    self._set_status(t("wrong_password"), DANGER)

            def lock_edit():
                self.set_lock_editable(False)
                self._set_status(t("lock_edit"), TEXT_MUTED)

            btn_frame = ctk.CTkFrame(lc, fg_color="transparent")
            btn_frame.pack(pady=(0, 10))

            ctk.CTkButton(btn_frame, text="🔑 MO", width=80,
                          command=unlock_edit).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="🔒 KHOA", width=80,
                          command=lock_edit).pack(side="left", padx=5)

            # ===== DAILY =====
            self.daily_var = ctk.BooleanVar(value=self.daily_mode)
            ctk.CTkCheckBox(f, text=t("daily_mode"),
                            variable=self.daily_var,
                            command=self._toggle_daily).pack(pady=(8, 8))

            self.start_btn = ctk.CTkButton(
                f, text=t("start"), height=48, corner_radius=14,
                fg_color=ACCENT, hover_color="#EAB308",
                text_color="#18181F",
                font=ctk.CTkFont(family="Courier New", size=14, weight="bold"),
                command=self.start)
            self.start_btn.pack(fill="x", padx=28, pady=(12, 0))

            ctk.CTkLabel(f, text=t("auto_lock_note"),
                         text_color=TEXT_MUTED,
                         font=ctk.CTkFont(family="Courier New", size=8)
                         ).pack(pady=(6, 20))

        self.running = False
        self.locked  = False
        self._switch(build, height=640)

        email, token = load_session()
        user = email

        if user:
            h, m, s = load_timer(user)
            self.var_h.var.set(f"{h:02d}")
            self.var_m.var.set(f"{m:02d}")
            self.var_s.var.set(f"{s:02d}")

            lh, lm, ls = load_lock_time(user)
            self.lock_h.var.set(f"{lh:02d}")
            self.lock_m.var.set(f"{lm:02d}")
            self.lock_s.var.set(f"{ls:02d}")

        if self.daily_mode:
            total = int(self.var_h.var.get())*3600 + int(self.var_m.var.get())*60 + int(self.var_s.var.get())
            if total > 0:
                self.after(500, self.start)

        self.set_lock_editable(False)

    # ── Restore lock sau khi bật lại máy ──────────────────────
    def _restore_lock(self):
        self.running = False
        self.locked = True

        try:
            self.block_process = subprocess.Popen(resource_path("lock.exe"),
                                                   creationflags=subprocess.CREATE_NO_WINDOW)
        except: pass

        self.lock_win = ctk.CTkToplevel(self)
        self.lock_win.protocol("WM_DELETE_WINDOW", lambda: None)
        w = self.winfo_screenwidth(); h = self.winfo_screenheight()
        self.lock_win.geometry(f"{w}x{h}+0+0")
        self.lock_win.overrideredirect(True)
        self.lock_win.attributes("-topmost", True)
        self.lock_win.configure(fg_color=BG_DARK)

        frame = ctk.CTkFrame(self.lock_win, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(frame, text="🔒", font=ctk.CTkFont(size=72)).pack(pady=(0, 8))
        ctk.CTkLabel(frame, text=t("locked_screen"),
                     font=ctk.CTkFont(family="Courier New", size=28, weight="bold"),
                     text_color=TEXT_PRIMARY).pack()
        ctk.CTkLabel(frame, text=t("restore_lock"),
                     font=ctk.CTkFont(family="Courier New", size=12),
                     text_color=TEXT_MUTED).pack(pady=(4, 12))
        self.lock_remain_label = ctk.CTkLabel(frame, text="...",
                     font=ctk.CTkFont(family="Courier New", size=18, weight="bold"),
                     text_color=DANGER)
        self.lock_remain_label.pack(pady=(0, 12))
        ctk.CTkFrame(frame, height=1, width=280, fg_color=BG_CARD2).pack()
        ctk.CTkButton(
            frame,
            text="MỞ KHẨN CẤP",
            fg_color="orange",
            command=self.emergency_unlock
        ).pack(pady=20)
        self._tick_lock_restore()


    def _tick_lock_restore(self):
        if not self.locked: return
        remain = (self.lock_deadline - datetime.now()).total_seconds()
        if remain <= 0:
            clear_lock_state()
            self.locked = False
            try:
                if hasattr(self, "block_process"): self.block_process.terminate()
                self.lock_win.destroy()
            except: pass
            self.show_main()
            return
        h=int(remain)//3600; m=(int(remain)%3600)//60; s=int(remain)%60
        txt = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
        try: self.lock_remain_label.configure(text=f"{t('unlock_after')} {txt}")
        except: return
        self.lock_win.after(1000, self._tick_lock_restore)

    def verify_password(self):
        popup = ctk.CTkInputDialog(text=t("enter_password"), title=t("title_confirm"))
        pw = popup.get_input()
        if not pw:
            return False

        email, token = load_session()
        ok, _ = db_login(email, pw)
        return ok



    # ── Logic ──────────────────────────────────────────────────
    def _logout(self):
        popup = ctk.CTkInputDialog(text=t("logout_confirm"), title=t("title_confirm"))
        pw = popup.get_input()
        if not pw:
            return

        email, token = load_session()
        ok, _ = db_login(email, pw)
        if ok:

            clear_session()
            self.running = False
            self.locked  = False
            self.show_login()
        else:
            self._set_status(t("wrong_password"), DANGER)


    def _toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
        self.fs_btn.configure(text="✕" if self.is_fullscreen else "⛶")

    def _set_timer_preset(self, secs):
        self.var_h.var.set(f"{secs//3600:02d}")
        self.var_m.var.set(f"{(secs%3600)//60:02d}")
        self.var_s.var.set(f"{secs%60:02d}")

    def _set_lock_preset(self, secs):
        self.lock_h.var.set(f"{secs//3600:02d}")
        self.lock_m.var.set(f"{(secs%3600)//60:02d}")
        self.lock_s.var.set(f"{secs%60:02d}")

    def _set_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)
        self.status_dot.configure(text_color=color)

    def _toggle_daily(self):
        self.daily_mode = self.daily_var.get()
        save_daily_mode(self.daily_mode)

    def start(self):
        if self.running or self.locked:
            return
        try:
            h = int(self.var_h.var.get())
            m = int(self.var_m.var.get())
            s = int(self.var_s.var.get())
            self.total = h*3600 + m*60 + s
            email, token = load_session()
            user = email

            if user:
                save_timer(user, h, m, s)
                lh = int(self.lock_h.var.get())
                lm = int(self.lock_m.var.get())
                ls = int(self.lock_s.var.get())
                save_lock_time(user, lh, lm, ls)
        except ValueError:
            self._set_status(t("error_input"), DANGER)
            return

        if self.total <= 0:
            return

        self.deadline = datetime.now() + timedelta(seconds=self.total)
        save_timer_state(self.deadline, self.total)
        self.running  = True
        self.start_btn.configure(state="disabled", fg_color=ACCENT_DIM, text=t("running"))
        self._set_status(t("running_status"), ACCENT)
        self.tick()

    def tick(self):

        if not self.running:
            return

        if self.locked:
            return

        remain = (self.deadline - datetime.now()).total_seconds()

        minutes_left = int(remain) // 60

        if minutes_left > 0 and minutes_left % 3 == 0:
            if self.last_notify != minutes_left:
                self.last_notify = minutes_left

                msg = t("notify_remaining").format(m=minutes_left)

                toast = Notification(
                    app_id="FocusLock",
                    title="FocusLock",
                    msg=msg,
                    icon=resource_path("icon.ico"),
                    duration="short"
                )
                toast.show()

        if remain <= 0:
            self.circle.update_progress(0, "00:00:00")
            self.lock()
            return

        progress = remain / self.total

        h = int(remain)//3600
        m = (int(remain)%3600)//60
        s = int(remain)%60

        self.circle.update_progress(
            progress,
            f"{h:02d}:{m:02d}:{s:02d}"
        )

        self.after(1000, self.tick)


    def lock(self):
        set_taskmgr_enabled(False)
        self.locked = True
        self.running = False
        clear_timer_state()
        self._set_status(t("locked"), DANGER)
        try:
            self.block_process = subprocess.Popen(
                resource_path("lock.exe"),
                creationflags=subprocess.CREATE_NO_WINDOW)
        except: pass

        try:
            lh=int(self.lock_h.var.get()); lm=int(self.lock_m.var.get()); ls=int(self.lock_s.var.get())
            lock_secs = lh*3600 + lm*60 + ls
        except:
            lock_secs = 300
        if lock_secs <= 0: lock_secs = 300
        self.lock_deadline = datetime.now() + timedelta(seconds=lock_secs)

        save_lock_state(self.lock_deadline)

        self.lock_win = ctk.CTkToplevel(self)
        self.lock_win.protocol("WM_DELETE_WINDOW", lambda: None)
        w = self.winfo_screenwidth(); h = self.winfo_screenheight()
        self.lock_win.geometry(f"{w}x{h}+0+0")
        self.lock_win.overrideredirect(True)
        self.lock_win.attributes("-topmost", True)
        self.lock_win.configure(fg_color=BG_DARK)
        self.lock_win.grab_set()
        self.lock_win.focus_force()

        frame = ctk.CTkFrame(self.lock_win, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(frame, text="🔒", font=ctk.CTkFont(size=72)).pack(pady=(0, 8))
        ctk.CTkLabel(frame, text=t("locked_screen"),
                     font=ctk.CTkFont(family="Courier New", size=28, weight="bold"),
                     text_color=TEXT_PRIMARY).pack()
        ctk.CTkLabel(frame, text=t("session_end"),
                     font=ctk.CTkFont(family="Courier New", size=12),
                     text_color=TEXT_MUTED).pack(pady=(4, 12))
        self.lock_remain_label = ctk.CTkLabel(frame, text="...",
                     font=ctk.CTkFont(family="Courier New", size=18, weight="bold"),
                     text_color=DANGER)
        self.lock_remain_label.pack(pady=(0, 12))
        ctk.CTkFrame(frame, height=1, width=280, fg_color=BG_CARD2).pack()

        def keep_focus():
            if not self.locked: return
            try: self.lock_win.lift(); self.lock_win.focus_force()
            except: return
            self.lock_win.after(300, keep_focus)
        keep_focus()
        self._tick_lock()

    def _tick_lock(self):
        if not self.locked: return
        remain = (self.lock_deadline - datetime.now()).total_seconds()
        if remain <= 0:
            self.unlock(); return
        h=int(remain)//3600; m=(int(remain)%3600)//60; s=int(remain)%60
        txt = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
        try:
            self.lock_remain_label.configure(text=f"{t('unlock_after')} {txt}")
        except:
            return
        self.lock_win.after(1000, self._tick_lock)

    def unlock(self):
        clear_timer_state()
        set_taskmgr_enabled(True)

        self.locked = False
        self.running = False
        self.deadline = None
        self.total = 0

        clear_lock_state()
        clear_timer_state()

        # reset notify
        self.last_notify = -1

        # tắt lock.exe
        if hasattr(self, "block_process"):
            try:
                self.block_process.terminate()
            except:
                pass

        # đóng màn hình khóa
        if hasattr(self, "lock_win"):
            try:
                self.lock_win.destroy()
            except:
                pass

        # KHÔNG reload toàn app nữa
        # chỉ reset UI hiện tại thôi

        if hasattr(self, "start_btn"):
            self.start_btn.configure(
                state="normal",
                fg_color=ACCENT,
                text=t("start")
            )

        if hasattr(self, "circle"):
            self.circle.update_progress(1.0, "--:--:--")

        if hasattr(self, "status_label"):
            self._set_status(t("idle"), TEXT_MUTED)

        self.deiconify()




app = App()
app.mainloop()
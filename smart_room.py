import ctypes
import os
import time
import threading
import sys
import subprocess
import asyncio
import hmac
import hashlib
import requests
import tinytuya
import screen_brightness_control as sbc
from bleak import BleakClient
from flask import Flask, render_template_string, jsonify
from PyQt6.QtCore import Qt, QUrl, QPoint, QSettings
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QSizeGrip, QSystemTrayIcon, QMenu)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# =====================================================================
# تحميل الإعدادات من config.py
# =====================================================================
try:
    from config import (
        TUYA_API_KEY, TUYA_API_SECRET, TUYA_REGION,
        LED_PLUG_ID, LED_PLUG_IP, LED_PLUG_KEY,
        BLE_MAC_ADDRESS, SCENES
    )
except ImportError:
    print("❌ ملف config.py غير موجود — انسخ config.example.py وعدّله")
    sys.exit(1)

app = Flask(__name__)

# =====================================================================
# 1. Tuya Cloud — HMAC-SHA256 signing
# =====================================================================
BASE_URL = f"https://openapi.tuya{TUYA_REGION}.com"

_tuya_token     = None
_tuya_token_exp = 0

def _tuya_sign(method: str, path: str, body: str, token: str, t: int) -> str:
    content_hash = hashlib.sha256(body.encode()).hexdigest()
    str_to_sign  = "\n".join([method, content_hash, "", path])
    message      = TUYA_API_KEY + token + str(t) + str_to_sign
    return hmac.new(TUYA_API_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest().upper()

def _tuya_headers(method: str, path: str, body: str = "", use_token: bool = True) -> dict:
    t   = int(time.time() * 1000)
    tok = _get_token() if use_token else ""
    sig = _tuya_sign(method, path, body, tok, t)
    return {
        "client_id":    TUYA_API_KEY,
        "sign":         sig,
        "sign_method":  "HMAC-SHA256",
        "t":            str(t),
        "access_token": tok,
        "Content-Type": "application/json",
    }

def _get_token() -> str:
    global _tuya_token, _tuya_token_exp
    now = time.time()
    if _tuya_token and now < _tuya_token_exp - 60:
        return _tuya_token
    path = "/v1.0/token?grant_type=1"
    hdrs = _tuya_headers("GET", path, use_token=False)
    resp = requests.get(BASE_URL + path, headers=hdrs, timeout=10).json()
    if resp.get("success"):
        _tuya_token     = resp["result"]["access_token"]
        _tuya_token_exp = now + resp["result"]["expire_time"]
        print(f"✅ Tuya token OK: {_tuya_token[:12]}…")
    else:
        raise RuntimeError(f"Token error: {resp}")
    return _tuya_token

try:
    _get_token()
except Exception as e:
    print(f"⚠️ فشل أول اتصال بـ Tuya: {e}")

# =====================================================================
# 2. الأجهزة
# =====================================================================
led_plug = tinytuya.OutletDevice(LED_PLUG_ID, LED_PLUG_IP, LED_PLUG_KEY)
led_plug.set_version(3.5)

BLE_CHAR_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"
BLE_TURN_ON   = bytearray([0x7e, 0x00, 0x04, 0x01, 0x00, 0x00, 0xff, 0x00, 0xef])
BLE_TURN_OFF  = bytearray([0x7e, 0x00, 0x04, 0x00, 0x00, 0x00, 0xff, 0x00, 0xef])

ble_led_state     = False
ble_command_queue = None
ble_loop          = None

# =====================================================================
# 3. Tuya Scene Trigger
# =====================================================================
def trigger_tuya_scene(scene_id: str) -> dict:
    path = f"/v2.0/cloud/scene/rule/{scene_id}/actions/trigger"
    body = "{}"
    hdrs = _tuya_headers("POST", path, body)
    try:
        resp = requests.post(BASE_URL + path, headers=hdrs, data=body, timeout=10).json()
        print(f"Scene [{scene_id}] → {resp}")
        return resp
    except Exception as e:
        print(f"Scene exception: {e}")
        return {"success": False, "msg": str(e)}

# =====================================================================
# 4. BLE Manager
# =====================================================================
async def ble_manager():
    global ble_led_state
    while True:
        try:
            print("🔄 محاولة الاتصال بلمبة البلوتوث…")
            async with BleakClient(BLE_MAC_ADDRESS) as client:
                print("⚡ تم الاتصال بالبلوتوث!")
                while True:
                    cmd = await ble_command_queue.get()
                    if cmd == "toggle":
                        data = BLE_TURN_OFF if ble_led_state else BLE_TURN_ON
                        await client.write_gatt_char(BLE_CHAR_UUID, data)
                        ble_led_state = not ble_led_state
        except Exception as e:
            print(f"⚠️ انقطع اتصال البلوتوث: {e}")
            await asyncio.sleep(3)

def start_ble_loop():
    global ble_loop, ble_command_queue
    ble_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(ble_loop)
    ble_command_queue = asyncio.Queue()
    ble_loop.run_until_complete(ble_manager())

threading.Thread(target=start_ble_loop, daemon=True).start()

# =====================================================================
# 5. وظائف النظام
# =====================================================================
def shutdown_pc():     os.system("shutdown /s /t 1")
def sleep_pc():        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def kill_server():
    time.sleep(0.2); os._exit(0)

def restart_server():
    time.sleep(0.2)
    subprocess.Popen([sys.executable, sys.argv[0]], creationflags=subprocess.CREATE_NO_WINDOW)
    os._exit(0)

# =====================================================================
# 6. HTML – الواجهة الرئيسية
# =====================================================================
CSS_BASE = """
<style>
    :root {
        --bg: #000000;
        --glass-bg: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.03) 100%);
        --glass-border: rgba(255,255,255,0.12);
        --text-main: #ffffff;
        --text-sub: rgba(255,255,255,0.55);
        --accent: #0a84ff;
        --sheet-bg: rgba(20,20,20,0.65);
    }
    * { box-sizing: border-box; font-family: -apple-system, sans-serif; user-select: none; -webkit-tap-highlight-color: transparent; }
    body {
        background-color: var(--bg); color: var(--text-main);
        margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center;
        height: 100dvh; width: 100vw; overflow: hidden;
        background-image: radial-gradient(circle at 50% -20%, rgba(30,40,60,.8), #000 60%);
    }
    .app-container { max-width: 400px; width: 100%; height: 100%; padding: 50px 20px 30px; overflow-y: auto; scrollbar-width: none; }
    .dynamic-island {
        background: rgba(10,10,10,.8); border: 1px solid rgba(255,255,255,.08); border-radius: 999px;
        padding: 12px 24px; display: flex; justify-content: space-between; align-items: center;
        margin: 0 auto 40px; width: max-content; box-shadow: 0 8px 32px rgba(0,0,0,.5); backdrop-filter: blur(20px);
    }
    .island-text { font-size: 15px; font-weight: 600; }
    .dot-green { width: 8px; height: 8px; background: #32d74b; border-radius: 50%; box-shadow: 0 0 8px #32d74b; margin-right: 12px; }
    .grid { display: grid; grid-template-columns: repeat(2,1fr); gap: 18px; padding-bottom: 20px; }
    .card {
        background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 32px; padding: 22px;
        display: flex; flex-direction: column; justify-content: space-between; aspect-ratio: 1; cursor: pointer;
        backdrop-filter: blur(40px); box-shadow: 0 10px 40px rgba(0,0,0,.2); transition: transform .2s;
    }
    .card:active { transform: scale(.92); }
    .card .icon { font-size: 38px; }
    .card .info { text-align: right; }
    .card .title { font-size: 17px; font-weight: 600; margin-bottom: 2px; }
    .card .subtitle { font-size: 13px; color: var(--text-sub); }
    .sheet-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100dvh;
        background: rgba(0,0,0,.5); backdrop-filter: blur(10px);
        opacity: 0; visibility: hidden; transition: .4s;
        display: flex; align-items: flex-end; justify-content: center; padding: 0 16px 32px; z-index: 999;
    }
    .sheet-overlay.active { opacity: 1; visibility: visible; }
    .sheet-content { width: 100%; max-width: 400px; transform: translateY(120%); transition: .5s; }
    .sheet-overlay.active .sheet-content { transform: translateY(0); }
    .menu-group { background: var(--sheet-bg); border-radius: 32px; margin-bottom: 12px; overflow: hidden; backdrop-filter: blur(50px); border: 1px solid var(--glass-border); }
    .menu-btn { width: 100%; padding: 20px; background: transparent; border: none; color: white; font-size: 18px; cursor: pointer; border-bottom: .5px solid rgba(255,255,255,.08); }
    .menu-btn.red { color: #ff453a; } .menu-btn.blue { color: #32ade6; } .menu-btn.orange { color: #ff9f0a; }
    .cancel-btn { background: var(--sheet-bg); width: 100%; padding: 20px; border-radius: 32px; color: var(--accent); font-size: 18px; font-weight: 600; cursor: pointer; border: 1px solid var(--glass-border); }
    .bright-row { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px 4px; }
    .bright-label { font-size: 17px; font-weight: 600; }
    .bright-val { font-size: 15px; color: var(--text-sub); font-weight: 600; }
    .bright-slider { -webkit-appearance: none; width: calc(100% - 40px); margin: 6px 20px 18px; height: 6px; border-radius: 99px; background: rgba(255,255,255,.15); outline: none; cursor: pointer; display: block; }
    .bright-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 26px; height: 26px; border-radius: 50%; background: #fff; box-shadow: 0 2px 12px rgba(0,0,0,.5); }
</style>
<script>
    function openMenu(id)  { document.getElementById(id).classList.add('active'); }
    function closeMenu(id, event) { if(event) event.stopPropagation(); document.getElementById(id).classList.remove('active'); }
    function trigger(endpoint) { fetch(endpoint).then(r=>r.json()).catch(e=>console.error(e)); }
</script>
"""

ROOM_HTML = f"""
<!DOCTYPE html><html dir="rtl"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Smart Room</title>{CSS_BASE}</head>
<body>
    <div class="app-container">
        <div class="dynamic-island"><div class="island-text">Smart Room</div><div class="dot-green"></div></div>
        <div class="grid">
            <div class="card" onclick="openMenu('pc-sheet')"><div class="icon">💻</div><div class="info"><div class="title">البي سي</div><div class="subtitle">التحكم والطاقة</div></div></div>
            <div class="card" onclick="openMenu('ac-sheet')"><div class="icon">❄️</div><div class="info"><div class="title">التكييف</div><div class="subtitle">المناخ</div></div></div>
            <div class="card" onclick="trigger('/api/scene/tv_power')"><div class="icon">📺</div><div class="info"><div class="title">التلفزيون</div></div></div>
            <div class="card" onclick="trigger('/api/led/toggle')"><div class="icon">🛋️</div><div class="info"><div class="title">الأباجورة</div></div></div>
            <div class="card" onclick="trigger('/api/ble_led/toggle')"><div class="icon">✨</div><div class="info"><div class="title">إضاءة LED</div></div></div>
            <div class="card" onclick="openMenu('server-sheet')"><div class="icon">⚙️</div><div class="info"><div class="title">السيرفر</div></div></div>
        </div>
    </div>

    <!-- PC Sheet -->
    <div class="sheet-overlay" id="pc-sheet" onclick="closeMenu('pc-sheet',event)">
        <div class="sheet-content" onclick="event.stopPropagation()">
            <div class="menu-group">
                <div class="bright-row"><span class="bright-label">☀️ السطوع</span><span class="bright-val" id="bright-val">50%</span></div>
                <input class="bright-slider" id="bright-slider" type="range" min="1" max="100" value="50"
                    oninput="document.getElementById('bright-val').textContent=this.value+'%'"
                    onchange="trigger('/api/bright/'+this.value)">
            </div>
            <div class="menu-group">
                <button class="menu-btn orange" onclick="trigger('/api/pc/sleep');closeMenu('pc-sheet')">🌙 سكون</button>
                <button class="menu-btn red"    onclick="trigger('/api/pc/off');closeMenu('pc-sheet')">🛑 إيقاف</button>
            </div>
            <button class="cancel-btn" onclick="closeMenu('pc-sheet')">إلغاء</button>
        </div>
    </div>

    <!-- AC Sheet -->
    <div class="sheet-overlay" id="ac-sheet" onclick="closeMenu('ac-sheet',event)">
        <div class="sheet-content" onclick="event.stopPropagation()">
            <div class="menu-group">
                <button class="menu-btn blue"   onclick="trigger('/api/scene/super');closeMenu('ac-sheet')">أقصى برودة 🧊</button>
                <button class="menu-btn blue"   onclick="trigger('/api/scene/cold');closeMenu('ac-sheet')">بارد 💨</button>
                <button class="menu-btn blue"   onclick="trigger('/api/scene/mid');closeMenu('ac-sheet')">متوسط 🌤️</button>
                <button class="menu-btn blue"   onclick="trigger('/api/scene/low');closeMenu('ac-sheet')">خفيف 🍃</button>
                <button class="menu-btn red"    onclick="trigger('/api/scene/ac_off');closeMenu('ac-sheet')">إيقاف التكييف 🛑</button>
            </div>
            <button class="cancel-btn" onclick="closeMenu('ac-sheet')">إلغاء</button>
        </div>
    </div>

    <!-- Server Sheet -->
    <div class="sheet-overlay" id="server-sheet" onclick="closeMenu('server-sheet',event)">
        <div class="sheet-content" onclick="event.stopPropagation()">
            <div class="menu-group">
                <button class="menu-btn blue" onclick="trigger('/api/server/restart');closeMenu('server-sheet')">إعادة التشغيل 🔄</button>
                <button class="menu-btn red"  onclick="trigger('/api/server/stop');closeMenu('server-sheet')">إيقاف نهائي 🔌</button>
            </div>
            <button class="cancel-btn" onclick="closeMenu('server-sheet')">إلغاء</button>
        </div>
    </div>
</body></html>
"""

# =====================================================================
# 7. HTML – الويدجت المصغرة لسطح المكتب
# =====================================================================
WIDGET_HTML_TEMPLATE = """
<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8">
<style>
    * { box-sizing: border-box; font-family: -apple-system, sans-serif; user-select: none; }
    body { margin: 0; padding: 8px; height: 100vh; display: flex; align-items: center; justify-content: center; background: transparent; overflow: hidden; }
    .card {
        background: linear-gradient(135deg, rgba(255,255,255,.1) 0%, rgba(255,255,255,.03) 100%);
        border: 1px solid rgba(255,255,255,.15); border-radius: 28px; padding: 16px;
        display: flex; flex-direction: column; justify-content: space-between;
        width: 100%; height: 100%; cursor: pointer; color: white;
        backdrop-filter: blur(30px); box-shadow: 0 10px 40px rgba(0,0,0,.4); transition: transform .1s;
    }
    .card:active { transform: scale(.92); }
    .card .icon { font-size: 36px; margin-bottom: auto; }
    .card .info { text-align: right; }
    .card .title { font-size: 16px; font-weight: bold; }
    .card .subtitle { font-size: 11px; color: rgba(255,255,255,.6); }
    .sheet {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(15,15,15,.85); backdrop-filter: blur(20px); border-radius: 28px;
        display: flex; flex-direction: column; justify-content: center; padding: 10px;
        opacity: 0; visibility: hidden; transition: .2s; z-index: 10;
    }
    .sheet.active { opacity: 1; visibility: visible; }
    .btn { width: 100%; padding: 10px; margin: 2px 0; border: none; border-radius: 12px; background: rgba(255,255,255,.1); color: white; font-weight: bold; cursor: pointer; font-size: 13px; }
    .btn:active { background: rgba(255,255,255,.2); }
    .btn.red { color: #ff453a; } .btn.blue { color: #32ade6; }
</style>
<script>
    function toggleSheet(id) { document.getElementById(id).classList.toggle('active'); }
    function trigger(url) { fetch(url).catch(e=>console.error(e)); }
</script>
</head><body>
{{ content|safe }}
</body></html>
"""

WIDGETS_DATA = {
    "pc": """
        <div class="card" onclick="toggleSheet('sheet')">
            <div class="icon">💻</div>
            <div class="info"><div class="title">البي سي</div><div class="subtitle">الطاقة</div></div>
        </div>
        <div class="sheet" id="sheet">
            <div style="color:white;font-size:12px;font-weight:bold;text-align:center;padding:6px 0 2px">☀️ السطوع — <span id="bv">50</span>%</div>
            <input type="range" min="1" max="100" value="50"
                style="-webkit-appearance:none;width:90%;margin:4px auto 8px;display:block;height:5px;border-radius:99px;background:rgba(255,255,255,.2);outline:none;cursor:pointer"
                oninput="document.getElementById('bv').textContent=this.value"
                onchange="fetch('/api/bright/'+this.value)">
            <button class="btn red"  onclick="trigger('/api/pc/off');toggleSheet('sheet')">🛑 إيقاف البي سي</button>
            <button class="btn"      onclick="toggleSheet('sheet')">↩ رجوع</button>
        </div>""",
    "ac": """
        <div class="card" onclick="toggleSheet('sheet')">
            <div class="icon">❄️</div>
            <div class="info"><div class="title">التكييف</div><div class="subtitle">المناخ</div></div>
        </div>
        <div class="sheet" id="sheet">
            <button class="btn blue" onclick="trigger('/api/scene/super');toggleSheet('sheet')">أقصى برودة 🧊</button>
            <button class="btn blue" onclick="trigger('/api/scene/cold');toggleSheet('sheet')">بارد 💨</button>
            <button class="btn blue" onclick="trigger('/api/scene/mid');toggleSheet('sheet')">متوسط 🌤️</button>
            <button class="btn blue" onclick="trigger('/api/scene/low');toggleSheet('sheet')">خفيف 🍃</button>
            <button class="btn red"  onclick="trigger('/api/scene/ac_off');toggleSheet('sheet')">إيقاف 🛑</button>
            <button class="btn"      onclick="toggleSheet('sheet')">↩ رجوع</button>
        </div>""",
    "tv":   """<div class="card" onclick="trigger('/api/scene/tv_power')"><div class="icon">📺</div><div class="info"><div class="title">التلفزيون</div></div></div>""",
    "lamp": """<div class="card" onclick="trigger('/api/led/toggle')"><div class="icon">🛋️</div><div class="info"><div class="title">الأباجورة</div></div></div>""",
    "led":  """<div class="card" onclick="trigger('/api/ble_led/toggle')"><div class="icon">✨</div><div class="info"><div class="title">إضاءة LED</div></div></div>""",
    "server": """
        <div class="card" onclick="toggleSheet('sheet')">
            <div class="icon">⚙️</div>
            <div class="info"><div class="title">السيرفر</div></div>
        </div>
        <div class="sheet" id="sheet">
            <button class="btn blue" onclick="trigger('/api/server/restart');toggleSheet('sheet')">إعادة التشغيل 🔄</button>
            <button class="btn red"  onclick="trigger('/api/server/stop');toggleSheet('sheet')">إيقاف نهائي 🔌</button>
            <button class="btn"      onclick="toggleSheet('sheet')">↩ رجوع</button>
        </div>""",
}

# =====================================================================
# 8. Routes / APIs
# =====================================================================
@app.route('/')
def room_page():
    return render_template_string(ROOM_HTML)

@app.route('/widget/<name>')
def widget_page(name):
    content = WIDGETS_DATA.get(name, "")
    return render_template_string(WIDGET_HTML_TEMPLATE, content=content)

@app.route('/api/scene/<name>')
def run_scene(name):
    scene_id = SCENES.get(name)
    if not scene_id:
        return jsonify({"status": "error", "msg": "scene not found"}), 404
    result = trigger_tuya_scene(scene_id)
    if result.get("success"):
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "msg": result.get("msg", str(result))}), 500

@app.route('/api/led/toggle')
def led_toggle():
    try:
        status = led_plug.status()
        if status.get('dps', {}).get('1'):
            led_plug.turn_off()
        else:
            led_plug.turn_on()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/api/ble_led/toggle')
def ble_led_toggle():
    if ble_loop and ble_command_queue:
        asyncio.run_coroutine_threadsafe(ble_command_queue.put('toggle'), ble_loop)
    return jsonify({"status": "success"})

@app.route('/api/bright/<int:level>')
def api_bright(level):
    sbc.set_brightness(max(1, min(100, level)))
    return jsonify({"status": "success", "level": level})

@app.route('/api/pc/sleep')
def api_pc_sleep():
    sleep_pc()
    return jsonify({"status": "success"})

@app.route('/api/pc/off')
def api_pc_off():
    shutdown_pc()
    return jsonify({"status": "success"})

@app.route('/api/server/restart')
def api_server_restart():
    threading.Thread(target=restart_server).start()
    return jsonify({"status": "success"})

@app.route('/api/server/stop')
def api_server_stop():
    threading.Thread(target=kill_server).start()
    return jsonify({"status": "success"})

# =====================================================================
# 9. الويدجت العائم — PyQt6 (مع حفظ الموضع والحجم)
# =====================================================================
SETTINGS_ORG = "SmartRoomApp"
SETTINGS_APP = "Widgets"

class FloatingWidget(QWidget):
    def __init__(self, card_id: str, default_x: int, default_y: int):
        super().__init__()
        self.card_id = card_id

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
        saved_x = self.settings.value(f"{card_id}/x",      default_x, type=int)
        saved_y = self.settings.value(f"{card_id}/y",      default_y, type=int)
        saved_w = self.settings.value(f"{card_id}/width",  170,       type=int)
        saved_h = self.settings.value(f"{card_id}/height", 200,       type=int)

        self.resize(saved_w, saved_h)
        self.move(saved_x, saved_y)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Drag header
        self.header = QWidget()
        self.header.setFixedHeight(22)
        self.header.setCursor(Qt.CursorShape.OpenHandCursor)
        ind_layout = QVBoxLayout(self.header)
        ind_layout.setContentsMargins(0, 8, 0, 8)
        indicator = QWidget()
        indicator.setFixedSize(30, 4)
        indicator.setStyleSheet("background-color: rgba(255,255,255,0.4); border-radius: 2px;")
        ind_layout.addWidget(indicator, alignment=Qt.AlignmentFlag.AlignCenter)

        # Web view
        self.browser = QWebEngineView()
        self.browser.page().setBackgroundColor(Qt.GlobalColor.transparent)
        self.browser.setUrl(QUrl(f"http://127.0.0.1:5000/widget/{card_id}"))

        layout.addWidget(self.header)
        layout.addWidget(self.browser)

        # Resize grip
        self.grip = QSizeGrip(self)
        self.grip.setFixedSize(12, 12)
        self.grip.setStyleSheet("background: transparent;")

        self._drag_pos = None

    def _save_geometry(self):
        self.settings.setValue(f"{self.card_id}/x",      self.x())
        self.settings.setValue(f"{self.card_id}/y",      self.y())
        self.settings.setValue(f"{self.card_id}/width",  self.width())
        self.settings.setValue(f"{self.card_id}/height", self.height())
        self.settings.sync()

    def moveEvent(self, event):
        super().moveEvent(event)
        self._save_geometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.grip.move(self.width() - 15, self.height() - 15)
        self.grip.raise_()
        self._save_geometry()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() <= 22:
            self._drag_pos = event.globalPosition().toPoint()
            self.header.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self.header.setCursor(Qt.CursorShape.OpenHandCursor)

# =====================================================================
# 10. WidgetManager + System Tray
# =====================================================================
class WidgetManager(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.widgets: list[FloatingWidget] = []

        self.tray_icon = QSystemTrayIcon()
        icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)

        self.menu = QMenu()
        self.menu.addAction("إظهار / إخفاء الكروت").triggered.connect(self.toggle_widgets)
        self.menu.addAction("إعادة ضبط المواضع").triggered.connect(self.reset_positions)
        self.menu.addSeparator()
        self.menu.addAction("إغلاق السيرفر").triggered.connect(self.quit_app)

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_activated)

    def add_widget(self, w: FloatingWidget):
        self.widgets.append(w)
        w.show()

    def toggle_widgets(self):
        for w in self.widgets:
            w.hide() if w.isVisible() else w.show()

    def reset_positions(self):
        s = QSettings(SETTINGS_ORG, SETTINGS_APP)
        s.clear(); s.sync()
        self.tray_icon.showMessage(
            "Smart Room", "سيتم إعادة الضبط عند إعادة التشغيل 🔄",
            QSystemTrayIcon.MessageIcon.Information, 3000
        )

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_widgets()

    def quit_app(self):
        for w in self.widgets:
            w._save_geometry()
        self.tray_icon.hide()
        self.quit()

# =====================================================================
# التشغيل الرئيسي
# =====================================================================
if __name__ == '__main__':
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=5000, use_reloader=False),
        daemon=True
    )
    flask_thread.start()
    time.sleep(1.5)

    app_qt = WidgetManager(sys.argv)

    sx, sy = 100, 100
    app_qt.add_widget(FloatingWidget("pc",     sx,          sy))
    app_qt.add_widget(FloatingWidget("ac",     sx + 180,    sy))
    app_qt.add_widget(FloatingWidget("tv",     sx + 360,    sy))
    app_qt.add_widget(FloatingWidget("lamp",   sx,          sy + 210))
    app_qt.add_widget(FloatingWidget("led",    sx + 180,    sy + 210))
    app_qt.add_widget(FloatingWidget("server", sx + 360,    sy + 210))

    sys.exit(app_qt.exec())

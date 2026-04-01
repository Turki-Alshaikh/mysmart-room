<div align="center">

# 🏠 My Smart Room Controller

**نظام تحكم ذكي بالغرفة — مبني بـ Python + Flask + PyQt6**

*Personal smart home controller built with Python, Flask & PyQt6*

---

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-41CD52?style=flat-square&logo=qt)](https://pypi.org/project/PyQt6/)
[![Tuya](https://img.shields.io/badge/Tuya-OpenAPI_v2-FF6600?style=flat-square)](https://developer.tuya.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows)](https://microsoft.com/windows)

</div>

---

> **⚠️ ملاحظة شخصية / Personal Note**
>
> هذا المشروع مبني لاستخدامي الشخصي وهو مُخصص لإعداد غرفتي تحديداً.
> يمكنك بالطبع تعديله ليناسب أجهزتك وبيئتك الخاصة — كل الإعدادات موجودة في `config.py`.
>
> *This project was built for my personal use and is tailored to my specific room setup.
> Feel free to adapt it to your own devices and environment — all settings live in `config.py`.*

---

## 📋 المحتويات / Table of Contents

- [المميزات / Features](#-المميزات--features)
- [المتطلبات / Requirements](#-المتطلبات--requirements)
- [التثبيت / Installation](#-التثبيت--installation)
- [الإعداد / Configuration](#-الإعداد--configuration)
- [التشغيل / Usage](#-التشغيل--usage)
- [هيكل المشروع / Project Structure](#-هيكل-المشروع--project-structure)
- [API Reference](#-api-reference)
- [التخصيص / Customization](#-التخصيص--customization)

---

## ✨ المميزات / Features

<table>
<tr>
<td width="50%">

### 🇸🇦 بالعربي

- **واجهة موبايل** — تُفتح من أي متصفح على الشبكة المحلية  
- **كروت سطح المكتب** — ويدجت عائمة مستقلة قابلة للسحب والتكبير  
- **حفظ تلقائي** — يتذكر موضع وحجم كل كارت بعد إعادة التشغيل  
- **Tuya Wi-Fi** — تحكم بالمنافذ الذكية والسيناريوهات  
- **Tuya Scenes** — تشغيل السيناريوهات عبر OpenAPI v2 مع توقيع HMAC-SHA256  
- **Bluetooth BLE** — تحكم بإضاءة LED بلوتوث (MELK / SP110E)  
- **التكييف** — 4 مستويات برودة + إيقاف عبر Tuya Scenes  
- **سطوع الشاشة** — شريط تمرير يُعدّل السطوع مباشرة  
- **التحكم بالنظام** — سكون / إيقاف / إعادة تشغيل السيرفر  
- **System Tray** — إخفاء/إظهار الكروت بنقرة واحدة  

</td>
<td width="50%">

### 🇬🇧 In English

- **Mobile Web UI** — accessible from any browser on local network  
- **Desktop Widgets** — floating draggable & resizable cards  
- **Persistent Layout** — remembers position & size across restarts  
- **Tuya Wi-Fi** — control smart plugs and automations  
- **Tuya Scenes** — trigger via OpenAPI v2 with proper HMAC-SHA256 signing  
- **Bluetooth BLE** — control BLE LED strips (MELK / SP110E)  
- **AC Control** — 4 cooling levels + off via Tuya Scenes  
- **Screen Brightness** — live slider to adjust display brightness  
- **System Control** — sleep / shutdown / server restart  
- **System Tray** — show/hide all widgets with a single click  

</td>
</tr>
</table>

---

## 🖥️ لقطات الشاشة / Screenshots

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│   ╭─────────────────────────────╮                    │
│   │      ● Smart Room           │  ← Dynamic Island  │
│   ╰─────────────────────────────╯                    │
│                                                      │
│   ┌─────────────┐  ┌─────────────┐                   │
│   │  💻          │  │  ❄️          │                   │
│   │             │  │             │                   │
│   │    البي سي  │  │   التكييف   │                   │
│   └─────────────┘  └─────────────┘                   │
│   ┌─────────────┐  ┌─────────────┐                   │
│   │  📺          │  │  🛋️          │                   │
│   │             │  │             │                   │
│   │  التلفزيون  │  │  الأباجورة  │                   │
│   └─────────────┘  └─────────────┘                   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 📦 المتطلبات / Requirements

| المتطلب | الإصدار |
|---------|---------|
| Python  | 3.11+   |
| Windows | 10 / 11 |
| Bluetooth | BLE 4.0+ |
| الشبكة | Wi-Fi (نفس شبكة الأجهزة) |

---

## 🔧 التثبيت / Installation

### 1. استنساخ المشروع / Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/smart-room.git
cd smart-room
```

### 2. إنشاء بيئة افتراضية / Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. تثبيت المكتبات / Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ الإعداد / Configuration

### الخطوة الأولى — إنشاء ملف الإعدادات / Step 1 — Create config file

```bash
cp config.example.py config.py
```

ثم عدّل `config.py` بقيمك الخاصة / Then edit `config.py` with your own values.

---

### الحصول على مفاتيح Tuya / Getting Tuya Keys

#### API Key & Secret
1. اذهب إلى [iot.tuya.com](https://iot.tuya.com)
2. **Cloud → Development → Create Cloud Project**
3. اختر المنطقة المناسبة (EU, US, CN, IN)
4. انسخ `Access ID` → `TUYA_API_KEY`
5. انسخ `Access Secret` → `TUYA_API_SECRET`

#### Device ID & Local Key
```bash
# ثبّت tinytuya وشغّل المسح
python -m tinytuya wizard
```
سيُوفر لك `device_id` و `local_key` لكل جهاز.

#### Scene IDs
1. اذهب إلى Tuya IoT Platform
2. **Cloud → Scene Management → Automation**
3. افتح السينا المطلوب → انسخ الـ `Rule ID`

---

### الحصول على MAC Address البلوتوث / Getting BLE MAC Address

```python
import asyncio
from bleak import BleakScanner

async def scan():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d.address, d.name)

asyncio.run(scan())
```

ابحث عن اسم جهازك في القائمة وانسخ الـ MAC Address.

---

## 🚀 التشغيل / Usage

```bash
python smart_room.py
```

بعد التشغيل:
- **الواجهة الرئيسية:** `http://localhost:5000` أو `http://YOUR_PC_IP:5000` من الجوال
- **كروت سطح المكتب:** تظهر تلقائياً
- **System Tray:** أيقونة بجانب الساعة للتحكم

After running:
- **Main UI:** `http://localhost:5000` or `http://YOUR_PC_IP:5000` from mobile
- **Desktop Widgets:** appear automatically on screen
- **System Tray:** icon near clock for quick control

### 🔁 تشغيل تلقائي مع Windows / Auto-start with Windows

المشروع مُعدّ للتشغيل التلقائي عند بدء تشغيل الجهاز بدون أي نافذة مرئية عبر ملف **VBScript**.

*The project is set up to auto-start at boot silently via a **VBScript** file — no console window appears.*

---

#### الطريقة المستخدمة — VBScript (مخفي تماماً) / Method Used — Hidden VBScript

**الخطوة 1:** اضغط `Win + R` واكتب:
```
shell:startup
```
سيفتح مجلد:
```
C:\Users\YOUR_PC_NAME\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

**الخطوة 2:** أنشئ ملفاً باسم `start_hidden.vbs` داخل هذا المجلد بالمحتوى التالي:

```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\Users\YOUR_PC_NAME\AppData\Local\Python\pythoncore-3.14-64\python.exe"" ""C:\Turki Smart Room\TurkiSmartRoom.py""", 0, False
```

> **⚠️ عدّل المسارين حسب جهازك:**
> - `YOUR_PC_NAME` → اسم مستخدم جهازك
> - مسار `python.exe` → تحقق منه بتشغيل `where python` في CMD
> - مسار الملف → المكان الذي وضعت فيه `smart_room.py`

---

#### شرح المعاملات / Parameter Explanation

| المعامل | القيمة | المعنى |
|---------|--------|--------|
| `WshShell.Run` | الأمر | تشغيل برنامج |
| `, 0,` | `0` = مخفي | **لا تظهر أي نافذة** |
| `, False` | لا تنتظر | يكمل Windows الإقلاع بدون انتظار |

---

#### للتحقق من مسار Python / Verify Python path

```cmd
where python
```
أو إذا عندك إصدارات متعددة:
```cmd
py -3.14 -c "import sys; print(sys.executable)"
```

---

#### إيقاف التشغيل التلقائي / Disable Auto-start

احذف ملف `start_hidden.vbs` من مجلد Startup أو غيّر اسمه مؤقتاً.

---

## 📁 هيكل المشروع / Project Structure

```
smart-room/
│
├── smart_room.py          # الملف الرئيسي / Main application
├── config.py              # إعداداتك الخاصة (لا يُرفع) / Your private config
├── config.example.py      # نموذج الإعدادات / Config template
├── requirements.txt       # المكتبات المطلوبة / Dependencies
├── .gitignore             # استثناء الملفات الحساسة
└── README.md              # هذا الملف / This file
```

---

## 📡 API Reference

جميع الـ endpoints تعيد JSON. All endpoints return JSON.

| Endpoint | الوصف | Description |
|----------|-------|-------------|
| `GET /` | الواجهة الرئيسية | Main web UI |
| `GET /widget/<name>` | ويدجت سطح المكتب | Desktop widget HTML |
| `GET /api/scene/<name>` | تشغيل سينا | Trigger Tuya scene |
| `GET /api/led/toggle` | تشغيل/إيقاف الأباجورة | Toggle Wi-Fi plug |
| `GET /api/ble_led/toggle` | تشغيل/إيقاف LED BLE | Toggle BLE LED |
| `GET /api/bright/<0-100>` | ضبط السطوع | Set screen brightness |
| `GET /api/pc/sleep` | وضع السكون | Sleep PC |
| `GET /api/pc/off` | إيقاف الكمبيوتر | Shutdown PC |
| `GET /api/server/restart` | إعادة تشغيل السيرفر | Restart Flask server |
| `GET /api/server/stop` | إيقاف السيرفر | Stop server |

### أسماء السيناريوهات المدعومة / Supported Scene Names

| الاسم | الوصف |
|-------|-------|
| `super` | أقصى برودة |
| `cold` | بارد |
| `mid` | متوسط |
| `low` | خفيف |
| `ac_off` | إيقاف التكييف |
| `tv_power` | تشغيل/إيقاف التلفاز |

### أمثلة / Examples

```bash
# تشغيل التكييف على أقصى برودة
curl http://localhost:5000/api/scene/super

# ضبط السطوع على 70%
curl http://localhost:5000/api/bright/70

# إيقاف الأباجورة
curl http://localhost:5000/api/led/toggle
```

---

## 🎨 التخصيص / Customization

### إضافة جهاز جديد / Adding a new device

**1. في `config.py` أضف الإعدادات:**
```python
MY_NEW_DEVICE_IP  = "192.168.1.XX"
MY_NEW_DEVICE_KEY = "your_key"
```

**2. في `smart_room.py` أضف الجهاز:**
```python
new_device = tinytuya.OutletDevice(DEVICE_ID, DEVICE_IP, DEVICE_KEY)
new_device.set_version(3.5)
```

**3. أضف Route:**
```python
@app.route('/api/new_device/toggle')
def new_device_toggle():
    # منطقك هنا
    return jsonify({"status": "success"})
```

**4. أضف كارت في `WIDGETS_DATA` و `ROOM_HTML`:**
```python
"new_device": """
    <div class="card" onclick="trigger('/api/new_device/toggle')">
        <div class="icon">🔌</div>
        <div class="info"><div class="title">جهازي الجديد</div></div>
    </div>"""
```

**5. أضف الويدجت في التشغيل الرئيسي:**
```python
app_qt.add_widget(FloatingWidget("new_device", sx + 540, sy))
```

---

### تغيير إضاءة BLE / Changing BLE LED Protocol

بعض الأجهزة تستخدم بروتوكولات مختلفة. عدّل هذه القيم في `smart_room.py`:

```python
BLE_CHAR_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"  # UUID الخاص بجهازك
BLE_TURN_ON   = bytearray([...])   # أوامر جهازك
BLE_TURN_OFF  = bytearray([...])
```

---

## 🏗️ كيف يعمل / How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                        smart_room.py                         │
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ Flask Server│    │  BLE Thread  │    │   PyQt6 App   │  │
│  │  :5000      │    │  (asyncio)   │    │  Tray+Widgets │  │
│  └──────┬──────┘    └──────┬───────┘    └───────┬───────┘  │
│         │                  │                    │           │
│         ▼                  ▼                    ▼           │
│   HTTP Routes         BLE Commands         QWebEngineView   │
│   /api/scene/...     toggle on/off        → localhost:5000  │
│   /api/led/...                                              │
│   /api/bright/...                                           │
│         │                                                   │
│         ▼                                                   │
│   ┌─────────────────────────────┐                           │
│   │      Tuya OpenAPI v2        │                           │
│   │  HMAC-SHA256 signed calls   │                           │
│   │  Scene Trigger / Token Mgmt │                           │
│   └─────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔒 الأمان / Security

- `config.py` مُدرج في `.gitignore` — **لا يُرفع أبداً على GitHub**
- السيرفر يعمل على الشبكة المحلية فقط — لا يوجد وصول من الإنترنت
- مفاتيح Tuya محلية للاتصال المباشر بالأجهزة دون المرور بالسحابة

---

## 🛠️ المشاكل الشائعة / Troubleshooting

| المشكلة | الحل |
|---------|------|
| `500 error` في السيناريوهات | تأكد من صحة `TUYA_API_KEY` و `Scene IDs` في `config.py` |
| البلوتوث لا يتصل | تأكد من أن البلوتوث مفعّل وأن الـ MAC صحيح |
| الأباجورة لا تستجيب | شغّل `python -m tinytuya scan` للتحقق من الـ IP |
| الكروت لا تظهر | انتظر 2 ثانية بعد التشغيل حتى يقلع Flask |
| خطأ `ImportError` | تأكد من تفعيل البيئة الافتراضية `venv\Scripts\activate` |

---

## 📄 الرخصة / License

MIT License — استخدم، عدّل، وشارك بحرية.

*Use, modify, and share freely.*

---

<div align="center">

بُني بـ ❤️ لغرفة واحدة — يمكنك تعديله لأي غرفة

*Built with ❤️ for one room — adapt it for any room*

</div>

# =====================================================================
# config.example.py
# ─────────────────────────────────────────────────────────────────────
# انسخ هذا الملف باسم config.py وعدّل القيم بما يناسب أجهزتك.
# Copy this file as config.py and fill in your own values.
# =====================================================================

# ── Tuya Cloud API ────────────────────────────────────────────────────
# الحصول عليها من: https://iot.tuya.com → Cloud → My Projects
# Get from: https://iot.tuya.com → Cloud → My Projects

TUYA_API_KEY    = "YOUR_TUYA_API_KEY"
TUYA_API_SECRET = "YOUR_TUYA_API_SECRET"

# المنطقة: "eu" | "us" | "cn" | "in"
# Region:  "eu" | "us" | "cn" | "in"
TUYA_REGION = "eu"

# ── Tuya Local Device (الأباجورة / Smart Plug) ───────────────────────
# للحصول على هذه القيم شغّل: python -m tinytuya scan
# Get these by running: python -m tinytuya scan

LED_PLUG_ID  = "YOUR_DEVICE_ID"
LED_PLUG_IP  = "AUTO"            # أو IP ثابت مثل "192.168.1.50"
LED_PLUG_KEY = "YOUR_DEVICE_LOCAL_KEY"

# ── Bluetooth LED (MELK / SP110E or similar) ─────────────────────────
# ابحث عن MAC address عبر: python -m bleak.backends.p4android.scanner
# Scan for MAC: python -c "import asyncio; from bleak import BleakScanner; asyncio.run(BleakScanner.discover())"

BLE_MAC_ADDRESS = "XX:XX:XX:XX:XX:XX"

# ── Tuya Scene IDs ────────────────────────────────────────────────────
# احصل عليها من Tuya IoT → Cloud → Scene → انسخ الـ Rule ID
# Get from Tuya IoT → Cloud → Automation → copy the Rule ID

SCENES = {
    "super":    "YOUR_SCENE_ID_SUPER_COLD",
    "cold":     "YOUR_SCENE_ID_COLD",
    "mid":      "YOUR_SCENE_ID_MID",
    "low":      "YOUR_SCENE_ID_LOW",
    "ac_off":   "YOUR_SCENE_ID_AC_OFF",
    "tv_power": "YOUR_SCENE_ID_TV_POWER",
}

"""RTRW-Net Monitor: pantau sinyal klien Mikrotik dan kirim alert ke Telegram."""
import os
import re
import time
import logging

import requests
import urllib3

HOST = os.environ["MIKROTIK_HOST"]
USER = os.environ["MIKROTIK_USER"]
PASSWORD = os.environ["MIKROTIK_PASS"]
VERIFY_SSL = os.getenv("MIKROTIK_VERIFY_SSL", "false").lower() == "true"
ENDPOINT = os.getenv("MIKROTIK_ENDPOINT", "/rest/interface/wireless/registration-table")
THRESHOLD = int(os.getenv("THRESHOLD_DBM", "-75"))
INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
COOLDOWN = int(os.getenv("ALERT_COOLDOWN", "1800"))
TG_TOKEN = os.environ["TELEGRAM_TOKEN"]
TG_CHAT = os.environ["TELEGRAM_CHAT_ID"]

if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("rtrw-monitor")

last_alert = {}    # mac -> waktu alert terakhir
weak_clients = set()
router_down = False


def send_telegram(text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        log.error("Gagal kirim Telegram: %s", e)


def parse_signal(raw):
    """Ubah '-65@5GHz' atau '-65' menjadi integer -65."""
    m = re.match(r"-?\d+", str(raw or ""))
    return int(m.group()) if m else None


def fetch_clients():
    r = requests.get(
        f"https://{HOST}{ENDPOINT}",
        auth=(USER, PASSWORD),
        verify=VERIFY_SSL,
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def check():
    global router_down
    try:
        clients = fetch_clients()
    except requests.RequestException as e:
        log.error("Router tidak bisa diakses: %s", e)
        if not router_down:
            router_down = True
            send_telegram(f"🔴 <b>Router tidak merespons</b>\n{HOST}")
        return

    if router_down:
        router_down = False
        send_telegram(f"🟢 <b>Router kembali online</b>\n{HOST}")

    now = time.time()
    current_weak = set()

    for c in clients:
        mac = c.get("mac-address", "?")
        signal = parse_signal(c.get("signal-strength", c.get("signal")))
        if signal is None:
            continue
        name = c.get("comment") or c.get("last-ip") or mac

        if signal < THRESHOLD:
            current_weak.add(mac)
            if now - last_alert.get(mac, 0) >= COOLDOWN:
                last_alert[mac] = now
                send_telegram(
                    f"⚠️ <b>Sinyal lemah</b>\n"
                    f"Klien: {name}\nMAC: {mac}\n"
                    f"Sinyal: {signal} dBm (batas {THRESHOLD})\n"
                    f"Interface: {c.get('interface', '-')}"
                )

    for mac in weak_clients - current_weak:
        send_telegram(f"✅ Sinyal klien {mac} sudah normal kembali.")
        last_alert.pop(mac, None)

    weak_clients.clear()
    weak_clients.update(current_weak)
    log.info("Cek selesai: %d klien, %d lemah", len(clients), len(current_weak))


if __name__ == "__main__":
    log.info("Monitor dimulai (interval %ss, batas %s dBm)", INTERVAL, THRESHOLD)
    while True:
        check()
        time.sleep(INTERVAL)

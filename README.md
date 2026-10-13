# 📡 RTRW-Net Monitor

[![CI](https://github.com/USERNAME/rtrw-net-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/rtrw-net-monitor/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)

Memantau sinyal klien jaringan RT RW Net lewat RouterOS REST API (Mikrotik v7+) dan mengirim alert ke Telegram saat sinyal lemah atau router tidak merespons.

## ✨ Fitur
- Cek sinyal semua klien wireless secara berkala
- Alert Telegram saat sinyal di bawah ambang batas, plus notifikasi pulih
- Cooldown agar alert tidak spam
- Deteksi router down / kembali online
- Berjalan di Docker

## 🧱 Arsitektur
```text
Mikrotik (REST API) --> monitor.py --> Telegram
```

## ⚙️ Persiapan Router
```routeros
/user group add name=monitor policy=read,api,rest-api
/user add name=monitor group=monitor password=GANTI_PASSWORD
/ip service enable www-ssl
/ip service set www-ssl address=IP_SERVER_MONITOR/32
```

## 🚀 Instalasi
```bash
git clone https://github.com/GiexId/Route-Monitoring.git
cd rtrw-net-monitor
cp .env.example .env    # isi konfigurasi
docker compose up -d --build
docker compose logs -f
```

Tanpa Docker:
```bash
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)
python monitor.py
```

## 🔑 Konfigurasi
| Variabel | Fungsi |
|---|---|
| `MIKROTIK_HOST` | IP router |
| `MIKROTIK_USER` / `MIKROTIK_PASS` | Akun read-only |
| `MIKROTIK_ENDPOINT` | Path registration-table (wireless / wifi) |
| `THRESHOLD_DBM` | Batas sinyal, mis. -75 |
| `CHECK_INTERVAL` | Jeda cek (detik) |
| `ALERT_COOLDOWN` | Jeda alert ulang per klien (detik) |
| `TELEGRAM_TOKEN` / `TELEGRAM_CHAT_ID` | Tujuan notifikasi |

## 🗺️ Rencana
- [ ] Grafik riwayat sinyal
- [ ] Integrasi n8n untuk alur lanjutan
- [ ] Monitoring CPU & latency router

## 📄 Lisensi
MIT

# Discord Bot Manager  
GUI modern untuk mengelola multi-akun Discord Bot, multi-channel, dan multi-world, lengkap dengan fitur RUN/STOP bot.

---

## 🚀 Fitur Utama
- Mengatur banyak akun Discord sekaligus  
- Channel list per akun (add/edit/delete)  
- World list per akun (add/delete, dipilih & dirandom oleh bot)  
- Delay min/max per channel  
- Counter pesan per channel  
- Checkbox akun yang ingin dijalankan  
- RUN / STOP bot langsung dari GUI  
- Auto update `config.json`  
- Webhook notifikasi (start, error, finish)  

---

## 📁 Struktur Folder
Project/
│ gui.py
│ requirements.txt
│ README.md
│
├── config/
│ └── config.json
│
└── main/
└── main.py

---

## 🔧 Instalasi

### 1️⃣ Install Python (jika belum ada)
Download Python di:
https://www.python.org/downloads/

Pastikan centang: Add Python to PATH

### 2️⃣ Install Dependencies
Buka terminal di folder project:

```sh
pip install -r requirements.txt


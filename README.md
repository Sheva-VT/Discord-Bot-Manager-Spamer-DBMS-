# Discord Bot Manager  
GUI sederhana & modern untuk mengatur multi-akun Discord, multi-channel, multi-world, lengkap dengan tombol RUN/STOP bot.

---

## 🚀 Fitur Utama
- Multi akun Discord (token + webhook per akun)
- Multi channel per akun (add/edit/delete)
- Multi world per akun (diacak / random saat mengirim pesan)
- Delay min/max per channel
- Counter jumlah pesan per channel
- Centang akun mana yang ingin dijalankan
- Tombol RUN / STOP bot langsung dari GUI
- Auto update file `config.json`
- Webhook notifikasi (Start, Error, Finish)

---

## 📁 Struktur Folder
```
Project/
│ gui.py
│ requirements.txt
│ README.md
│
├── config/
│   └── config.json
│
└── main/
    └── main.py
```

---

## 🔧 Instalasi

### 1️⃣ Install Python  
Download di:  
https://www.python.org/downloads/  
*Pastikan centang: Add Python to PATH*

---

### 2️⃣ Install Dependencies  
Buka Terminal/CMD di folder project:

```
pip install -r requirements.txt
```

---

## ▶️ Cara Menjalankan  
Jalankan GUI:

```
python gui.py
```

Gunakan GUI untuk:
- Menambah akun  
- Menambah channel  
- Menambah world  
- Mengatur delay / count  
- Memilih akun yang ingin dirun  
- Menjalankan bot via tombol RUN  
- Menghentikan bot via tombol STOP  

---

## 📘 Tutorial Penting
### 🔹 Cara mengambil Token Discord
1. Buka Discord → tekan **CTRL + SHIFT + I**  
2. Ke Tab **Network**  
3. Klik request apa saja  
4. Cari di Header: **authorization**  
5. Copy token

### 🔹 Cara mengambil Webhook
1. Server Settings → Integrations → Webhooks  
2. Create webhook  
3. Copy URL

### 🔹 Cara mengambil Channel ID
1. Discord → User Settings  
2. Advanced → Aktifkan **Developer Mode**  
3. Klik kanan channel → Copy ID

---

## 📞 Support
Jika ada bug/error, silakan lapor via instagram : rap.husni
---

# Telegram Media Copier User Bot

Bot pengguna (user bot) yang dibuat dengan Telethon untuk secara otomatis memantau channel dan menyalin semua pesan media. Bot ini memiliki alur kerja interaktif yang canggih.

## Fitur

- **Startup Interaktif**: Saat dimulai, bot akan meminta admin untuk memberikan target channel dan pesan awal melalui chat.
- **Dua Mode Operasi**:
  1.  **Mode Riwayat**: Menyalin semua media dari titik awal yang ditentukan hingga pesan terbaru.
  2.  **Mode Real-time**: Setelah riwayat selesai, bot akan memantau channel untuk pesan baru secara real-time.
- **Penanganan Canggih**:
  - Menyalin media tunggal dan album dengan benar.
  - Menambahkan caption informatif (sumber, pengirim, waktu, link asli) ke setiap media yang disalin.
  - Penanganan `Rate Limit` otomatis dengan mekanisme `retry-after`.
- **Autentikasi Berbasis File Sesi**: Login yang mudah pada penggunaan pertama, dan otomatis pada penggunaan selanjutnya.

## Prasyarat

- Python 3.8 atau lebih baru.
- Akun Telegram dengan `API_ID` dan `API_HASH`. Anda bisa mendapatkannya dari [my.telegram.org](https://my.telegram.org).

## Instruksi Instalasi & Konfigurasi

**1. Dapatkan Kode**

Unduh atau clone repositori ini ke komputer Anda.

**2. Buat File Konfigurasi (`.env`)**

Buat file baru bernama `.env` di direktori yang sama dengan `main.py`. Salin konten dari `.env.example` dan isi dengan nilai yang benar:

```ini
# Ganti dengan kredensial Anda dari my.telegram.org
API_ID=1234567
API_HASH=abcdef1234567890abcdef1234567890

# Beri nama untuk file sesi Anda, contoh: userbot.
# File [NAMA_SESI].session akan dibuat saat pertama kali dijalankan.
SESSION_NAME=userbot

# Masukkan ID atau username dari channel tujuan
DESTINATION_CHANNEL=-1009876543210

# Masukkan ID chat atau username Anda (admin).
# Bot akan mengirim pesan ke ID ini saat dimulai untuk meminta instruksi.
NOTIFICATION_CHAT_ID=123456789
```

**3. Instal Dependensi**

Buka terminal atau command prompt di direktori proyek dan jalankan:
```bash
pip install -r requirements.txt
```

## Menjalankan Bot

**1. Login Pertama Kali**

Saat Anda menjalankan bot untuk **pertama kalinya** dengan `SESSION_NAME` yang baru, Telethon akan meminta Anda untuk login:
```bash
python main.py
# Anda akan diminta memasukkan nomor telepon, kode verifikasi, dan password 2FA.
```
Setelah login berhasil, sebuah file `[SESSION_NAME].session` akan dibuat. Untuk selanjutnya, bot akan menggunakan file ini dan tidak akan meminta login lagi.

**2. Operasi Normal**

Setelah login, bot akan mengirim pesan ke `NOTIFICATION_CHAT_ID` Anda, meminta instruksi.
- **Kirimkan link pesan**: Balas pesan bot dengan mengirimkan link ke pesan di channel target yang ingin Anda jadikan titik awal.
  - Contoh: `https://t.me/c/1234567890/500`
- Bot akan mengonfirmasi instruksi dan mulai bekerja, pertama dalam mode riwayat, lalu beralih ke mode real-time.

Untuk menghentikan bot, tekan `Ctrl+C` di terminal.

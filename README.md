# Telegram Media Copier User Bot

Bot pengguna (user bot) sederhana yang dibuat dengan Telethon untuk secara otomatis memantau supergrup/channel dan menyalin semua pesan media baru ke channel tujuan.

## Fitur

- Memantau channel/supergrup sumber secara real-time.
- Menyalin pesan yang berisi media (foto, video, dokumen, dll.) beserta caption-nya.
- Mengabaikan pesan teks murni.
- Konfigurasi yang aman menggunakan file `.env`.
- Menggunakan Session String untuk login (tidak perlu memasukkan nomor telepon/kode setiap kali).
- Memberikan notifikasi ke chat lain jika bot berhenti karena error.

## Prasyarat

- Python 3.8 atau lebih baru.
- Akun Telegram dengan `API_ID` dan `API_HASH`. Anda bisa mendapatkannya dari [my.telegram.org](https://my.telegram.org).

## Instruksi Instalasi & Konfigurasi

**1. Dapatkan Kode**

Unduh atau clone repositori ini ke komputer Anda.

**2. Buat File Konfigurasi (`.env`)**

Buat file baru bernama `.env` di direktori yang sama dengan `main.py`. Anda bisa menyalin dari file `.env.example` yang telah disediakan.

Isi file `.env` dengan nilai yang benar:

```ini
# Ganti dengan kredensial Anda dari my.telegram.org
API_ID=1234567
API_HASH=abcdef1234567890abcdef1234567890

# String sesi Telethon Anda. Lihat cara membuatnya di bawah.
SESSION_STRING=xxxxxxxxxxxxxxxxx

# Masukkan ID atau username dari channel/supergroup sumber
# Contoh: -1001234567890 atau 'namachannelpublik'
SOURCE_CHANNEL=-1001234567890

# Masukkan ID atau username dari channel tujuan
# Contoh: -1009876543210 atau 'channelku'
DESTINATION_CHANNEL=-1009876543210

# Masukkan ID chat atau username tujuan untuk notifikasi error
# Contoh: 123456789 (untuk user) atau 'usernamebot'
NOTIFICATION_CHAT_ID=123456789
```
**Penting:**
- Untuk mendapatkan ID channel/grup privat, Anda bisa menggunakan bot seperti `@userinfobot`. Forward pesan dari channel tersebut ke bot ini untuk melihat ID-nya.
- ID channel/grup biasanya diawali dengan `-100`.

**3. Hasilkan `SESSION_STRING`**

Bot ini menggunakan string sesi agar tidak perlu login berulang kali. Jika Anda belum memilikinya, Anda perlu membuatnya sekali.

- Pastikan Anda sudah mengisi `API_ID` dan `API_HASH` di file `.env` Anda (ini akan mempermudah).
- Jalankan skrip `generate_session.py` yang telah disediakan:
  ```bash
  python generate_session.py
  ```
- Skrip akan meminta Anda untuk memasukkan nomor telepon, kode login, dan password 2FA (jika ada).
- Setelah berhasil, skrip akan mencetak `SESSION_STRING`. Salin string tersebut dan tempelkan ke file `.env` Anda.

**4. Instal Dependensi**

Buka terminal atau command prompt di direktori proyek dan jalankan:
```bash
pip install -r requirements.txt
```

## Menjalankan Bot

Setelah semua konfigurasi selesai, jalankan bot utama dengan perintah:
```bash
python main.py
```

Bot akan berjalan, memantau pesan baru dan menyalinnya sesuai konfigurasi. Anda akan melihat log aktivitas di terminal. Untuk menghentikan bot, tekan `Ctrl+C`.

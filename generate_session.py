import os
from telethon import TelegramClient
from dotenv import load_dotenv

# Muat variabel dari .env jika ada, untuk memudahkan
load_dotenv()

print("="*30)
print("  Generator String Sesi Telethon")
print("="*30)
print("Skrip ini akan memandu Anda untuk membuat SESSION_STRING.")
print("Anda akan diminta memasukkan API ID, API Hash, dan nomor telepon.")
print("Setelah login, string sesi akan dicetak di layar.")
print("-" * 30)

# Coba ambil kredensial dari file .env, jika tidak ada, minta input dari pengguna
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

if not API_ID:
    API_ID = input("Masukkan API ID Anda: ")

if not API_HASH:
    API_HASH = input("Masukkan API Hash Anda: ")

# Validasi bahwa API_ID adalah angka
try:
    API_ID = int(API_ID)
except (ValueError, TypeError):
    print("\n[Error] API_ID harus berupa angka. Harap jalankan kembali skrip.")
    exit()

# Menggunakan sesi di memori karena kita hanya butuh string-nya untuk dicetak
# Ini tidak akan membuat file .session
with TelegramClient(':memory:', API_ID, API_HASH) as client:
    print("\nClient Telethon sedang dimulai...")
    # `client.session.save()` akan mengembalikan string sesi saat ini
    # Kita panggil di dalam `send_code_request` karena sesi baru dibuat setelahnya
    client.send_code_request(input("Masukkan nomor telepon Anda (format +62xxxx): "))
    client.sign_in(phone=client.phone, code=input('Masukkan kode yang Anda terima: '))

    session_string = client.session.save()

    print("\nLogin berhasil! Anda telah terhubung.")
    print("Simpan string sesi ini dengan aman dan jangan bagikan kepada siapa pun!")
    print("\nSESSION_STRING ANDA:\n")
    print(f"{session_string}")
    print("\nSalin string di atas dan masukkan ke dalam file .env Anda.")

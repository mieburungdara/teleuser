import asyncio
import os
from telethon import TelegramClient
from dotenv import load_dotenv

async def main():
    """Fungsi utama untuk menghasilkan string sesi secara asinkron."""
    # Muat variabel dari .env jika ada, untuk memudahkan
    load_dotenv()

    print("="*30)
    print("  Generator String Sesi Telethon")
    print("="*30)

    # Coba ambil kredensial dari file .env, jika tidak ada, minta input dari pengguna
    api_id_str = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')

    if not api_id_str:
        api_id_str = input("Masukkan API ID Anda: ")

    if not api_hash:
        api_hash = input("Masukkan API Hash Anda: ")

    # Validasi bahwa API_ID adalah angka
    try:
        api_id = int(api_id_str)
    except (ValueError, TypeError):
        print("\n[Error] API_ID harus berupa angka. Harap jalankan kembali skrip.")
        return

    # Menggunakan sesi di memori karena kita hanya butuh string-nya untuk dicetak
    async with TelegramClient(':memory:', api_id, api_hash) as client:
        print("\nClient Telethon sedang dimulai...")

        phone_number = input("Masukkan nomor telepon Anda (format +62xxxx): ")

        await client.send_code_request(phone_number)
        print("Kode verifikasi telah dikirim.")

        # Minta kode dan password (jika ada)
        code = input("Masukkan kode yang Anda terima: ")
        password = input("Masukkan password 2FA Anda (jika tidak ada, tekan Enter): ")

        try:
            # Coba login
            if password:
                await client.sign_in(phone_number, code, password=password)
            else:
                await client.sign_in(phone_number, code)
        except Exception as e:
            print(f"\n[Error] Gagal login: {e}")
            return

        print("\nLogin berhasil! Anda telah terhubung.")
        print("Simpan string sesi ini dengan aman dan jangan bagikan kepada siapa pun!")

        session_string = client.session.save()
        print("\nSESSION_STRING ANDA:\n")
        print(f"{session_string}")
        print("\nSalin string di atas dan masukkan ke dalam file .env Anda.")

if __name__ == "__main__":
    # Menjalankan loop event asyncio untuk fungsi main
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nProses dibatalkan oleh pengguna.")
    finally:
        print("Skrip selesai.")

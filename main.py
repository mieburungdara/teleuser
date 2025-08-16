import os
import sys
from dotenv import load_dotenv
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# --- 1. MEMUAT KONFIGURASI ---
print("Memuat konfigurasi dari file .env...")
load_dotenv()

# Ambil nilai dari environment variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')
SOURCE_STR = os.getenv('SOURCE_CHANNEL')
DEST_STR = os.getenv('DESTINATION_CHANNEL')
NOTIF_STR = os.getenv('NOTIFICATION_CHAT_ID')

# --- 2. VALIDASI KONFIGURASI ---
# Pastikan variabel penting tidak kosong
required_vars = {
    "API_ID": API_ID,
    "API_HASH": API_HASH,
    "SESSION_STRING": SESSION_STRING,
    "SOURCE_CHANNEL": SOURCE_STR,
    "DESTINATION_CHANNEL": DEST_STR,
    "NOTIFICATION_CHAT_ID": NOTIF_STR
}

missing_vars = [name for name, value in required_vars.items() if value is None]

if missing_vars:
    print(f"Error: Variabel environment berikut tidak ditemukan atau kosong: {', '.join(missing_vars)}")
    print("Harap periksa file .env Anda.")
    sys.exit(1)

# --- 3. KONVERSI TIPE DATA ---
# Telethon membutuhkan ID dalam bentuk integer. Jika bukan angka, diasumsikan username.
def parse_entity(entity_str):
    try:
        return int(entity_str)
    except (ValueError, TypeError):
        return entity_str

SOURCE_CHANNEL = parse_entity(SOURCE_STR)
DESTINATION_CHANNEL = parse_entity(DEST_STR)
NOTIFICATION_CHAT_ID = parse_entity(NOTIF_STR)

print("Konfigurasi berhasil dimuat.")

# --- 4. INISIALISASI KLIEN TELETHON ---
from telethon.sessions import StringSession

client = TelegramClient(
    StringSession(SESSION_STRING),
    int(API_ID),
    API_HASH
)

# --- 5. LOGIKA UTAMA BOT ---
# --- 5. LOGIKA UTAMA BOT ---
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handle_new_message(event):
    """Handler untuk pesan baru di channel sumber, dengan logika retry."""
    message = event.message

    # Sesuai permintaan: hanya proses pesan yang memiliki media.
    if message.media:
        print(f"Media terdeteksi di pesan ID {message.id}, mencoba menyalin...")

        # Loop untuk mencoba kembali jika terjadi FloodWaitError
        while True:
            try:
                await client.send_message(
                    entity=DESTINATION_CHANNEL,
                    message=message.text,  # Ini adalah caption
                    file=message.media
                )
                print(f"Pesan ID {message.id} berhasil disalin.")
                break  # Keluar dari loop jika berhasil
            except FloodWaitError as e:
                print(f"Terkena FloodWaitError. Menunggu selama {e.seconds} detik...")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"Gagal menyalin pesan ID {message.id} karena error lain: {e}")
                break  # Hentikan percobaan untuk pesan ini jika error lain terjadi

async def main():
    """Fungsi utama untuk menjalankan bot, dengan penanganan error."""
    try:
        await client.start()
        print("Bot berhasil terhubung dan siap memantau pesan.")
        print(f"Memantau channel/grup: {SOURCE_CHANNEL}")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Terjadi error kritis yang tidak terduga: {e}")
        print("Mencoba mengirim notifikasi error sebelum berhenti...")

        # Loop untuk mencoba kembali mengirim notifikasi jika terjadi FloodWaitError
        while True:
            try:
                # Pastikan client terhubung untuk bisa mengirim pesan notifikasi
                if not client.is_connected():
                    await client.connect()

                await client.send_message(
                    entity=NOTIFICATION_CHAT_ID,
                    message=f"**PEMBERITAHUAN: BOT BERHENTI**\n\n"
                            f"Bot pemantau channel berhenti karena mengalami error kritis.\n\n"
                            f"**Detail Error:**\n`{type(e).__name__}: {e}`"
                )
                print("Notifikasi error berhasil dikirim.")
                break  # Keluar dari loop jika berhasil
            except FloodWaitError as fe:
                print(f"Gagal mengirim notifikasi karena FloodWaitError. Menunggu {fe.seconds} detik...")
                await asyncio.sleep(fe.seconds)
            except Exception as notif_e:
                print(f"Gagal total mengirim notifikasi error. Error notifikasi: {notif_e}")
                break  # Gagal karena error lain, keluar dari loop
    finally:
        if client.is_connected():
            await client.disconnect()
        print("Koneksi bot telah ditutup. Program berhenti.")
        # sys.exit(0) akan menghentikan program

if __name__ == "__main__":
    print("Menjalankan bot...")
    # Menggunakan loop dari client untuk menjalankan fungsi main
    with client:
        client.loop.run_until_complete(main())
    print("Program selesai.")

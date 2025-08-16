import os
import sys
from dotenv import load_dotenv
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.tl import types

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
def format_caption(message, chat, sender):
    """Membangun caption baru yang informatif."""
    original_caption = message.text or ""

    # Info Sumber
    source_name = chat.title
    if chat.username:
        source_link = f"https://t.me/{chat.username}"
        source_info = f"[{source_name}]({source_link})"
    else:
        source_info = source_name

    # Info Pengirim
    sender_info = "N/A"
    if sender:
        if isinstance(sender, types.User):
            sender_name = sender.first_name
            if sender.last_name:
                sender_name += f" {sender.last_name}"
            # Buat deep link ke profil pengguna
            sender_info = f"[{sender_name}](tg://user?id={sender.id})"
        elif isinstance(sender, types.Channel):
            sender_info = sender.title

    # Info Waktu (dalam UTC)
    timestamp = message.date.strftime("%d %b %Y, %H:%M:%S UTC")

    # Link Pesan Asli
    if chat.username:
        message_link = f"https://t.me/{chat.username}/{message.id}"
    else:
        # Untuk chat privat, ID perlu sedikit diubah
        chat_id_str = str(message.chat_id).replace("-100", "", 1)
        message_link = f"https://t.me/c/{chat_id_str}/{message.id}"

    # Gabungkan semua informasi
    additional_info = (
        f"\n\n― ― ― ― ― ― ― ― ― ―\n"
        f"**Sumber:** {source_info}\n"
        f"**Pengirim:** {sender_info}\n"
        f"**Waktu:** {timestamp}\n"
        f"**Tautan Asli:** [Klik di sini]({message_link})"
    )

    return original_caption + additional_info

# --- 5. LOGIKA UTAMA BOT ---
@client.on(events.Album(chats=SOURCE_CHANNEL))
async def handle_album(event):
    """Handler untuk album media, dengan logika retry."""
    album_messages = event.messages
    # Ambil chat dan sender dari event
    chat = event.chat
    sender = event.sender
    # Gunakan pesan pertama sebagai referensi untuk caption
    reference_message = album_messages[0]

    # Buat caption baru yang informatif
    new_caption = format_caption(reference_message, chat, sender)

    print(f"Album terdeteksi dengan Group ID {reference_message.grouped_id}, berisi {len(album_messages)} media. Mencoba menyalin...")

    while True:
        try:
            await client.send_file(
                entity=DESTINATION_CHANNEL,
                file=[msg.media for msg in album_messages],
                caption=new_caption,
                parse_mode='md'  # Penting: untuk merender Markdown di caption
            )
            print(f"Album dengan Group ID {album_messages[0].grouped_id} berhasil disalin.")
            break
        except FloodWaitError as e:
            print(f"Terkena FloodWaitError saat menyalin album. Menunggu selama {e.seconds} detik...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Gagal menyalin album karena error lain: {e}")
            break

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handle_new_message(event):
    """Handler untuk pesan media tunggal, dengan logika retry."""
    message = event.message

    # Jika pesan adalah bagian dari album, abaikan. Sudah ditangani oleh handle_album.
    if message.grouped_id:
        return

    # Sesuai permintaan: hanya proses pesan yang memiliki media.
    if message.media:
        print(f"Media terdeteksi di pesan ID {message.id}, mencoba menyalin...")

        # Dapatkan info chat dan sender
        chat = event.chat
        sender = event.sender
        # Buat caption baru
        new_caption = format_caption(message, chat, sender)

        # Loop untuk mencoba kembali jika terjadi FloodWaitError
        while True:
            try:
                await client.send_message(
                    entity=DESTINATION_CHANNEL,
                    message=new_caption,
                    file=message.media,
                    parse_mode='md'
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

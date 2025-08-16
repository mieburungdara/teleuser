import os
import sys
from dotenv import load_dotenv
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
import re
from telethon.tl import types
from telethon.errors.rpcerrorlist import UserIsBlockedError
from asyncio.exceptions import TimeoutError

# --- 1. MEMUAT KONFIGURASI ---
print("Memuat konfigurasi dari file .env...")
load_dotenv()

# Ambil nilai dari environment variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')
# Variabel-variabel ini sekarang diatur secara interaktif
# SOURCE_STR = os.getenv('SOURCE_CHANNEL')
# HISTORY_START_ID_STR = os.getenv('HISTORY_START_ID')
DEST_STR = os.getenv('DESTINATION_CHANNEL')
NOTIF_STR = os.getenv('NOTIFICATION_CHAT_ID')

# --- 2. VALIDASI KONFIGURASI ---
# Pastikan variabel penting tidak kosong
required_vars = {
    "API_ID": API_ID,
    "API_HASH": API_HASH,
    "SESSION_STRING": SESSION_STRING,
    # "SOURCE_CHANNEL": SOURCE_STR, # Dihapus dari validasi
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

# SOURCE_CHANNEL = parse_entity(SOURCE_STR) # Logika lama
DESTINATION_CHANNEL = parse_entity(DEST_STR)
NOTIFICATION_CHAT_ID = parse_entity(NOTIF_STR)

# HISTORY_START_ID sekarang didapat secara interaktif
# HISTORY_START_ID = None
# if HISTORY_START_ID_STR and HISTORY_START_ID_STR.isdigit():
#     HISTORY_START_ID = int(HISTORY_START_ID_STR)
#     print(f"Mode Riwayat diaktifkan, mulai dari ID: {HISTORY_START_ID}")

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

# --- 5. FUNGSI PEMROSESAN INTI ---

async def process_single_message(message, chat, sender, client):
    """Memproses dan mengirim satu pesan media, termasuk retry."""
    new_caption = format_caption(message, chat, sender)
    print(f"Memproses media tunggal ID {message.id}...")
    while True:
        try:
            await client.send_message(
                entity=DESTINATION_CHANNEL,
                message=new_caption,
                file=message.media,
                parse_mode='md'
            )
            print(f"Pesan ID {message.id} berhasil disalin.")
            break
        except FloodWaitError as e:
            print(f"Terkena FloodWaitError pada pesan ID {message.id}. Menunggu {e.seconds} detik...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Gagal menyalin pesan ID {message.id} karena error: {e}")
            break

async def process_album(messages, chat, sender, client):
    """Memproses dan mengirim satu album media, termasuk retry."""
    reference_message = messages[0]
    new_caption = format_caption(reference_message, chat, sender)
    print(f"Memproses album Group ID {reference_message.grouped_id}...")
    while True:
        try:
            await client.send_file(
                entity=DESTINATION_CHANNEL,
                file=[msg.media for msg in messages],
                caption=new_caption,
                parse_mode='md'
            )
            print(f"Album Group ID {reference_message.grouped_id} berhasil disalin.")
            break
        except FloodWaitError as e:
            print(f"Terkena FloodWaitError pada album Group ID {reference_message.grouped_id}. Menunggu {e.seconds} detik...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Gagal menyalin album Group ID {reference_message.grouped_id} karena error: {e}")
            break

# --- 6. EVENT HANDLER REAL-TIME ---
async def handle_album(event):
    """Handler untuk album media. Meneruskan event ke fungsi proses."""
    print(f"Event Album terdeteksi (Group ID: {event.grouped_id})")
    await process_album(event.messages, event.chat, event.sender, client)

async def handle_new_message(event):
    """Handler untuk pesan media tunggal. Meneruskan event ke fungsi proses."""
    message = event.message
    # Abaikan pesan yang merupakan bagian dari album.
    if message.grouped_id:
        return
    # Abaikan pesan tanpa media.
    if not message.media:
        return

    print(f"Event Pesan Baru terdeteksi (ID: {message.id})")
    await process_single_message(message, event.chat, event.sender, client)

# --- 7. MODE RIWAYAT ---

async def run_scrape_pass(min_id, client, entity, processed_group_ids):
    """Menjalankan satu pass scraping dan memproses pesan."""
    last_id = min_id
    async for message in client.iter_messages(entity, min_id=min_id, reverse=True):
        last_id = message.id
        if not message.media:
            continue

        sender = await message.get_sender() # Perlu untuk info pengirim

        if message.grouped_id:
            if message.grouped_id in processed_group_ids:
                continue
            processed_group_ids.add(message.grouped_id)
            album_messages = await client.get_messages(entity, grouped_id=message.grouped_id)
            if album_messages:
                await process_album(album_messages, entity, sender, client)
        else:
            await process_single_message(message, entity, sender, client)
    return last_id

async def scrape_history(client, source_entity, start_id):
    """Menyalin riwayat pesan dari ID awal yang diberikan."""
    print("--- MEMULAI MODE RIWAYAT ---")
    try:
        last_known_id = start_id - 1
        processed_group_ids = set()

        while True:
            print(f"\nMemulai pass pengejaran dari ID: {last_known_id + 1}")
            latest_messages = await client.get_messages(entity, limit=1)
            if not latest_messages:
                print("Channel tampak kosong. Mengakhiri mode riwayat.")
                break

            current_latest_id = latest_messages[0].id
            if current_latest_id <= last_known_id:
                print("Sudah sinkron. Tidak ada pesan baru untuk pass ini.")
                break

            print(f"Menyalin pesan dari ID {last_known_id + 1} hingga {current_latest_id}...")
            last_known_id = await run_scrape_pass(last_known_id, client, entity, processed_group_ids)

        print("\nSinkronisasi awal selesai. Menunggu 5 detik untuk 'settling'...")
        await asyncio.sleep(5)

        print("Melakukan satu pemeriksaan terakhir...")
        final_pass_last_id = await run_scrape_pass(last_known_id, client, entity, processed_group_ids)
        if final_pass_last_id > last_known_id:
            print("Sisa pesan berhasil disalin.")
        else:
            print("Tidak ada pesan baru yang ditemukan.")

    except Exception as e:
        print(f"Terjadi error selama mode riwayat: {e}")

    print("--- MODE RIWAYAT SELESAI ---")


# --- 8. FUNGSI UTAMA & ALUR KERJA ---
async def main():
    """Fungsi utama yang menjalankan seluruh alur kerja bot secara interaktif."""

    print("Menjalankan bot...")
    # Menghubungkan client di dalam blok with untuk memastikan diskoneksi yang aman
    async with client:
        print("Bot berhasil terhubung.")

        # Memuat dialog untuk "memanaskan" cache entitas dan mencegah error
        print("Memuat dialog untuk caching entitas...")
        async for _ in client.iter_dialogs():
            pass
        print("Dialogs berhasil di-cache.")

        # 1. Mulai percakapan interaktif dengan admin
        source_channel_id = None
        start_message_id = None
        try:
            admin_entity = await client.get_entity(NOTIFICATION_CHAT_ID)
            print(f"Mengirim permintaan ke admin ({admin_entity.id}) untuk instruksi...")
            async with client.conversation(admin_entity, timeout=300) as conv:
                await conv.send_message(
                    "Bot siap. Silakan kirim link dari pesan awal yang ingin disalin.\n"
                    "Contoh: `https://t.me/c/1234567890/500`"
                )

                response = await conv.get_response()

                # 2. Parsing link dari admin
                link_pattern = re.compile(r"t\.me/c/(\d+)/(\d+)")
                match = link_pattern.search(response.text)

                if not match:
                    await conv.send_message("Format link tidak valid. Harap berikan link yang benar. Bot berhenti.")
                    return

                channel_id_str, start_message_id_str = match.groups()
                source_channel_id = int("-100" + channel_id_str)
                start_message_id = int(start_message_id_str)

                await conv.send_message(
                    f"Instruksi diterima. Menyalin dari Channel ID: `{source_channel_id}` "
                    f"mulai dari Pesan ID: `{start_message_id}`."
                )

        except TimeoutError:
            print("Waktu habis menunggu input dari admin. Bot berhenti.")
            return
        except UserIsBlockedError:
            print("Bot diblokir oleh admin, tidak bisa mengirim permintaan. Bot berhenti.")
            return
        except Exception as e:
            print(f"Terjadi error tak terduga saat setup interaktif: {e}. Bot berhenti.")
            return

        # 3. Pendaftaran handler dinamis
        print(f"Mendaftarkan event handler untuk channel: {source_channel_id}")
        client.add_event_handler(handle_album, events.Album(chats=source_channel_id))
        client.add_event_handler(handle_new_message, events.NewMessage(chats=source_channel_id))

        # 4. Jalankan mode riwayat
        try:
            source_entity = await client.get_entity(source_channel_id)
            await scrape_history(client, source_entity, start_message_id)
        except Exception as e:
            print(f"Gagal total saat menjalankan mode riwayat: {e}")

        # 5. Jalankan mode real-time
        print(f"\n--- MEMULAI MODE REAL-TIME ---")
        print(f"Memantau pesan baru di channel/grup: {source_channel_id}")
        print("Bot sekarang berjalan dalam mode real-time. Tekan Ctrl+C untuk berhenti.")
        await client.run_until_disconnected()

if __name__ == "__main__":
    # Menjalankan loop event asyncio untuk fungsi main
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot dihentikan oleh pengguna.")
    finally:
        print("Program selesai.")

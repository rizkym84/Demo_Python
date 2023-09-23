import imaplib
import email
from email.header import decode_header
import pymongo
import logging
import re

# Konfigurasi logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

# Fungsi untuk mendekode judul email
def decode_subject(subject):
    decoded_parts = decode_header(subject)
    decoded_subject = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_subject += part.decode(encoding or 'utf-8')
        else:
            decoded_subject += part
    return decoded_subject

# Fungsi untuk mendapatkan tanggal dari email
def extract_date_from_email(email_message):
    date = email_message["Date"]
    return date

# Fungsi untuk mengekstrak data dari tubuh email
def extract_data_from_body(body):
    # Ekstrak data dari Body email
    # Ekstrak nomor klaim sebagai contoh
    claim_number = re.search(r"Nomor Klaim: (\d+)", body)
    if claim_number:
        return claim_number.group(1)
    else:
        return None

# Fungsi untuk menyimpan data ke MongoDB
def save_to_mongodb(data):
    try:
        client = pymongo.MongoClient("")
        db = client["klaim_asuransi"]
        collection = db["data_klaim"]
        collection.insert_one(data)
    except Exception as e:
        logging.error(f"Error saving data to MongoDB: {str(e)}")

# Konfigurasi email
email_user = "rpa_demo@digitaloptima.id"
email_pass = ")emhY3pOwp{W"
imap_server = "mail.digitaloptima.id"
imap_port = 993  # Port IMAP SSL

# Buat koneksi ke server email
try:
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
    mail.login(email_user, email_pass)
    mail.select("inbox")

    # Cari email dengan subjek tertentu
    search_criteria = '(SUBJECT "Klaim Asuransi")'
    status, email_ids = mail.search(None, search_criteria)

    email_ids = email_ids[0].split()

    # Loop melalui email yang cocok dengan kriteria pencarian
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")

        if status == "OK":
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Ekstrak data yang dibutuhkan dari email
            sender = email_message["From"]
            subject = decode_subject(email_message["Subject"])
            date = extract_date_from_email(email_message)
            body = ""

            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8")
                        break
            
            # Ekstrak data tambahan dari tubuh email
            additional_data = extract_data_from_body(body)
            
            # Simpan data ke MongoDB
            data = {
                "Sender": sender,
                "Subject": subject,
                "Date": date,
                "Body": body,
                "AdditionalData": additional_data
            }
            save_to_mongodb(data)

except Exception as e:
    logging.error(f"An error occurred: {str(e)}")

finally:
    try:
        mail.logout()
    except Exception as e:
        logging.error(f"Error while logging out from email server: {str(e)}")

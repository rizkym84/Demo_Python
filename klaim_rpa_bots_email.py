import tempfile
import os
import re
import logging
import pymongo
from email.header import decode_header
import email
import imaplib

# Konfigurasi logging -Ricky
logging.basicConfig(filename='error.log', level=logging.ERROR)

# Fungsi untuk mendekode judul email -Ricky
def decode_subject(subject):
    decoded_parts = decode_header(subject)
    decoded_subject = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_subject += part.decode(encoding or 'utf-8')
        else:
            decoded_subject += part
    return decoded_subject

# Fungsi untuk mendapatkan tanggal dari email -Ricky
def extract_date_from_email(email_message):
    date = email_message["Date"]
    return date

# Fungsi untuk mengekstrak data dari tubuh email -Ricky
def extract_data_from_body(body):
    # Ekstrak data dari Body email -Ricky
    # Ekstrak nomor klaim sebagai contoh -Ricky
    claim_number = re.search(r"Nomor Klaim: (\d+)", body)
    if claim_number:
        return claim_number.group(1)
    else:
        return None

# Fungsi untuk menyimpan data ke MongoDB -Ricky Isi Koneksi MongoDB anda -Ricky
def save_to_mongodb(data):
    try:
        client = pymongo.MongoClient("")
        db = client["klaim_asuransi"]
        collection = db["data_klaim"]
        collection.insert_one(data)
    except Exception as e:
        logging.error(f"Error saving data to MongoDB: {str(e)}")

# Fungsi untuk mengekstrak data dari attachment -Ricky
def process_email(email_body):
    # Define regular expressions to match the parameter values -Ricky
    claim_number_pattern = r"No Klaim: (\w+)"
    amount_pattern = r"amount: ([\d.]+)"
    date_pattern = r"transaction_date: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
    merchant_id_pattern = r"merchant_id: ([\w=]+)"
    sub_type_pattern = r"subType: (\d+)"
    transaction_type_pattern = r"transaction_type: (\w+)"
    location_pattern = r"location: (.+)"

    # Extract parameter values using regular expressions -Yundi
    claim_number = re.search(claim_number_pattern, email_body).group(1)
    amount = re.search(amount_pattern, email_body).group(1)
    transaction_date = re.search(date_pattern, email_body).group(1)
    merchant_id = re.search(merchant_id_pattern, email_body).group(1)
    sub_type = re.search(sub_type_pattern, email_body).group(1)
    transaction_type = re.search(transaction_type_pattern, email_body).group(1)
    location = re.search(location_pattern, email_body).group(1)

    document = {
        'claim_number': claim_number,
        'amount': float(amount),
        'transaction_date': transaction_date,
        'merchant_id': merchant_id,
        'sub_type': int(sub_type),
        'transaction_type': transaction_type,
        'location': location
    }

    return document

def extract_data_from_attachment(part):
    try:
        temp_dir = tempfile.mkdtemp()
        attachment_filename = part.get_filename()
        if attachment_filename:
            file_path = os.path.join(temp_dir, attachment_filename)
            with open(file_path, "wb") as file:
                file.write(part.get_payload(decode=True))

            # Process the attachment data here as needed
            # For example, you can parse a CSV file or extract text from a document

            # Don't forget to remove the temporary directory and file when done
            os.remove(file_path)
            os.rmdir(temp_dir)
    except Exception as e:
        logging.error(f"Error extracting data from attachment: {str(e)}")

# Konfigurasi email ganti dengan akun email password anda -Ricky
email_user = "rpa_demo@digitaloptima.id"
email_pass = ""
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
                    elif part.get_content_type() == "application/octet-stream":
                        # Ekstrak data dari attachment
                        extract_data_from_attachment(part)

            # Ekstrak data tambahan dari tubuh email
            additional_data = extract_data_from_body(body)

            dataprocess = process_email(body)

            # Simpan data ke MongoDB
            data = {
                "Sender": sender,
                "Subject": subject,
                "Date": date,
                "Body": body,
                "AdditionalData": additional_data,
                "dataprocess": dataprocess
            }
            save_to_mongodb(data)

except Exception as e:
    logging.error(f"An error occurred: {str(e)}")

finally:
    try:
        mail.logout()
    except Exception as e:
        logging.error("Error while logging out from email server: " + str(e))

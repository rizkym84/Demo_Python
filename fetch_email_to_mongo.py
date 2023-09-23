import imaplib
import email
import pymongo


# Konfigurasi email
email_address = "rpa_demo@digitaloptima.id"
password = ")emhY3pOwp{W"


# IMAP server settings (for Gmail)
imap_server = "mail.digitaloptima.id"
imap_port = 993  # Port IMAP SSL

# MongoDB settings
mongodb_uri = "mongodb://localhost:27017/"
database_name = "rpa_sample"
collection_name = "emails"

# Connect to MongoDB
client = pymongo.MongoClient(mongodb_uri)
db = client[database_name]
collection = db[collection_name]


def connect_to_imap_server():
    try:
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)

        # Login to the email account
        mail.login(email_address, password)

        # Select the mailbox you want to fetch emails from (e.g., "inbox")
        mailbox = "inbox"
        mail.select(mailbox)

        return mail
    except Exception as e:
        print("Error connecting to the IMAP server:", e)
        return None


def fetch_and_push_emails(mail):
    try:
        # Search for all emails in the selected mailbox
        status, email_ids = mail.search(None, "ALL")

        if status == "OK":
            email_ids = email_ids[0].split()
            for email_id in email_ids:
                # Fetch the email by ID
                status, email_data = mail.fetch(email_id, "(RFC822)")

                if status == "OK":
                    raw_email = email_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Extract email details
                    subject = msg["Subject"]
                    date = msg["Date"]
                    body = ""
                    sender = msg["From"]

                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                body = part.get_payload(
                                    decode=True).decode("utf-8")
                                break

                    # Insert email data into MongoDB
                    email_doc = {
                        "subject": subject,
                        "date": date,
                        "body": body,
                        "sender": sender
                    }
                    collection.insert_one(email_doc)

                    print("Email inserted into MongoDB:", subject)
        else:
            print("No emails found.")
    except Exception as e:
        print("Error fetching and pushing emails:", e)


if __name__ == "__main__":
    mail_connection = connect_to_imap_server()

    if mail_connection:
        fetch_and_push_emails(mail_connection)
        mail_connection.logout()

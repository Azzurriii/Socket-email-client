from pop3_client import POP3_Client as Pop3MailClient
import sqlite3
import re
import json
import time

class DatabaseManager:
    def __init__(self):
        self.config = json.load(open('config.json'))

    def get_email_type(self, email_sender, email_subject, email_content):
        if (re.search(r'@([^.]+)', email_sender).group(1) == "testing"):
            return "PROJECT"
        
        if any(keyword.upper() in email_subject.upper() for keyword in ["urgent", "ASAP"]):
            return "IMPORTANT"
        
        if any(keyword.upper() in email_content.upper() for keyword in ["roport", "meeting"]):
            return "WORK"
        
        if any(keyword.upper() in text.upper() for keyword in ["virus", "hack", "crack"] for text in [email_subject, email_content]):
            return "SPAM"
        
        return "INBOX"

    def update_base(self):
        mail_getter = Pop3MailClient(
            email=re.search(r'<([^>]*)>', self.config["General"]["Username"]).group(1), 
            password=self.config["General"]["Password"],
            server_name=self.config["General"]["MailServer"],
            server_port=self.config["General"]["POP3"]
        )

        mail_getter.connectingServer()
        mail_getter.cmd_USER()
        mail_getter.cmd_PASS()
        mail_getter.cmd_STAT()
        mail_getter.cmd_LIST()
        mail_getter.cmd_receive_mail()
        mail_getter.cmd_receive_mail_information()
        mail_getter.cmd_DELE()
        mail_getter.cmd_QUIT()

        mail_list = [(
            0,
            self.get_email_type(mail_getter.mail_from[i], mail_getter.mail_subject[i], mail_getter.mail_content[i]),
            mail_getter.client_email,
            mail_getter.mail_from[i],
            mail_getter.mail_subject[i],
            mail_getter.mail_content[i],
            mail_getter.attach_file_dir[i]
        ) for i in range(mail_getter.message_count)]
        
        conn = sqlite3.connect("email_database.db")
        cursor = conn.cursor()

        cursor.executemany("INSERT INTO received_emails (email_status, email_type, email_client, email_sender, email_subject, email_content, email_attach_dir) VALUES (?,?,?,?,?,?,?)", mail_list)        
        cursor.execute("SELECT * FROM received_emails")

        conn.commit()

        conn.close()
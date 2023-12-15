import msvcrt
import json
import re
import os
import sqlite3
from smtp_client import MailSender as SmtpMailClient 
import textwrap
from update_database import DatabaseManager
import shutil
import threading
import getpass

#Sending email with SMTP
class ConsoleMailClient:
    def __init__(self):
        with open('config.json', encoding='utf-8') as f:
            self.config = json.load(f)
        self.current_folder = None
        self.smtp_client = None
        self.email_address = None

    def login(self):
        match = re.match(r"(.+?) <(.*?)>", self.config['General']['Username'])
        if match:
            name, self.email_address = match.groups()
        else:
            print("Không thể đọc thông tin từ config.json")
            name, self.email_address = "", ""
        if name and self.email_address:
            greeting_message = f"Xin chào, {name} <{self.email_address}>"
            print(greeting_message)
        else:
            print("Thông tin đăng nhập không tồn tại.")
        while True:
            entered_password = getpass.getpass("Nhập mật khẩu: ")
            correct_password = self.config['General']['Password']

            if entered_password == correct_password:
                print("Đăng nhập thành công.")
                break
            else:
                print("Mật khẩu không đúng. Vui lòng thử lại.")

            
        input("- Nhấn [Enter] để tiếp tục -")


    def display_menu(self):
        os.system("cls")
        print("--- MENU ---")
        print("1. Gửi email")
        print("2. Xem danh sách các email đã nhận")
        print("3. Thoát")
        print("Vui lòng nhập lựa chọn của bạn:")

    def validate_email(self, email):
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.match(regex, email)
    

    def send_email(self):
        to, cc, bcc = "", "", ""

        to = list(map(str.strip, input("To: ").split(',')))
        cc = list(map(str.strip, input("CC: ").split(',')))
        bcc = list(map(str.strip, input("BCC: ").split(',')))
        subject = input("Subject: ")

        email_client = SmtpMailClient(
            server_name=self.config['General']['MailServer'],
            server_port=int(self.config['General']['SMTP']),
            addr_from=self.email_address,
            addr_to=to,
            addr_cc=cc,
            addr_bcc=bcc,
            content_subject=subject,
            content_main="",  # Initialize content_main as an empty string
            content_dir_attachment=[]
        )

        # Prompt the user to enter the email content
        print("Nhập nội dung email: (Nhập 'end' ở dòng cuối để kết thúc)")
        content_lines = []
        while True:
            line = input()
            if line.lower() == 'end':
                break
            content_lines.append(line)

        email_client.content_main = '\r\n'.join(content_lines)

        send_option = input("Bạn có muốn gửi email kèm attachment không? (1. Có, 2. Không): ")

        if send_option == "1":
            attachments = []
            num_attachments = int(input("Số lượng file muốn gửi: "))

            for i in range(num_attachments):
                while True:
                    curr_file_dir = input(f"Cho biết đường dẫn file thứ {i + 1}: ")
                    if os.path.exists(curr_file_dir) and os.path.getsize(curr_file_dir) <= 3 * 1024 * 1024:
                        attachments.append(curr_file_dir)
                        print("Đã thêm file thành công.")
                        break
                    else:
                        print("Dung lượng file đính kèm vượt quá giới hạn hoặc file không tồn tại.")
                        choice = input("Bạn có muốn chọn file khác không? (1. Có, 2. Không): ")
                        if choice == "2":
                            break 

            if attachments:
                email_client.content_dir_attachment = attachments

        # Gửi email
        if (email_client.cmd_init_smtp_server() and email_client.cmd_send_email_addresses() and email_client.cmd_send_email_content()):
            print("Đã gửi email thành công")
        else:
            print("Gửi email thất bại.")

        email_client.cmd_close_smtp_server()        

    def format_emails_thumbnails(self, emails):
        emails_thumbnails = []

        for i in range(len(emails)):
            email_thumbnail = str(i + 1) + ". "
            email_thumbnail += "[Chưa Đọc] " if emails[i][1] == 0 else "";
            email_thumbnail += f"{emails[i][4]}: {emails[i][5]}"
            emails_thumbnails.append(email_thumbnail)

        return emails_thumbnails

    def view_email(self):
        keywords = ["INBOX", "PROJECT", "IMPORTANT", "WORK", "SPAM"]
        
        user_input = ""
        option = 0

        while True:
            os.system("cls")

            for i in range(len(keywords)):
                print(f"{i + 1}. {keywords[i]}")

            user_input = input("Nhập lựa chọn của bạn:")
            
            if user_input.isdigit():
                option = int(user_input)

                if 1 <= option <= len(keywords):
                    break
            
            print("Lựa chọn không hợp lệ! Xin nhập lại!")

        email_type = keywords[option - 1]
        conn = sqlite3.connect("email_database.db")
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM received_emails WHERE email_client = ? AND email_type == ? AND email_status == 0", (self.email_address, email_type,))
        email_list = cursor.fetchall()
        cursor.execute(f"SELECT * FROM received_emails WHERE email_client = ? AND email_type == ? AND email_status == 1", (self.email_address,  email_type,))
        email_list += cursor.fetchall()

        while True:
            os.system("cls")
            print(f"-- {email_type} --")
            print("\r\n".join(self.format_emails_thumbnails(email_list)))

            user_input = input("Lựa chọn email muốn xem. Nhập 0 nếu muốn thoát ra menu: ")
            
            if user_input.isdigit():
                option = int(user_input)

                if 1 <= option <= len(email_list):
                    self.read_email_content(email_list[option - 1])
                    
                    cursor.execute('''
                        UPDATE received_emails
                        SET email_status = ?
                        WHERE id == ?
                    ''', (1, email_list[option - 1][0],))
                    
                    conn.commit()
                    break
                elif option == 0:
                    break                
                else:
                    print("Lựa chọn không hợp lệ! Xin lựa chọn lại!")

        conn.close()

    def read_email_content(self, email):
        LINE_WIDTH = 100
        textwrap_format = textwrap.TextWrapper(width=LINE_WIDTH, break_long_words=False, replace_whitespace=False)
        
        print(f"EMAIL {'-' * (LINE_WIDTH - 6)}")
        print(f"From: {email[4]}")
        print("Subject:"+ '\n'.join(textwrap_format.wrap(email[5])))
        print("Content:\r\n"+ '\n'.join(textwrap_format.wrap(email[6])))
        print(f"{'-' * LINE_WIDTH}")
        
        if (email[7] != ""):
            attachments_list = email[7].split(sep=",")
            print(f"Hiện tại đang có {len(attachments_list)} tệp đính kèm trong email.")
            print("Với mỗi file, nhập [Y] để tải về, [N] để bỏ qua")
            for i in range(len(attachments_list)):
                print(f"{i + 1}. {attachments_list[i]}")
                
                option = ""
                while (option.upper() not in ["Y", "N"]):
                    option = input("Bạn có muốn tải về file đính kèm này?\r\n>> ")

                if (option.upper() == "N"):
                    continue
                else:
                    option_path = ""
                    while True:
                        print("Nhập đường dẫn. Để trống nếu muốn bỏ qua tệp.")
                        option_path = input(">> ")

                        if os.path.exists(option_path):
                            shutil.copy2(attachments_list[i], option_path.rstrip('\\') + "\\" + os.path.basename(attachments_list[i]))
                            break
                        elif option_path.strip() == "":
                            break
                        else:
                            print("Lựa chọn không hợp lệ! Xin chọn lại!")
                        
                    input("- Nhấn [Enter] để tiếp tục -")
                    
        option_path = ""
        while option_path.upper() not in ["Y", "N"]:
            option_path = input("Bạn có muốn đổi phân loại của mail? [Y] / [N]\r\n>> ")

        if (option_path.upper() == "Y"):
            print("Chọn phân loại theo số thứ tự:")
            keywords = ["INBOX", "PROJECT", "IMPORTANT", "WORK", "SPAM"]
            
            for i in range(len(keywords)):
                print(f"{i + 1}. {keywords[i]}")

            option_path = ""
            while (not option_path.isdigit() or not 1 <= int(option_path) <= len(keywords)):
                option_path = input(">> ")

            conn = sqlite3.connect("email_database.db")
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE received_emails
                SET email_type = ?
                WHERE id == ?
            ''', (keywords[int(option_path) - 1], email[0],))
            
            conn.commit()
            conn.close()

    def init_database(self):
        conn = sqlite3.connect("email_database.db")

        cursor = conn.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS received_emails (
            id INTEGER PRIMARY KEY,
            email_status INTEGER,
            email_type TEXT,
            email_client text,
            email_sender text,
            email_subject text,
            email_content text,
            email_attach_dir text
        )""")

        conn.commit()
        conn.close()

        if not os.path.exists("AttachmentFiles"):
            os.makedirs("AttachmentFiles")

    def run_database(self):
        thread = threading.Timer(self.config["General"]["Autoload"], self.run_database, [])
        thread.daemon = True
        thread.start()
        
        database_instance = DatabaseManager()
        database_instance.update_base()

    def run(self): 
        self.login()
        self.init_database()
        self.run_database()

        while True:
            self.display_menu()
            choice = input("Bạn chọn: ")

            if choice == "1":
                self.send_email()
            elif choice == "2":
                # Implement viewing emails
                self.view_email()
            elif choice == "3":
                print("Thoát chương trình. Tạm biệt.")
                break
            else:
                print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

            input("- Nhấn [Enter] để tiếp tục -")

    #Receiving email with POP3

if __name__ == "__main__":
    console_mail_client = ConsoleMailClient()
    console_mail_client.run()
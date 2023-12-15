import socket
import os
import re
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.message import EmailMessage
from email import policy

class POP3_Client:
    def __init__(self, email, password, server_name, server_port):
        self.client_email = email
        self.client_password = password
        self.server_name = server_name
        self.server_port = server_port
        self.message_count = 0
        self.mail = []
        self.mail_from = []
        self.mail_subject = []
        self.mail_content = []
        self.attach_file_dir = []
        self.mail_type = []
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __del__(self):
        self.client_socket.close()

    def connectingServer(self):
        self.client_socket.connect((self.server_name, self.server_port))

        return self.checkServerResponse()

    def checkServerResponse(self):
        return (self.client_socket.recv(1024).decode()[:3] == "+OK")

    def cmd_CAPA(self):
        self.client_socket.send("CAPA\r\n".encode())
        return self.checkServerResponse()

    def cmd_USER(self):
        self.client_socket.send(f"USER {self.client_email}\r\n".encode())
        return self.checkServerResponse()

    def cmd_PASS(self):
        self.client_socket.send(f"PASS {self.client_email}\r\n".encode())
        return self.checkServerResponse()

    def cmd_STAT(self):
        self.client_socket.send("STAT\r\n".encode())
        # Lấy số mail nhận được của mail này
        self.message_count = int(re.compile(r'\s(\S+)\s').findall(self.client_socket.recv(1024).decode())[0])

    def cmd_LIST(self):
        self.client_socket.send("LIST\r\n".encode())
        return self.checkServerResponse()

    def cmd_UIDL(self):
        self.client_socket.send("UIDL\r\n".encode())
        return self.checkServerResponse()

    def cmd_QUIT(self):
        self.client_socket.send("QUIT\r\n".encode())
        return self.checkServerResponse()

    def cmd_DELE(self):
        i = 0
        while (i < self.message_count):
            self.client_socket.send(f"DELE {i + 1}\r\n".encode())
            self.client_socket.recv(1024)
            i += 1

    def cmd_receive_data(self):
        raw_data = b''
        while True:
            chunk = self.client_socket.recv(1024)
            raw_data += chunk
            if b'\r\n.\r\n' in raw_data:
                break
        return re.sub(r'^.*?\r\n', '', raw_data.decode())

    def cmd_receive_mail(self):
        # Lấy thông tin mail từ server và day vao 1 list
        for curr_count in range(self.message_count):
            self.client_socket.send(f"RETR {curr_count + 1}\r\n".encode())
            self.mail.append(self.cmd_receive_data())

    def containsContent(self,part):
        return (part.get_content_type() == 'text/plain' and part.get("Content-Disposition") == None)

    def containtFiles(self,part):
        return (part.get("Content-Disposition"))

    def receive_mail_header(self,msg):
        if msg.get('USER-Agent'):
            self.mail_from.append(re.search(r'<(.*?)>', msg['From']).group(1))
        else:
            self.mail_from.append(msg['From'])
        self.mail_subject.append(msg['Subject'])

    def receive_mail_content(self,part):
        temp = part.get_payload().strip(' ')
        self.mail_content.append(temp.strip("\r\n\r\n.\r\n"))

    def download_files(self,part,file_dirs):
        file_basename = f"{os.getcwd()}\\AttachmentFiles\\{part.get_filename()}"
        if (os.path.exists(file_basename)):
            copy_cnt = 1
            file_name, file_extension = os.path.splitext(os.path.split(file_basename)[1])
            while (os.path.exists(f"{os.getcwd()}\\AttachmentFiles\\{file_name}_{copy_cnt}{file_extension}")):
                copy_cnt += 1

            file_basename = f"{os.getcwd()}\\AttachmentFiles\\{file_name}_{copy_cnt}{file_extension}"
        
        file_dirs.append(file_basename)

        with open(file_basename, "wb") as file:
            file.write(part.get_payload(decode=True))
        file.close()

    def cmd_receive_mail_information(self):
        try:
            for curr_mail in self.mail[:self.message_count]:
                msg = email.message_from_string(curr_mail, policy=policy.default)
                self.receive_mail_header(msg)

                if msg.is_multipart():
                    file_attach_dirs = []
                    for part in msg.walk():
                        if self.containsContent(part):
                            self.receive_mail_content(part)
                        elif self.containtFiles(part):
                            self.download_files(part,file_attach_dirs)
                    self.attach_file_dir.append(",".join(file_attach_dirs))
                else:
                    self.receive_mail_content(msg)
                    self.attach_file_dir.append('')

        except:
            print("Error!")

    def printMails(self):
        for i in range(self.message_count):
            print(self.mail_from[i])
            print(self.mail_subject[i])
            print(self.mail_content[i].encode())
            print(self.attach_file_dir[i])


# client_mail = POP3_Client(
#     email="nqthinh@hcmus.com",
#     server_name="127.0.0.1",
#     server_port=3335
# )

# client_mail.connectingServer()
# print(client_mail.cmd_USER())
# # print(client_mail.cmd_PASS())
# client_mail.cmd_STAT()
# print(client_mail.cmd_LIST())
# client_mail.cmd_receive_mail()
# client_mail.cmd_receive_mail_information()
# print(client_mail.attach_file_dir)
# # client_mail.cmd_DELE()
# client_mail.cmd_QUIT()
from socket import *
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import mimetypes
from email import encoders
import os

class MailSender:
    def __init__ (self, server_name = "127.0.0.1", server_port = 2225, addr_from = "", addr_to = [], addr_cc = [], addr_bcc = [], content_main = [], content_subject = [], content_dir_attachment = []):
        self.server_name = server_name
        self.server_port = server_port
        self.client_socket = socket(AF_INET, SOCK_STREAM)

        self.addr_from = addr_from
        self.addr_to = addr_to
        self.addr_cc = addr_cc
        self.addr_bcc = addr_bcc

        self.content_main = content_main
        self.content_subject = content_subject
        self.content_dir_attachment = content_dir_attachment

    def __del__(self):
        self.client_socket.close()

    def check_smtp_response(self, target_response) -> bool:
        try:
            return (int(self.client_socket.recv(1024).decode()[:3]) == target_response)
        except:
            return False
    
    def cmd_init_smtp_server(self) -> bool:
        try:
            self.client_socket.connect((self.server_name, self.server_port))
            if (self.check_smtp_response(220) == False):
                return False
            
            self.client_socket.send("HELO\r\n".encode())
            return self.check_smtp_response(250)
        except:
            return False

    def cmd_send_email_addresses(self) -> bool:
        try:
            self.client_socket.send(f"MAIL FROM:<{self.addr_from}>\r\n".encode())
            if (self.check_smtp_response(250) == False):
                return False            

            for recipient in self.addr_to:
                self.client_socket.send(f"RCPT TO:<{recipient}>\r\n".encode())
                if (self.check_smtp_response(250) == False):
                    return False
                
            for recipient in self.addr_cc:
                self.client_socket.send(f"RCPT TO:<{recipient}>\r\n".encode())
                if (self.check_smtp_response(250) == False):
                    return False

            for recipient in self.addr_bcc:
                self.client_socket.send(f"RCPT TO:<{recipient}>\r\n".encode())
                if (self.check_smtp_response(250) == False):
                    return False
                
            return True
        except:
            return False
        
    def email_mime_format(self):
        if (self.content_dir_attachment != []):
            message = MIMEMultipart()

            message["From"] = self.addr_from
            message["To"] = ",".join(self.addr_to)
            message["Cc"] = ",".join(self.addr_cc)

            message["Subject"] = self.content_subject
            message.attach(MIMEText(self.content_main, _subtype="plain"))

            for attachment_file_dir in self.content_dir_attachment:
                if (os.path.exists(attachment_file_dir) and os.path.getsize(attachment_file_dir)):
                    file_name = os.path.basename(attachment_file_dir)
                    # file_type = mimetypes.guess_type(file_name).split("/")

                    main_type, sub_type = mimetypes.guess_type(file_name)[0].split("/")
                    attachment = MIMEBase(main_type, sub_type)

                    attachment.set_payload(open(file_name, "rb").read())

                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        "Content-Disposition",
                        f"attachment; filename={file_name}",
                    )
                    message.attach(attachment)
            

        else:
            message = MIMEText(self.content_main, "plain")

            message["From"] = self.addr_from
            message["To"] = ",".join(self.addr_to)
            message["Cc"] = ",".join(self.addr_cc)

            message["Subject"] = self.content_subject

        return message.as_bytes()
    
    def cmd_send_email_content(self):
        try:
            self.client_socket.send("DATA\r\n".encode())
            if (self.check_smtp_response(354) == False):
                return False            

            self.client_socket.sendall(self.email_mime_format())
            self.client_socket.send("\r\n.\r\n".encode())

            return self.check_smtp_response(250)
        except:
            return False
        
    def cmd_close_smtp_server(self):
        try:
            self.client_socket.send("QUIT\r\n".encode())

            if (self.check_smtp_response(221) == False):
                return False

            self.client_socket.close()

            return True
        except:
            return False

client_email = MailSender(
    server_name="127.0.0.1",
    server_port=2225,
    addr_from="rockstargaming@gmail.com",
    addr_bcc=["nguyenphutrong@gmail.com"],
    content_subject="GTA 3 is coming out!",
    content_main="Give us your kidney stones and other things, so that the making of this game is complete!",
    content_dir_attachment=["pic1.jpg"]
)

if __name__ == "__main__":
    print(client_email.cmd_init_smtp_server())
    print(client_email.cmd_send_email_addresses())
    print(client_email.cmd_send_email_content())
    print(client_email.cmd_close_smtp_server())
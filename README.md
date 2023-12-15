# Email Client using SMTP and POP3

This project is a simple and lightweight email client that uses the SMTP and POP3 protocols to send and receive emails. It has a console-based interface that allows you to compose, view, and delete emails.
## Getting started
These instructions will help you set up and run the email client on your local machine.
## Prerequisites
You will need the following software to run the email client:

Java Runtime Environment (JRE) 8 or higher

Python 3.6 or higher
## Installation
1. Clone this repository to your local device using the command:
```
   git clone https://github.com/vtthanh04/smtp-pop3-email-client.git
```
2. Navigate to the project folder and run the test-mail-server-1.0.jar file using the command:
```
java -jar test-mail-server-1.0.jar
```
This will start a local mail server that listens on port 2225 for SMTP and port 3335 for POP3.

3. Open the configuration.py file and change the SMTP_SERVER and POP3_SERVER variables to “localhost”. Also, change the SMTP_PORT and POP3_PORT variables to 2225 and 3335, respectively.

4. Open the console_menu.py file and run the Python script using the command:
```
python console_menu.py
```
## Usage
Once you have logged in, you will see a menu with the following options:

* Send an email: This option allows you to compose and send an email to one or more recipients. You will be asked to enter the subject, the recipients (separated by commas), and the message body. You can also attach files to your email by entering their paths (separated by commas) when prompted.

* View inbox: This option allows you to view the list of emails in your inbox. You will see the sender, the subject, and the date of each email. You can select an email to read its full content and attachments. You can also delete an email by entering its number when prompted.

* Quit: This option allows you to exit the email client and close the connection with the mail server.

## License
This project is licensed under the HIHI License - see the LICENSE.md file for more details.
## Acknowledgments
* This project uses the socket and mime modules from the Python standard library to implement the SMTP and POP3 protocols.
* This project uses the test-mail-server project by Eugenehr as a local mail server for testing purposes.
```
https://github.com/eugenehr/test-mail-server
```
## Contact
If you have any questions or feedback, please feel free to contact me at vtthanh04.qb@gmail.com.

## Troubleshooting
If you encounter any issues or errors while using the email client, please refer to the Troubleshooting guide for possible solutions.

## Release History
1.0.0 (December 11, 2023)
Initial release

## Disclaimer
This project is for educational purposes only and should be used responsibly. The authors are not liable for any misuse or damage caused by the software.

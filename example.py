from tenminutemail import MailBox
from time import sleep
import sys

if __name__ == "__main__":
    mail_box = MailBox(None, 10)
    
    connect_response = mail_box.connect()
    if (connect_response["status"] == False):
        print (connect_response["tr_message"])
        exit(0)
    
    print("Mail Address: " + mail_box.email)

    mail_box.start_check_thread()

    while (True):
        try:
            for mail_data in mail_box.mails:
                print("Header:" + mail_data["header"])
                sleep(2)
        except KeyboardInterrupt:
            mail_box.stop_check_thread()
            sys.exit()

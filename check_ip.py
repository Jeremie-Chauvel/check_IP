#! python
import os
import subprocess
import re
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import setup_logging

FROM_MACHINE="RZ"

def update_ip(IP):
    with open("old_IP.txt","w") as new_ip:
        new_ip.write(IP)

    server_name = "smtp.gmail.com:587"
    gmail_user = os.environ["gmail_user"]

    gmail_pwd = os.environ["gmail_pwd"]
    # Setup msg 
    msg = MIMEMultipart("alternative")
    msg['Subject'] = f"External IP tracking for {FROM_MACHINE}"
    msg['From'] = gmail_user
    msg['To'] = os.environ["gmail_to"]
    content = MIMEText(f"<p> the new IP for {FROM_MACHINE} is {IP}</p>", "html")
    msg.attach(content)
    # send msg
    with smtplib.SMTP(server_name) as server:
        try:
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.send_message(msg)
        except RuntimeError as e:
            log.error("Count not send mail"+str(e))
        else:
            log.fatal("successfully sent the mail.")




def check_ip():
    """Check ip and run update_ip if necessary"""
    command = ["dig", "+short", "myip.opendns.com", "@resolver1.opendns.com"]
    IP = subprocess.run(command,stdout=subprocess.PIPE).stdout.decode("UTF-8", "ignore")
    match_obj = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", IP)
    if match_obj:
        try:
            with open("old_IP.txt") as old_ip:
                val = old_ip.read()
        except FileNotFoundError as e:
            print(e)
            log.warning("no old IP found")
            update_ip(IP)
        else:
            if val != IP:
                update_ip(IP)
    else:
        log.error(f"Found IP as a strange syntax: {IP}")

if __name__ == "__main__":

    log = logging.getLogger()
    check_ip()

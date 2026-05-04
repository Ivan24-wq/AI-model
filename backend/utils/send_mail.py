from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText

load_dotenv()

from_mail = os.getenv("EMAIL")
from_password = os.getenv("PASSWORD")
from_name = "Мудрый мухомор"

#Отправка письма
def send_email(to_email: str, link: str):
    

    #Письмо
    msg = MIMEText(
        f"Перейтиде по ссылке: \n{link}",
        "plain",
        "utf-8"
    )
    msg["Subject"] = "Подтверждение регистрации"
    msg["From"] = f"{from_name} <{from_mail}>"
    msg["To"] = to_email

    #Объект для отправки
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_mail, from_password)

    server.sendmail(from_mail, to_email, msg.as_string())

    server.quit()

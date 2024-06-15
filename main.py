from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import os
from typing import List
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

app = FastAPI()

class EmailRequest(BaseModel):
    recipients: List[EmailStr]
    subject: str
    body: str
    sender: EmailStr
    password: str
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    attachments: Optional[List[str]] = None
    
def send_email(email_request: EmailRequest):
    msg = MIMEMultipart()
    msg['From'] = email_request.sender
    msg['To'] = ', '.join(email_request.recipients)
    msg['Subject'] = email_request.subject

    msg.attach(MIMEText(email_request.body, 'plain'))

    # Attach files
    if email_request.attachments:
        for file_path in email_request.attachments:
            part = MIMEApplication(open(file_path, "rb").read())
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
            msg.attach(part)

    try:
        server = smtplib.SMTP(email_request.smtp_server, email_request.smtp_port)
        server.starttls()
        server.login(email_request.sender, email_request.password)
        text = msg.as_string()
        server.sendmail(email_request.sender, email_request.recipients, text)
        server.quit()
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-email/")
async def send_email_endpoint(email_request: EmailRequest):
    return send_email(email_request)

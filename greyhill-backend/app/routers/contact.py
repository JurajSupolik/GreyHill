from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from dotenv import load_dotenv
import pathlib

env_path = pathlib.Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

router = APIRouter(
    prefix="/api/contact",
    tags=["contact"]
)

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    subject: str | None = None
    message: str

@router.post("/send")
async def send_contact_message(contact: ContactMessage):
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "jurajsupolik@gmail.com")
        
        html_message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #f8f9fa; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; }}
                .field {{ margin-bottom: 15px; padding: 10px; background: #f1f5f9; border-radius: 5px; }}
                .label {{ font-weight: bold; color: #1e3a8a; }}
                .message-box {{ background: #e0f2fe; padding: 20px; border-left: 4px solid #2563eb; border-radius: 5px; margin-top: 20px; }}
                .footer {{ text-align: center; color: #64748b; padding: 20px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏢 Nová správa z Greyhill</h1>
                    <p>Kontaktný formulár</p>
                </div>
                <div class="content">
                    <div class="field"><span class="label">👤 Meno:</span> {contact.name}</div>
                    <div class="field"><span class="label">📧 Email:</span> {contact.email}</div>
                    {f'<div class="field"><span class="label">📞 Telefón:</span> {contact.phone}</div>' if contact.phone else ''}
                    {f'<div class="field"><span class="label">📋 Predmet:</span> {contact.subject}</div>' if contact.subject else ''}
                    <div class="message-box">
                        <div class="label">💬 Správa:</div>
                        <p>{contact.message}</p>
                    </div>
                    <div class="footer">
                        <p>Odoslané: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
                        <p>Greyhill Booking System</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        print(f"📧 NOVÁ SPRÁVA od {contact.name} ({contact.email})")
        
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not smtp_username or not smtp_password:
            print("⚠️ SMTP nie je nastavené!")
            return {"success": True, "message": "Správa prijatá (email nekonfigurovaný)", "timestamp": datetime.now().isoformat()}
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Greyhill: {contact.subject or 'Nová správa'}"
        msg['From'] = smtp_username
        msg['To'] = admin_email
        msg['Reply-To'] = contact.email
        
        msg.attach(MIMEText(html_message, 'html'))
        
        print(f"📧 Odosielam email na {admin_email}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Email odoslaný!")
        return {"success": True, "message": "Správa bola úspešne odoslaná!", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        print(f"❌ Chyba: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chyba: {str(e)}")
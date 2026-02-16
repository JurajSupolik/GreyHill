# app/utils/email.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from app.utils.env_variables import get_env_variables, EnvVariables

# Email konfigurácia - UPRAV TIETO ÚDAJE!
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "jurajsupolik@gmail.com"  # Tvoj Gmail

# Príjemca admin emailov
ADMIN_EMAIL = "jurajsupolik@gmail.com"

def get_smtp_password():
    """Get SMTP password from environment variables"""
    env_vars = get_env_variables()
    if not env_vars or not env_vars.smtp_password:
        raise Exception("SMTP password not found")
    return env_vars.smtp_password

def send_booking_confirmation_email(booking_data: dict, apartment_name: str, total_price: float):
    """Pošle email potvrdenie rezervácie hosťovi"""
    
    try:
        # Vytvor email správu
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'✅ Potvrdenie rezervácie - {apartment_name}'
        msg['From'] = SMTP_EMAIL
        msg['To'] = booking_data['guest_email']
        
        # Formátuj dátumy
        check_in = datetime.fromisoformat(booking_data['check_in_date'].replace('Z', '+00:00'))
        check_out = datetime.fromisoformat(booking_data['check_out_date'].replace('Z', '+00:00'))
        
        # HTML obsah emailu
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
              
              <h1 style="color: #1976d2; text-align: center;">🎉 Rezervácia potvrdená!</h1>
              
              <p>Dobrý deň <strong>{booking_data['guest_name']}</strong>,</p>
              
              <p>Vaša rezervácia bola úspešne vytvorená a čaká na potvrdenie administrátorom.</p>
              
              <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h2 style="margin-top: 0; color: #1976d2;">📋 Detaily rezervácie</h2>
                
                <p><strong>🏠 Apartmán:</strong> {apartment_name}</p>
                <p><strong>📅 Príchod:</strong> {check_in.strftime('%d.%m.%Y %H:%M')}</p>
                <p><strong>📅 Odchod:</strong> {check_out.strftime('%d.%m.%Y %H:%M')}</p>
                <p><strong>👥 Počet dospelých:</strong> {booking_data['number_of_adults']}</p>
                <p><strong>💰 Celková cena:</strong> {total_price}€</p>
                <p><strong>📊 Status:</strong> <span style="color: orange;">ČAKÁ NA POTVRDENIE</span></p>
              </div>
              
              <div style="background-color: #e3f2fd; padding: 15px; border-left: 4px solid #1976d2; margin: 20px 0;">
                <p style="margin: 0;"><strong>ℹ️ Dôležité informácie:</strong></p>
                <ul>
                  <li>Vaša rezervácia bude potvrdená administrátorom do 24 hodín</li>
                  <li>Dostanete ďalší email po potvrdení rezervácie</li>
                  <li>Check-in: od 14:00</li>
                  <li>Check-out: do 10:00</li>
                </ul>
              </div>
              
              <p>V prípade akýchkoľvek otázok nás kontaktujte na <a href="mailto:{SMTP_EMAIL}">{SMTP_EMAIL}</a></p>
              
              <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
              
              <p style="text-align: center; color: #999; font-size: 12px;">
                Greyhill Apartments © 2025<br>
                Tento email bol odoslaný automaticky, neodpovedajte naň.
              </p>
              
            </div>
          </body>
        </html>
        """
        
        # Pridaj HTML obsah
        msg.attach(MIMEText(html, 'html'))
        
        # Odošli email
        smtp_password = get_smtp_password()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Email potvrdenie odoslané na {booking_data['guest_email']}")
        return True
        
    except Exception as e:
        print(f"❌ Chyba pri odosielaní emailu: {e}")
        return False


def send_admin_notification_email(booking_data: dict, apartment_name: str, total_price: float, booking_id: int):
    """Pošle notifikáciu adminovi o novej rezervácii"""
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🔔 Nová rezervácia #{booking_id} - {apartment_name}'
        msg['From'] = SMTP_EMAIL
        msg['To'] = ADMIN_EMAIL
        
        check_in = datetime.fromisoformat(booking_data['check_in_date'].replace('Z', '+00:00'))
        check_out = datetime.fromisoformat(booking_data['check_out_date'].replace('Z', '+00:00'))
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
              
              <h1 style="color: #ff9800; text-align: center;">🔔 Nová rezervácia!</h1>
              
              <p>Bola vytvorená nová rezervácia, ktorá čaká na potvrdenie.</p>
              
              <div style="background-color: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h2 style="margin-top: 0; color: #ff9800;">📋 Detaily rezervácie #{booking_id}</h2>
                
                <p><strong>🏠 Apartmán:</strong> {apartment_name}</p>
                <p><strong>👤 Hosť:</strong> {booking_data['guest_name']}</p>
                <p><strong>📧 Email:</strong> {booking_data['guest_email']}</p>
                <p><strong>📱 Telefón:</strong> {booking_data['guest_phone']}</p>
                <p><strong>📅 Príchod:</strong> {check_in.strftime('%d.%m.%Y %H:%M')}</p>
                <p><strong>📅 Odchod:</strong> {check_out.strftime('%d.%m.%Y %H:%M')}</p>
                <p><strong>👥 Počet dospelých:</strong> {booking_data['number_of_adults']}</p>
                <p><strong>💰 Celková cena:</strong> {total_price}€</p>
              </div>
              
              <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:4200/admin" 
                   style="display: inline-block; background-color: #1976d2; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                   Otvoriť Admin Panel
                </a>
              </div>
              
              <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
              
              <p style="text-align: center; color: #999; font-size: 12px;">
                Greyhill Admin Notifications
              </p>
              
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        smtp_password = get_smtp_password()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Admin notifikácia odoslaná")
        return True
        
    except Exception as e:
        print(f"❌ Chyba pri odosielaní admin emailu: {e}")
        return False


def send_booking_confirmed_email(booking: dict, apartment_name: str):
    """Pošle email hosťovi že rezervácia bola potvrdená"""
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'✅ Rezervácia potvrdená - {apartment_name}'
        msg['From'] = SMTP_EMAIL
        msg['To'] = booking['guest_email']
        
        check_in = datetime.fromisoformat(str(booking['check_in_date']).replace('Z', '+00:00'))
        check_out = datetime.fromisoformat(str(booking['check_out_date']).replace('Z', '+00:00'))
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
              
              <h1 style="color: #4caf50; text-align: center;">✅ Rezervácia POTVRDENÁ!</h1>
              
              <p>Dobrý deň <strong>{booking['guest_name']}</strong>,</p>
              
              <p>Skvelé správy! Vaša rezervácia bola <strong style="color: #4caf50;">POTVRDENÁ</strong>.</p>
              
              <div style="background-color: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4caf50;">
                <h2 style="margin-top: 0; color: #4caf50;">📋 Detaily rezervácie</h2>
                
                <p><strong>🏠 Apartmán:</strong> {apartment_name}</p>
                <p><strong>📅 Príchod:</strong> {check_in.strftime('%d.%m.%Y %H:%M')}</p>
                <p><strong>📅 Odchod:</strong> {check_out.strftime('%d.%m.%Y %H:%M')}</p>
                <p><strong>👥 Počet dospelých:</strong> {booking['number_of_adults']}</p>
                <p><strong>💰 Celková cena:</strong> {booking['total_price']}€</p>
                <p><strong>📊 Status:</strong> <span style="color: #4caf50; font-weight: bold;">POTVRDENÁ</span></p>
              </div>
              
              <div style="background-color: #fff3e0; padding: 15px; border-left: 4px solid #ff9800; margin: 20px 0;">
                <p style="margin: 0;"><strong>📝 Dôležité informácie:</strong></p>
                <ul>
                  <li><strong>Check-in:</strong> od 14:00 hod.</li>
                  <li><strong>Check-out:</strong> do 10:00 hod.</li>
                  <li>Prosím, prihláste sa na recepcii s platným dokladom totožnosti</li>
                  <li>V prípade oneskoreného príchodu nás kontaktujte</li>
                </ul>
              </div>
              
              <div style="text-align: center; margin: 30px 0;">
                <p style="font-size: 18px; color: #333;">Tešíme sa na Vašu návštevu! 🎉</p>
              </div>
              
              <p>V prípade akýchkoľvek otázok nás kontaktujte na <a href="mailto:{SMTP_EMAIL}">{SMTP_EMAIL}</a></p>
              
              <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
              
              <p style="text-align: center; color: #999; font-size: 12px;">
                Greyhill Apartments © 2025<br>
                Tento email bol odoslaný automaticky, neodpovedajte naň.
              </p>
              
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        smtp_password = get_smtp_password()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Email potvrdenia odoslaný na {booking['guest_email']}")
        return True
        
    except Exception as e:
        print(f"❌ Chyba pri odosielaní emailu potvrdenia: {e}")
        return False


def send_booking_cancelled_email(booking: dict, apartment_name: str):
    """Pošle email hosťovi že rezervácia bola zrušená"""
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'❌ Rezervácia zrušená - {apartment_name}'
        msg['From'] = SMTP_EMAIL
        msg['To'] = booking['guest_email']
        
        check_in = datetime.fromisoformat(str(booking['check_in_date']).replace('Z', '+00:00'))
        check_out = datetime.fromisoformat(str(booking['check_out_date']).replace('Z', '+00:00'))
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
              
              <h1 style="color: #f44336; text-align: center;">❌ Rezervácia zrušená</h1>
              
              <p>Dobrý deň <strong>{booking['guest_name']}</strong>,</p>
              
              <p>Vaša rezervácia bola <strong style="color: #f44336;">ZRUŠENÁ</strong>.</p>
              
              <div style="background-color: #ffebee; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f44336;">
                <h2 style="margin-top: 0; color: #f44336;">📋 Zrušená rezervácia</h2>
                
                <p><strong>🏠 Apartmán:</strong> {apartment_name}</p>
                <p><strong>📅 Príchod:</strong> {check_in.strftime('%d.%m.%Y %H:%M')}</p>
                <p><strong>📅 Odchod:</strong> {check_out.strftime('%d.%m.%Y %H:%M')}</p>
                <p><strong>👥 Počet dospelých:</strong> {booking['number_of_adults']}</p>
                <p><strong>💰 Celková cena:</strong> {booking['total_price']}€</p>
                <p><strong>📊 Status:</strong> <span style="color: #f44336; font-weight: bold;">ZRUŠENÁ</span></p>
              </div>
              
              <div style="background-color: #e3f2fd; padding: 15px; border-left: 4px solid #1976d2; margin: 20px 0;">
                <p style="margin: 0;"><strong>ℹ️ Čo ďalej?</strong></p>
                <ul>
                  <li>Ak ste rezerváciu zrušili omylom, kontaktujte nás</li>
                  <li>Môžete si vytvoriť novú rezerváciu na našej stránke</li>
                  <li>V prípade platieb budete kontaktovaný ohľadom refundácie</li>
                </ul>
              </div>
              
              <p>V prípade akýchkoľvek otázok nás kontaktujte na <a href="mailto:{SMTP_EMAIL}">{SMTP_EMAIL}</a></p>
              
              <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
              
              <p style="text-align: center; color: #999; font-size: 12px;">
                Greyhill Apartments © 2025<br>
                Tento email bol odoslaný automaticky, neodpovedajte naň.
              </p>
              
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        smtp_password = get_smtp_password()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Email zrušenia odoslaný na {booking['guest_email']}")
        return True
        
    except Exception as e:
        print(f"❌ Chyba pri odosielaní emailu zrušenia: {e}")
        return False
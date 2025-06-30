#!/usr/bin/env python3
"""
Simple email test script to verify SMTP configuration
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def test_email_config():
    """Test SMTP configuration"""
    
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    print(f"Testing SMTP configuration:")
    print(f"Server: {smtp_server}:{smtp_port}")
    print(f"Username: {smtp_username}")
    print(f"Password: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
    print()
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = smtp_username  # Send to self for testing
        msg['Subject'] = "Newsletter Agent Test Email"
        
        body = """
        This is a test email from your Newsletter AI Agent.
        
        If you receive this email, your SMTP configuration is working correctly!
        
        🤖 Newsletter Agent Test
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        
        print("Authenticating...")
        server.login(smtp_username, smtp_password)
        
        print("Sending test email...")
        text = msg.as_string()
        server.sendmail(smtp_username, smtp_username, text)
        server.quit()
        
        print("✅ Email sent successfully!")
        print(f"Check your inbox: {smtp_username}")
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n💡 Solutions:")
        print("1. Enable 2-Step Verification in your Google Account")
        print("2. Generate an App Password: https://myaccount.google.com/apppasswords")
        print("3. Use the 16-character app password instead of your regular password")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_email_config()

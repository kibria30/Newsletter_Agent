import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import os
from typing import List, Dict

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
    
    def create_newsletter_html(self, articles: List[Dict], user_interests: List[str]) -> str:
        """Create HTML newsletter content"""
        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }
                .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
                .article { border-bottom: 1px solid #eee; padding: 20px 0; }
                .article h3 { color: #2c3e50; margin-bottom: 10px; }
                .category { background: #3498db; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
                .source { color: #7f8c8d; font-size: 14px; }
                .footer { background: #f8f9fa; padding: 20px; text-align: center; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 Your AI Newsletter</h1>
                <p>Personalized tech insights for: {{ interests|join(', ') }}</p>
            </div>
            
            <div class="content">
                {% for article in articles %}
                <div class="article">
                    <span class="category">{{ article.category }}</span>
                    <h3><a href="{{ article.url }}" style="text-decoration: none; color: #2c3e50;">{{ article.title }}</a></h3>
                    <p>{{ article.content[:300] }}...</p>
                    <div class="source">Source: {{ article.source }} | Published: {{ article.published_at.strftime('%Y-%m-%d') if article.published_at else 'Recently' }}</div>
                </div>
                {% endfor %}
            </div>
            
            <div class="footer">
                <p>This newsletter was curated by AI based on your interests.</p>
                <p><a href="#">Unsubscribe</a> | <a href="#">Update Preferences</a></p>
            </div>
        </body>
        </html>
        """)
        
        return template.render(articles=articles, interests=user_interests)
    
    def send_newsletter(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send newsletter email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            # Create HTML part
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return False

email_service = EmailService()
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime, timedelta
from database import DatabaseManager
import telegram
from config import Config

class NotificationManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.telegram_bot = None
        if Config.TELEGRAM_BOT_TOKEN:
            self.telegram_bot = telegram.Bot(token=Config.TELEGRAM_BOT_TOKEN)

    def send_email_notification(self, email, subject, html_content):
        """Send email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = Config.SMTP_USERNAME
            msg['To'] = email
            msg['Subject'] = subject

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Connect to SMTP server
            server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
            server.starttls()
            server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)

            # Send email
            server.sendmail(Config.SMTP_USERNAME, email, msg.as_string())
            server.quit()

            print(f"✅ Email sent to {email}")
            return True

        except Exception as e:
            print(f"❌ Error sending email to {email}: {e}")
            return False

    async def send_telegram_notification(self, telegram_id, message):
        """Send Telegram notification"""
        try:
            if not self.telegram_bot:
                print("❌ Telegram bot not configured")
                return False

            await self.telegram_bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='HTML'
            )

            print(f"✅ Telegram message sent to {telegram_id}")
            return True

        except Exception as e:
            print(f"❌ Error sending Telegram message to {telegram_id}: {e}")
            return False

    def get_new_scholarships(self, since_date=None):
        """Get scholarships added since specified date"""
        if not since_date:
            since_date = datetime.now() - timedelta(days=7)  # Default to last week

        scholarships = self.db.get_scholarships()
        new_scholarships = []

        for scholarship in scholarships:
            if scholarship.scraped_at and scholarship.scraped_at >= since_date:
                new_scholarships.append(scholarship)

        return new_scholarships

    def get_urgent_deadlines(self, within_days=14):
        """Get scholarships with deadlines within specified days"""
        deadline_threshold = datetime.now() + timedelta(days=within_days)

        scholarships = self.db.get_scholarships()
        urgent_scholarships = []

        for scholarship in scholarships:
            if (scholarship.deadline and
                scholarship.deadline <= deadline_threshold and
                scholarship.deadline >= datetime.now()):
                urgent_scholarships.append(scholarship)

        return urgent_scholarships

    def generate_html_digest(self, scholarships, title="New Scholarships"):
        """Generate HTML email digest"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
                .scholarship {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .deadline {{ color: #dc3545; font-weight: bold; }}
                .apply-btn {{ background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                .footer {{ margin-top: 30px; padding: 20px; background: #f8f9fa; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎓 {title}</h1>
                <p>ScholarSift - Your Smart Scholarship Discovery Platform</p>
            </div>

            <div style="padding: 20px;">
                <p>Hello! Here are the latest scholarship opportunities:</p>
        """

        for scholarship in scholarships:
            html += f"""
            <div class="scholarship">
                <h3>{scholarship.name}</h3>
                {f'<p><strong>Country:</strong> {scholarship.country}</p>' if scholarship.country else ''}
                {f'<p><strong>Degree Level:</strong> {scholarship.degree_level}</p>' if scholarship.degree_level else ''}
                {f'<p><strong>Funding:</strong> {scholarship.funding_type.replace("_", " ").title()}</p>' if scholarship.funding_type else ''}
                {f'<p><strong>GPA Requirement:</strong> {scholarship.gpa_requirement}</p>' if scholarship.gpa_requirement else ''}
                {f'<p class="deadline"><strong>Deadline:</strong> {scholarship.deadline.strftime("%B %d, %Y")}</p>' if scholarship.deadline else ''}
                <p>{scholarship.summary or scholarship.description[:200] + "..." if scholarship.description else "No description available"}</p>
                <a href="{scholarship.application_link}" class="apply-btn">Apply Now</a>
            </div>
            """

        html += """
            </div>
            <div class="footer">
                <p>This is an automated update from ScholarSift.</p>
                <p>You can manage your subscription preferences anytime.</p>
                <p><a href="https://scholarsift.com/unsubscribe">Unsubscribe</a> | <a href="https://scholarsift.com">Visit Website</a></p>
            </div>
        </body>
        </html>
        """

        return html

    async def send_weekly_digest(self):
        """Send weekly digest to all subscribers"""
        print("📧 Sending weekly digest...")

        # Get new scholarships from the past week
        new_scholarships = self.get_new_scholarships(datetime.now() - timedelta(days=7))

        if not new_scholarships:
            print("ℹ️  No new scholarships to send")
            return

        # Get all subscriptions
        subscriptions = self.db.get_scholarships()  # This should be a method to get subscriptions
        # Note: We need to add a method to database.py to get subscriptions

        subject = f"ScholarSift Weekly Digest - {len(new_scholarships)} New Scholarships!"
        html_content = self.generate_html_digest(new_scholarships, "Weekly Scholarship Digest")

        email_count = 0
        telegram_count = 0

        for subscription in subscriptions:  # This needs to be implemented
            if subscription.email:
                success = self.send_email_notification(subscription.email, subject, html_content)
                if success:
                    email_count += 1

            if subscription.telegram_id:
                message = self.generate_telegram_message(new_scholarships)
                success = await self.send_telegram_notification(subscription.telegram_id, message)
                if success:
                    telegram_count += 1

        print(f"📊 Weekly digest sent: {email_count} emails, {telegram_count} Telegram messages")

    async def send_urgent_notifications(self):
        """Send urgent deadline notifications"""
        print("🚨 Sending urgent deadline notifications...")

        urgent_scholarships = self.get_urgent_deadlines()

        if not urgent_scholarships:
            print("ℹ️  No urgent deadlines")
            return

        # Generate messages
        subject = f"URGENT: {len(urgent_scholarships)} Scholarships Closing Soon!"
        html_content = self.generate_html_digest(urgent_scholarships, "Urgent Deadlines")

        telegram_message = self.generate_telegram_message(urgent_scholarships, urgent=True)

        # Get subscriptions that want urgent notifications
        subscriptions = self.db.get_scholarships()  # This needs to be implemented properly

        email_count = 0
        telegram_count = 0

        for subscription in subscriptions:
            preferences = json.loads(subscription.preferences or '{}')

            if not preferences.get('urgent', True):
                continue

            if subscription.email:
                success = self.send_email_notification(subscription.email, subject, html_content)
                if success:
                    email_count += 1

            if subscription.telegram_id:
                success = await self.send_telegram_notification(subscription.telegram_id, telegram_message)
                if success:
                    telegram_count += 1

        print(f"🚨 Urgent notifications sent: {email_count} emails, {telegram_count} Telegram messages")

    def generate_telegram_message(self, scholarships, urgent=False):
        """Generate Telegram message"""
        if urgent:
            header = "🚨 URGENT DEADLINES\n\n"
        else:
            header = "🎓 New Scholarships This Week\n\n"

        message = header

        for i, scholarship in enumerate(scholarships[:5]):  # Limit to 5 scholarships
            message += f"📚 {scholarship.name}\n"
            if scholarship.country:
                message += f"🌍 {scholarship.country}\n"
            if scholarship.deadline:
                message += f"⏰ {scholarship.deadline.strftime('%Y-%m-%d')}\n"
            if scholarship.funding_type:
                message += f"💰 {scholarship.funding_type.replace('_', ' ').title()}\n"
            message += f"🔗 {scholarship.application_link}\n\n"

        if len(scholarships) > 5:
            message += f"... and {len(scholarships) - 5} more scholarships!\n\n"

        message += "Visit our website for more details and filtering options."
        return message

# Add this method to DatabaseManager class in database.py
def get_subscriptions(self):
    """Get all subscriptions"""
    session = self.Session()
    try:
        return session.query(Subscription).all()
    finally:
        session.close()

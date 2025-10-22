import os

class Config:
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///scholarships.db')

    # Scraping
    DEFAULT_USER_AGENT = 'ScholarSift/1.0 (Educational Research Bot)'
    RESPECT_ROBOTS_TXT = True
    REQUEST_DELAY = 2  # seconds between requests
    MAX_RETRIES = 3

    # Playwright settings
    PLAYWRIGHT_HEADLESS = True
    PLAYWRIGHT_TIMEOUT = 30000

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # AI/API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    # Email settings
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

    # Seed URLs for discovery
    SEED_SOURCES = [
        'https://www.daad.de/en/',
        'https://www.chevening.org/scholarships/',
        'https://mastercardfdn.org/',
        'https://opportunitiesforafricans.com/',
        'https://scholarshiproar.com/',
        'https://www.commonwealthscholarships.org/'
    ]

    # Scholarship keywords for discovery
    SCHOLARSHIP_KEYWORDS = [
        'scholarship', 'grant', 'fellowship', 'bursary', 'financial aid',
        'fully funded', 'partial funding', 'tuition waiver', 'stipend'
    ]

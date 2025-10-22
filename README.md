# ScholarSift - Smart Scholarship Discovery Platform

🎓 **ScholarSift** is an intelligent web scraper that automatically discovers, analyzes, and organizes scholarship opportunities from trusted sources worldwide. It features AI-powered summarization, dynamic filtering, and automated notifications.

## ✨ Features

- **Smart Web Scraping**: Handles both static and JavaScript-rendered pages with adaptive parsing
- **AI Summarization**: Uses OpenAI or local transformers to summarize scholarship descriptions
- **Dynamic Filtering**: Filter by country, degree level, GPA requirements, funding type, and deadlines
- **Database Storage**: SQLite database with JSON/CSV export capabilities
- **Web Dashboard**: Beautiful Flask-based interface for browsing scholarships
- **Notification System**: Email and Telegram alerts for new opportunities and urgent deadlines
- **Ethical Scraping**: Respects robots.txt and implements rate limiting
- **Discovery Mode**: Automatically finds new scholarship sources

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd ScholarSift
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers**
   ```bash
   playwright install
   ```

3. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   # Database
   DATABASE_URL=sqlite:///scholarships.db

   # API Keys (Optional - for AI features)
   OPENAI_API_KEY=your_openai_api_key_here

   # Email Notifications (Optional)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password

   # Telegram Notifications (Optional)
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token

   # Flask
   SECRET_KEY=your-secret-key-here
   FLASK_DEBUG=True
   ```

4. **Initialize Database**
   ```bash
   python main.py
   ```

5. **Start Scraping**
   ```bash
   # Scrape from seed sources
   python main.py --scrape

   # Scrape specific URLs
   python main.py --scrape --urls "https://www.daad.de/en/" "https://www.chevening.org/scholarships/"
   ```

6. **Start Web Dashboard**
   ```bash
   cd dashboard
   python app.py
   ```

   Visit `http://localhost:5000` to access the web interface.

## 📁 Project Structure

```
ScholarSift/
├── main.py              # Main scraper orchestrator
├── scraper.py           # Core scraping logic with Playwright
├── database.py          # SQLite database operations
├── summarizer.py        # AI-powered text summarization
├── notifications.py     # Email and Telegram notifications
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── dashboard/           # Flask web application
│   ├── app.py          # Flask application
│   ├── static/         # CSS, JS, images
│   └── templates/      # HTML templates
│       └── index.html  # Main dashboard
├── data/               # Exported data files
│   └── scholarships.json
└── README.md           # This file
```

## 🛠️ Usage

### Command Line Interface

```bash
# Basic scraping
python main.py --scrape

# Advanced scraping options
python main.py --scrape --discovery    # Enable discovery mode
python main.py --scrape --urls URL1 URL2    # Scrape specific URLs

# Export data
python main.py --export json --filter-country "Germany"
python main.py --export json --filter-degree masters --filter-gpa 3.5

# Filter options
--filter-country     # Filter by country
--filter-degree      # undergraduate, masters, phd
--filter-gpa         # Minimum GPA requirement
```

### Web Dashboard

The Flask dashboard provides:

- **Browse Scholarships**: View all scholarships in a responsive grid
- **Advanced Filtering**: Filter by multiple criteria simultaneously
- **Scholarship Details**: Click any scholarship for full details
- **Subscription Management**: Subscribe to email/Telegram updates
- **Real-time Search**: Fast filtering and search capabilities

#### API Endpoints

- `GET /api/scholarships` - Get scholarships with optional filters
- `GET /api/scholarships/<id>` - Get specific scholarship details
- `GET /api/countries` - Get available countries
- `GET /api/funding-types` - Get available funding types
- `POST /api/subscribe` - Subscribe to notifications
- `POST /api/summarize` - Summarize text using AI

### Filtering Options

#### Country Filter
Filter scholarships by destination country (e.g., USA, UK, Germany, Canada)

#### Degree Level
- Undergraduate
- Master's
- PhD
- Postdoc

#### Funding Type
- Fully Funded
- Partial
- Stipend
- Other

#### GPA Requirements
Filter by minimum GPA requirement

#### Deadline Filters
- Next 30 days
- Next 2 months
- Next 3 months

## 🤖 AI Features

### Text Summarization
ScholarSift uses AI to generate concise summaries of scholarship descriptions:

- **OpenAI Integration**: Uses GPT-3.5-turbo for high-quality summaries (requires API key)
- **Local Fallback**: Uses BART transformer model when OpenAI is unavailable
- **Smart Extraction**: Focuses on key benefits, eligibility, and application process

### Discovery Mode (Coming Soon)
Automatically finds new scholarship sources by:
- Analyzing seed websites for related links
- Using search APIs to find scholarship pages
- Keyword-based content analysis

## 📧 Notifications

### Email Notifications
- Weekly digest of new scholarships
- Urgent deadline alerts (closing within 2 weeks)
- Customizable preferences

### Telegram Notifications
- Real-time alerts via Telegram bot
- Weekly summaries
- Urgent deadline notifications

## 🔧 Configuration

### Scraping Settings
```python
# config.py
DEFAULT_USER_AGENT = 'ScholarSift/1.0 (Educational Research Bot)'
RESPECT_ROBOTS_TXT = True
REQUEST_DELAY = 2  # seconds between requests
MAX_RETRIES = 3
```

### Seed Sources
The scraper starts with these trusted sources:
- DAAD (Germany)
- Chevening Scholarships (UK)
- Mastercard Foundation
- Commonwealth Scholarships
- Opportunities for Africans
- Scholarship Roar

## 🚨 Ethical Considerations

ScholarSift implements ethical scraping practices:

- **Respects robots.txt**: Checks and follows website rules
- **Rate Limiting**: Implements delays between requests
- **User Agent**: Identifies as educational research bot
- **Error Handling**: Gracefully handles failures and timeouts
- **Data Privacy**: Only collects publicly available information

## 🔄 Automation

### Scheduled Scraping
Set up cron jobs for automatic updates:

```bash
# Weekly scraping (Sundays at 9 AM)
0 9 * * 0 cd /path/to/ScholarSift && python main.py --scrape

# Daily urgent checks (6 AM)
0 6 * * * cd /path/to/ScholarSift && python -c "from notifications import NotificationManager; import asyncio; asyncio.run(NotificationManager().send_urgent_notifications())"
```

### Weekly Notifications
```bash
# Send weekly digest (Mondays at 8 AM)
0 8 * * 1 cd /path/to/ScholarSift && python -c "from notifications import NotificationManager; import asyncio; asyncio.run(NotificationManager().send_weekly_digest())"
```

## 🐛 Troubleshooting

### Common Issues

1. **Playwright Installation**
   ```bash
   playwright install chromium
   ```

2. **Database Issues**
   ```bash
   rm scholarships.db
   python main.py
   ```

3. **API Rate Limits**
   - Add delays in config.py
   - Use rotating user agents
   - Implement exponential backoff

4. **Memory Issues**
   - Process scholarships in batches
   - Use pagination for large datasets

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Playwright, BeautifulSoup, Flask, and SQLAlchemy
- AI features powered by OpenAI and Hugging Face Transformers
- Icons from Font Awesome
- Bootstrap for responsive design

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the configuration options

---

**ScholarSift** - Making scholarship discovery smarter and more accessible! 🎓

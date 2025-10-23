import sys
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import json
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager

# Try to import summarizer, fallback if not available
try:
    from summarizer import ScholarshipSummarizer
    SUMMARIZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Summarizer not available: {e}")
    SUMMARIZER_AVAILABLE = False
    ScholarshipSummarizer = None

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app)

# Initialize database and summarizer
db = DatabaseManager()
summarizer = ScholarshipSummarizer() if SUMMARIZER_AVAILABLE else None

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/scholarships')
def get_scholarships():
    """API endpoint to get scholarships with filters"""
    # Get filter parameters
    filters = {}

    country = request.args.get('country')
    degree_level = request.args.get('degree_level')
    funding_type = request.args.get('funding_type')
    gpa_min = request.args.get('gpa_min', type=float)
    gpa_max = request.args.get('gpa_max', type=float)
    deadline_days = request.args.get('deadline_days', type=int)

    if country:
        filters['country'] = country
    if degree_level:
        filters['degree_level'] = degree_level
    if funding_type:
        filters['funding_type'] = funding_type
    if gpa_min:
        filters['gpa_min'] = gpa_min
    if gpa_max:
        filters['gpa_max'] = gpa_max
    if deadline_days:
        filters['deadline_before'] = datetime.now() + timedelta(days=deadline_days)

    scholarships = db.get_scholarships(filters)

    # Convert to JSON-serializable format
    result = []
    for scholarship in scholarships:
        scholarship_data = {
            'id': scholarship.id,
            'name': scholarship.name,
            'description': scholarship.description,
            'eligibility': scholarship.eligibility,
            'deadline': scholarship.deadline.isoformat() if scholarship.deadline else None,
            'funding_type': scholarship.funding_type,
            'country': scholarship.country,
            'university': scholarship.university,
            'degree_level': scholarship.degree_level,
            'gpa_requirement': scholarship.gpa_requirement,
            'application_link': scholarship.application_link,
            'source_url': scholarship.source_url,
            'source_name': scholarship.source_name,
            'scraped_at': scholarship.scraped_at.isoformat(),
            'summary': scholarship.summary or summarizer.summarize_scholarship(scholarship.description or '')
        }
        result.append(scholarship_data)

    return jsonify(result)

@app.route('/api/scholarships/<int:scholarship_id>')
def get_scholarship(scholarship_id):
    """Get detailed information about a specific scholarship"""
    scholarships = db.get_scholarships()
    scholarship = next((s for s in scholarships if s.id == scholarship_id), None)

    if not scholarship:
        return jsonify({'error': 'Scholarship not found'}), 404

    scholarship_data = {
        'id': scholarship.id,
        'name': scholarship.name,
        'description': scholarship.description,
        'eligibility': scholarship.eligibility,
        'deadline': scholarship.deadline.isoformat() if scholarship.deadline else None,
        'funding_type': scholarship.funding_type,
        'country': scholarship.country,
        'university': scholarship.university,
        'degree_level': scholarship.degree_level,
        'gpa_requirement': scholarship.gpa_requirement,
        'application_link': scholarship.application_link,
        'source_url': scholarship.source_url,
        'source_name': scholarship.source_name,
        'scraped_at': scholarship.scraped_at.isoformat(),
        'summary': scholarship.summary or (summarizer.summarize_scholarship(scholarship.description or '') if summarizer else scholarship.description[:200] + '...' if scholarship.description else '')
    }

    return jsonify(scholarship_data)

@app.route('/api/countries')
def get_countries():
    """Get list of available countries"""
    scholarships = db.get_scholarships()
    countries = set()
    for scholarship in scholarships:
        if scholarship.country:
            countries.add(scholarship.country)

    return jsonify(sorted(list(countries)))

@app.route('/api/funding-types')
def get_funding_types():
    """Get list of available funding types"""
    scholarships = db.get_scholarships()
    funding_types = set()
    for scholarship in scholarships:
        if scholarship.funding_type:
            funding_types.add(scholarship.funding_type)

    return jsonify(sorted(list(funding_types)))

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Subscribe to scholarship updates"""
    data = request.get_json()

    if not data or not (data.get('email') or data.get('telegram_id')):
        return jsonify({'error': 'Email or Telegram ID required'}), 400

    subscription_data = {
        'email': data.get('email'),
        'telegram_id': data.get('telegram_id'),
        'preferences': json.dumps(data.get('preferences', {})),
        'subscribed_at': datetime.now()
    }

    try:
        subscription_id = db.add_subscription(subscription_data)
        return jsonify({'message': 'Successfully subscribed!', 'id': subscription_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    """Summarize scholarship text"""
    data = request.get_json()

    if not data or not data.get('text'):
        return jsonify({'error': 'Text required'}), 400

    summary = summarizer.summarize_scholarship(data['text'], data.get('max_length', 150))
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=app.config['FLASK_DEBUG'], host='0.0.0.0', port=5000)

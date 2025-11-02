#!/usr/bin/env python3
"""
Sample data generator for ScholarSift
Creates realistic scholarship data for testing the interface
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample scholarship data"""
    db = DatabaseManager()

    # Clear existing data
    scholarships = db.get_scholarships()
    for scholarship in scholarships:
        db.update_scholarship(scholarship.id, {'is_active': False})

    sample_scholarships = [
        {
            'name': 'DAAD Development-Related Postgraduate Courses (EPOS)',
            'description': 'The German Academic Exchange Service (DAAD) offers scholarships for development-related postgraduate courses. These scholarships are awarded to participants from developing countries to study in Germany. The program aims to train specialists and managerial staff from developing countries with a special focus on sustainability and development issues.',
            'eligibility': 'Bachelor degree with above-average grades, at least 2 years of professional experience, English or German language proficiency (TOEFL/IELTS), commitment to development policy issues. Age limit: 36 years for master programs, 42 years for doctoral programs.',
            'deadline': datetime.now() + timedelta(days=random.randint(30, 120)),
            'funding_type': 'fully_funded',
            'country': 'Germany',
            'university': 'Multiple German Universities',
            'degree_level': 'masters',
            'gpa_requirement': 3.0,
            'application_link': 'https://www.daad.de/en/study-and-research-in-germany/scholarships/epos/',
            'source_url': 'https://www.daad.de/en/',
            'source_name': 'daad.de'
        },
        {
            'name': 'Chevening Scholarships',
            'description': 'Chevening Scholarships are the UK government\'s global scholarship programme, funded by the Foreign, Commonwealth and Development Office (FCDO) and partner organisations. The scholarships are awarded to outstanding scholars with leadership potential from around the world to study postgraduate courses at UK universities.',
            'eligibility': 'Undergraduate degree equivalent to a UK 2:1, at least 2 years of work experience, leadership qualities, commitment to return home after studies, English language proficiency (IELTS 6.5+), not a UK citizen or dual citizen.',
            'deadline': datetime.now() + timedelta(days=random.randint(15, 60)),
            'funding_type': 'fully_funded',
            'country': 'UK',
            'university': 'Multiple UK Universities',
            'degree_level': 'masters',
            'gpa_requirement': 3.2,
            'application_link': 'https://www.chevening.org/apply/',
            'source_url': 'https://www.chevening.org/',
            'source_name': 'chevening.org'
        },
        {
            'name': 'Fulbright Foreign Student Program',
            'description': 'The Fulbright Foreign Student Program enables graduate students, young professionals and artists from abroad to study and conduct research in the United States. The Fulbright Program operates in more than 160 countries worldwide and has provided approximately 310,000 participants with the opportunity to exchange ideas and contribute to finding solutions to shared international concerns.',
            'eligibility': 'Bachelor degree or equivalent, English proficiency (TOEFL/IELTS), strong academic record, leadership potential, commitment to return home, not US citizen or permanent resident.',
            'deadline': datetime.now() + timedelta(days=random.randint(45, 90)),
            'funding_type': 'fully_funded',
            'country': 'USA',
            'university': 'Multiple US Universities',
            'degree_level': 'masters',
            'gpa_requirement': 3.5,
            'application_link': 'https://foreign.fulbrightonline.org/',
            'source_url': 'https://fulbrightprogram.org/',
            'source_name': 'fulbrightprogram.org'
        },
        {
            'name': 'Australia Awards Scholarships',
            'description': 'Australia Awards Scholarships are long-term awards administered by the Department of Foreign Affairs and Trade. They aim to contribute to the development needs of Australia\'s partner countries in line with bilateral and regional agreements. The scholarships provide opportunities for people from developing countries to undertake full-time undergraduate or postgraduate study at participating Australian universities.',
            'eligibility': 'Minimum 12 years of education, English proficiency (IELTS 6.5+), meet DFAT\'s OASIS requirements, not Australian citizen or permanent resident, meet specific country requirements.',
            'deadline': datetime.now() + timedelta(days=random.randint(20, 75)),
            'funding_type': 'fully_funded',
            'country': 'Australia',
            'university': 'Multiple Australian Universities',
            'degree_level': 'undergraduate',
            'gpa_requirement': 2.8,
            'application_link': 'https://www.australiaawards.gov.au/',
            'source_url': 'https://www.australiaawards.gov.au/',
            'source_name': 'australiaawards.gov.au'
        },
        {
            'name': 'Vanier Canada Graduate Scholarships',
            'description': 'The Vanier Canada Graduate Scholarships (Vanier CGS) program helps Canadian institutions attract highly qualified doctoral students. The scholarships are towards a doctoral degree (or combined MA/PhD or MD/PhD) at participating Canadian universities. The program aims to establish Canada as a global centre of excellence in research and higher learning.',
            'eligibility': 'PhD program or combined MA/PhD/MD/PhD, nominated by Canadian institution, academic excellence, research potential, leadership abilities, English or French proficiency.',
            'deadline': datetime.now() + timedelta(days=random.randint(30, 90)),
            'funding_type': 'fully_funded',
            'country': 'Canada',
            'university': 'Multiple Canadian Universities',
            'degree_level': 'phd',
            'gpa_requirement': 3.7,
            'application_link': 'https://vanier.gc.ca/en/application_process-processus_demande.html',
            'source_url': 'https://vanier.gc.ca/',
            'source_name': 'vanier.gc.ca'
        },
        {
            'name': 'Swedish Institute Scholarships for Global Professionals',
            'description': 'The Swedish Institute Scholarships for Global Professionals (SISGP) is the Swedish government\'s international awards scheme aimed at developing global leaders who will contribute to the United Nations 2030 Agenda for Sustainable Development. The scholarship covers full tuition fees, living expenses, travel grants and insurance.',
            'eligibility': 'Bachelor degree, work experience, leadership experience, English proficiency (IELTS 6.5+ or equivalent), from eligible countries, commitment to sustainable development.',
            'deadline': datetime.now() + timedelta(days=random.randint(25, 70)),
            'funding_type': 'fully_funded',
            'country': 'Sweden',
            'university': 'Multiple Swedish Universities',
            'degree_level': 'masters',
            'gpa_requirement': 3.0,
            'application_link': 'https://si.se/en/apply/scholarships/',
            'source_url': 'https://si.se/',
            'source_name': 'si.se'
        },
        {
            'name': 'Holland Scholarship',
            'description': 'The Holland Scholarship is meant for international students from outside the European Economic Area (EEA) who want to do their bachelor\'s or master\'s in the Netherlands. The scholarship amounts to €5,000 which you will receive in the first year of your studies.',
            'eligibility': 'Non-EEA nationality, applying for first year of bachelor or master program, never studied in Netherlands, meet English requirements, excellent academic performance.',
            'deadline': datetime.now() + timedelta(days=random.randint(40, 100)),
            'funding_type': 'partial',
            'country': 'Netherlands',
            'university': 'Multiple Dutch Universities',
            'degree_level': 'undergraduate',
            'gpa_requirement': 3.2,
            'application_link': 'https://www.studyinholland.nl/scholarships/holland-scholarship',
            'source_url': 'https://www.studyinholland.nl/',
            'source_name': 'studyinholland.nl'
        },
        {
            'name': 'Swiss Government Excellence Scholarships',
            'description': 'The Swiss Government Excellence Scholarships are aimed at young researchers from abroad who have completed a master\'s degree or PhD and at foreign artists holding a bachelor\'s degree. The scholarships are offered for research or study at all Swiss cantonal universities, universities of applied sciences and the two federal institutes of technology.',
            'eligibility': 'Master degree or PhD for research scholarships, Bachelor degree for arts scholarships, under 35 years old, English, German, French or Italian proficiency, not Swiss citizen.',
            'deadline': datetime.now() + timedelta(days=random.randint(35, 85)),
            'funding_type': 'fully_funded',
            'country': 'Switzerland',
            'university': 'Multiple Swiss Universities',
            'degree_level': 'phd',
            'gpa_requirement': 3.5,
            'application_link': 'https://www.sbfi.admin.ch/sbfi/en/home/education/scholarships-and-grants/swiss-government-excellence-scholarships.html',
            'source_url': 'https://www.sbfi.admin.ch/',
            'source_name': 'sbfi.admin.ch'
        },
        {
            'name': 'Erasmus Mundus Joint Master Degrees',
            'description': 'Erasmus Mundus Joint Master Degrees (EMJMDs) are international study programmes delivered by consortia of higher education institutions. They offer scholarships to the best students from around the world to study in at least two European countries. The programmes last 1-2 years and lead to the award of a joint or multiple degree.',
            'eligibility': 'Bachelor degree or equivalent, English proficiency, meet specific program requirements, not European citizen for some scholarships, academic excellence.',
            'deadline': datetime.now() + timedelta(days=random.randint(20, 60)),
            'funding_type': 'fully_funded',
            'country': 'Multiple European Countries',
            'university': 'Multiple European Universities',
            'degree_level': 'masters',
            'gpa_requirement': 3.0,
            'application_link': 'https://erasmus-plus.ec.europa.eu/opportunities/scholarships/students/scholarships-for-erasmus-mundus-joint-masters',
            'source_url': 'https://erasmus-plus.ec.europa.eu/',
            'source_name': 'erasmus-plus.ec.europa.eu'
        },
        {
            'name': 'Commonwealth Shared Scholarships',
            'description': 'Commonwealth Shared Scholarships are for candidates from least developed and lower middle income Commonwealth countries, for full-time Master\'s study on selected courses at UK universities. These scholarships are offered under six CSC Development themes: Science and technology for development, Strengthening health systems, Promoting global prosperity, Strengthening resilience and response to crises, Access, inclusion and opportunity, Strengthening peace, security and governance.',
            'eligibility': 'From eligible Commonwealth country, permanent resident in eligible country, Bachelor degree with first class or upper second class, English proficiency, not studied in UK before, under 40 years old.',
            'deadline': datetime.now() + timedelta(days=random.randint(30, 75)),
            'funding_type': 'fully_funded',
            'country': 'UK',
            'university': 'Multiple UK Universities',
            'degree_level': 'masters',
            'gpa_requirement': 3.3,
            'application_link': 'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-shared-scholarships/',
            'source_url': 'https://cscuk.fcdo.gov.uk/',
            'source_name': 'cscuk.fcdo.gov.uk'
        }
    ]

    # Add sample data to database
    added_count = 0
    for scholarship in sample_scholarships:
        try:
            scholarship_id = db.add_scholarship(scholarship)
            if scholarship_id:
                added_count += 1
        except Exception as e:
            print(f"Error adding scholarship {scholarship['name']}: {e}")

    # Export to JSON
    db.export_to_json('data/scholarships.json')

    print(f"✅ Added {added_count} sample scholarships to database")
    print("📄 Exported to data/scholarships.json")
    return added_count

if __name__ == "__main__":
    create_sample_data()

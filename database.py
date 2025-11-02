from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class Scholarship(Base):
    __tablename__ = 'scholarships'

    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    eligibility = Column(Text)
    deadline = Column(DateTime)
    funding_type = Column(String(100))  # fully_funded, partial, etc.
    country = Column(String(100))
    university = Column(String(200))
    degree_level = Column(String(100))  # undergraduate, masters, phd
    gpa_requirement = Column(Float)
    application_link = Column(String(500))
    source_url = Column(String(500))
    source_name = Column(String(200))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    summary = Column(Text)  # AI-generated summary

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    email = Column(String(255))
    telegram_id = Column(String(100))
    preferences = Column(Text)  # JSON string of user preferences
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    last_notified = Column(DateTime)

class DatabaseManager:
    def __init__(self, database_url='sqlite:///scholarships.db'):
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_scholarship(self, scholarship_data):
        """Add a new scholarship to the database"""
        session = self.Session()
        try:
            scholarship = Scholarship(**scholarship_data)
            session.add(scholarship)
            session.commit()
            return scholarship.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_scholarships(self, filters=None, limit=None):
        """Retrieve scholarships with optional filters"""
        session = self.Session()
        try:
            query = session.query(Scholarship).filter(Scholarship.is_active == True)

            if filters:
                if 'country' in filters:
                    query = query.filter(Scholarship.country.ilike(f'%{filters["country"]}%'))
                if 'degree_level' in filters:
                    query = query.filter(Scholarship.degree_level.ilike(f'%{filters["degree_level"]}%'))
                if 'funding_type' in filters:
                    query = query.filter(Scholarship.funding_type.ilike(f'%{filters["funding_type"]}%'))
                if 'gpa_min' in filters:
                    query = query.filter(Scholarship.gpa_requirement >= filters['gpa_min'])
                if 'gpa_max' in filters:
                    query = query.filter(Scholarship.gpa_requirement <= filters['gpa_max'])
                if 'deadline_before' in filters:
                    query = query.filter(Scholarship.deadline <= filters['deadline_before'])

            if limit:
                query = query.limit(limit)

            return query.all()
        finally:
            session.close()

    def update_scholarship(self, scholarship_id, updates):
        """Update an existing scholarship"""
        session = self.Session()
        try:
            scholarship = session.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
            if scholarship:
                for key, value in updates.items():
                    if hasattr(scholarship, key):
                        setattr(scholarship, key, value)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def add_subscription(self, subscription_data):
        """Add a new subscription"""
        session = self.Session()
        try:
            subscription = Subscription(**subscription_data)
            session.add(subscription)
            session.commit()
            return subscription.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def export_to_json(self, filepath, filters=None):
        """Export scholarships to JSON file"""
        scholarships = self.get_scholarships(filters)
        data = []

        for scholarship in scholarships:
            scholarship_dict = {
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
                'summary': scholarship.summary
            }
            data.append(scholarship_dict)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return len(data)

    def get_subscriptions(self):
        """Get all subscriptions"""
        session = self.Session()
        try:
            return session.query(Subscription).all()
        finally:
            session.close()

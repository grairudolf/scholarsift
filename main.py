#!/usr/bin/env python3
"""
ScholarSift - Smart Scholarship Scraper
Main entry point for the scholarship scraping system
"""

import asyncio
import argparse
import sys
from datetime import datetime

from scraper import ScholarshipScraper
from database import DatabaseManager
from config import Config

class ScholarSift:
    def __init__(self):
        self.scraper = ScholarshipScraper()
        self.db = DatabaseManager()

    async def scrape_scholarships(self, urls=None, discovery_mode=False):
        """Main scraping function"""
        print("🚀 Starting ScholarSift scraping...")

        if urls is None:
            urls = Config.SEED_SOURCES

        if discovery_mode:
            print("🔍 Discovery mode enabled - finding new sources...")
            # This would be implemented in a future enhancement
            urls = Config.SEED_SOURCES

        print(f"📋 Scraping {len(urls)} sources...")
        scholarships = await self.scraper.scrape_multiple_urls(urls)

        if scholarships:
            print(f"✅ Found {len(scholarships)} potential scholarships")
            saved_count = self.scraper.save_scholarships(scholarships)
            print(f"💾 Saved {saved_count} scholarships to database")

            # Export to JSON
            export_count = self.db.export_to_json('data/scholarships.json')
            print(f"📄 Exported {export_count} scholarships to JSON")

            return saved_count
        else:
            print("❌ No scholarships found")
            return 0

    def get_scholarships(self, filters=None):
        """Retrieve scholarships with filters"""
        return self.db.get_scholarships(filters)

    def export_data(self, format='json', filters=None):
        """Export scholarship data"""
        if format.lower() == 'json':
            count = self.db.export_to_json('data/scholarships.json', filters)
            print(f"📄 Exported {count} scholarships to JSON")
        else:
            print("❌ Unsupported export format")

async def main():
    parser = argparse.ArgumentParser(description='ScholarSift - Smart Scholarship Scraper')
    parser.add_argument('--scrape', action='store_true', help='Scrape scholarships from sources')
    parser.add_argument('--urls', nargs='*', help='Specific URLs to scrape')
    parser.add_argument('--discovery', action='store_true', help='Enable discovery mode')
    parser.add_argument('--export', choices=['json', 'csv'], help='Export data')
    parser.add_argument('--filter-country', help='Filter by country')
    parser.add_argument('--filter-degree', choices=['undergraduate', 'masters', 'phd'], help='Filter by degree level')
    parser.add_argument('--filter-gpa', type=float, help='Minimum GPA requirement')

    args = parser.parse_args()

    app = ScholarSift()

    if args.scrape:
        saved = await app.scrape_scholarships(args.urls, args.discovery)
        if saved > 0:
            print(f"\n🎉 Successfully scraped and saved {saved} scholarships!")
        else:
            print("\n⚠️  No new scholarships were found or saved.")
        return

    if args.export:
        filters = {}
        if args.filter_country:
            filters['country'] = args.filter_country
        if args.filter_degree:
            filters['degree_level'] = args.filter_degree
        if args.filter_gpa:
            filters['gpa_min'] = args.filter_gpa

        app.export_data(args.export, filters)
        return

    # Default: show help
    parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())

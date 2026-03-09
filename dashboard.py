# dashboard.py - Job Application Results Dashboard
# Created by Vignesh Yadala

import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

class JobDashboard:
    def __init__(self):
        self.data_dir = Path("data")
        
    def get_latest_results(self):
        """Get the most recent results file"""
        csv_files = list(self.data_dir.glob("job_results_*.csv"))
        
        if not csv_files:
            print("❌ No results found! Run the bot first: python main.py")
            return None
        
        # Get most recent file
        latest_file = max(csv_files, key=os.path.getctime)
        return pd.read_csv(latest_file)
    
    def display_dashboard(self):
        """Display beautiful dashboard"""
        df = self.get_latest_results()
        
        if df is None or len(df) == 0:
            return
        
        print("\n" + "=" * 100)
        print("🎯 AI JOB APPLICATION BOT - RESULTS DASHBOARD")
        print("=" * 100)
        
        # Overall Statistics
        print("\n📊 OVERALL STATISTICS:")
        print("-" * 100)
        print(f"  Total Jobs Analyzed:        {len(df)}")
        print(f"  ✅ Applications Sent:        {df['applied'].sum() if 'applied' in df else 0}")
        print(f"  ⏭️  Jobs Skipped:             {len(df) - (df['applied'].sum() if 'applied' in df else 0)}")
        print(f"  📈 Average Match Score:      {df['match_score'].mean():.1f}%")
        print(f"  🎯 Highest Match Score:      {df['match_score'].max():.1f}%")
        print(f"  📉 Lowest Match Score:       {df['match_score'].min():.1f}%")
        
        # Match Score Distribution
        print("\n📊 MATCH SCORE DISTRIBUTION:")
        print("-" * 100)
        score_ranges = [
            ("🔥 Excellent (90-100%)", 90, 100),
            ("✅ Good (75-89%)", 75, 89),
            ("⚠️  Fair (60-74%)", 60, 74),
            ("❌ Poor (<60%)", 0, 59)
        ]
        
        for label, min_score, max_score in score_ranges:
            count = len(df[(df['match_score'] >= min_score) & (df['match_score'] <= max_score)])
            percentage = (count / len(df) * 100) if len(df) > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"  {label:25} {count:3} jobs {bar} {percentage:.1f}%")
        
        # Top 10 Best Matches
        print("\n🏆 TOP 10 BEST MATCHES:")
        print("-" * 100)
        top_jobs = df.nlargest(10, 'match_score')[['title', 'company', 'location', 'match_score', 'applied']]
        
        for idx, (_, job) in enumerate(top_jobs.iterrows(), 1):
            status = "✅ APPLIED" if job.get('applied', False) else "⏭️  SKIPPED"
            print(f"\n  {idx}. {job['title']}")
            print(f"     Company:  {job['company']}")
            print(f"     Location: {job['location']}")
            print(f"     Score:    {job['match_score']:.1f}% | {status}")
        
        # Applications Summary
        if 'applied' in df and df['applied'].sum() > 0:
            print("\n✅ APPLICATIONS SENT:")
            print("-" * 100)
            applied_jobs = df[df['applied'] == True][['title', 'company', 'location', 'match_score']]
            
            for idx, (_, job) in enumerate(applied_jobs.iterrows(), 1):
                print(f"\n  {idx}. {job['title']}")
                print(f"     Company:  {job['company']}")
                print(f"     Location: {job['location']}")
                print(f"     Score:    {job['match_score']:.1f}%")
        
        # Companies Analysis
        print("\n🏢 TOP COMPANIES (by number of jobs):")
        print("-" * 100)
        company_counts = df['company'].value_counts().head(10)
        for company, count in company_counts.items():
            print(f"  {company:50} {count} jobs")
        
        # Location Analysis
        print("\n📍 JOBS BY LOCATION:")
        print("-" * 100)
        location_counts = df['location'].value_counts().head(10)
        for location, count in location_counts.items():
            print(f"  {location:50} {count} jobs")
        
        # Role Analysis
        if 'search_role' in df.columns:
            print("\n🎯 JOBS BY ROLE:")
            print("-" * 100)
            role_counts = df['search_role'].value_counts()
            for role, count in role_counts.items():
                print(f"  {role:50} {count} jobs")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 100)
        
        avg_score = df['match_score'].mean()
        if avg_score >= 80:
            print("  🎉 Great job! You're a strong match for most positions.")
        elif avg_score >= 60:
            print("  👍 Good matches found. Consider tailoring your resume for better scores.")
        else:
            print("  ⚠️  Low average match score. Consider:")
            print("     - Updating your resume with more relevant skills")
            print("     - Searching for different roles that match your experience")
            print("     - Adding certifications or projects to strengthen your profile")
        
        applied_count = df['applied'].sum() if 'applied' in df else 0
        if applied_count == 0:
            print("  ⚠️  No applications sent. Try:")
            print("     - Lowering MIN_MATCH_SCORE in .env file")
            print("     - Searching for more job roles")
            print("     - Improving your resume")
        elif applied_count < 5:
            print(f"  ✅ {applied_count} applications sent. Keep going!")
        else:
            print(f"  🎉 Great! {applied_count} applications sent. Good progress!")
        
        print("\n" + "=" * 100)
        print("💾 Full results saved in: data/job_results_*.csv")
        print("📊 Run the bot again: python main.py")
        print("=" * 100 + "\n")

if __name__ == "__main__":
    dashboard = JobDashboard()
    dashboard.display_dashboard() 

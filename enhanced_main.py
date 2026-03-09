# enhanced_main.py - Advanced AI Job Application Bot with Web Interface Support
# Created by Vignesh Yadala
# Updated: December 2025 - Added web config support, interactive company selection

import os
import json
import time
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import google.generativeai as genai
import PyPDF2

# Load environment variables
load_dotenv()

class EnhancedJobApplicationBot:
    def __init__(self, config_file: Optional[str] = None):
        """Initialize bot with optional config file from web interface"""
        
        # Load web config if provided
        self.web_config = {}
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                self.web_config = json.load(f)
                print(f"✅ Loaded configuration from {config_file}")
        
        # API Keys and credentials
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.naukri_email = os.getenv("NAUKRI_EMAIL")
        self.naukri_password = os.getenv("NAUKRI_PASSWORD")
        
        # Job preferences (can be overridden by web config)
        self.desired_roles = self.web_config.get('roles') or os.getenv("DESIRED_ROLES", "Python Developer,Software Engineer").split(",")
        self.desired_locations = self.web_config.get('locations') or os.getenv("DESIRED_LOCATIONS", "Bangalore,Mumbai,Hyderabad,Chennai,Pune").split(",")
        self.min_experience = int(self.web_config.get('minExperience') or os.getenv("MIN_EXPERIENCE", "0"))
        self.max_experience = int(self.web_config.get('maxExperience') or os.getenv("MAX_EXPERIENCE", "5"))
        self.min_match_score = int(os.getenv("MIN_MATCH_SCORE", "75"))
        self.max_applications = int(os.getenv("MAX_APPLICATIONS_PER_DAY", "20"))
        
        # Selected companies from web interface
        self.selected_companies = self.web_config.get('companies', [])
        
        # Initialize Google Gemini
        if not self.api_key:
            print("❌ ERROR: GOOGLE_API_KEY not found in .env file!")
            sys.exit(1)
            
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Storage
        self.data_dir = Path("data")
        self.logs_dir = Path("logs")
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Load resume
        self.resume_text = self.load_resume()
        
        # Track applications
        self.applied_jobs_file = self.data_dir / "applied_jobs.json"
        self.applied_jobs = self.load_applied_jobs()
        
        # Results
        self.results = []
        self.applications_today = 0
        
        # Company career pages
        self.company_urls = {
            # Indian IT Giants
            'TCS': 'https://www.tcs.com/careers',
            'Infosys': 'https://www.infosys.com/careers/',
            'Wipro': 'https://careers.wipro.com/',
            'HCLTech': 'https://www.hcltech.com/careers',
            'Tech Mahindra': 'https://www.techmahindra.com/careers',
            'Accenture': 'https://www.accenture.com/in-en/careers',
            'Cognizant': 'https://careers.cognizant.com/',
            
            # FAANG + Big Tech
            'Google': 'https://careers.google.com/',
            'Microsoft': 'https://careers.microsoft.com/',
            'Amazon': 'https://www.amazon.jobs/',
            'Apple': 'https://www.apple.com/careers/',
            'Meta': 'https://www.metacareers.com/',
            'Oracle': 'https://www.oracle.com/in/careers/',
            'IBM': 'https://www.ibm.com/careers/',
        }

    def load_resume(self) -> str:
        """Load and extract text from resume PDF"""
        resume_path = self.data_dir / "resume.pdf"
        
        if not resume_path.exists():
            print("⚠️  Warning: resume.pdf not found in data folder!")
            return "No resume provided"
        
        try:
            with open(resume_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"❌ Error reading resume: {e}")
            return "Error reading resume"

    def load_applied_jobs(self) -> set:
        """Load previously applied job IDs"""
        if self.applied_jobs_file.exists():
            with open(self.applied_jobs_file, 'r') as f:
                return set(json.load(f))
        return set()

    def save_applied_job(self, job_id: str):
        """Save applied job ID"""
        self.applied_jobs.add(job_id)
        with open(self.applied_jobs_file, 'w') as f:
            json.dump(list(self.applied_jobs), f, indent=2)

    def log(self, message: str):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        log_file = self.logs_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + "\n")

    def display_company_menu(self) -> List[str]:
        """Display interactive company selection menu"""
        print("\n" + "=" * 80)
        print("🏢 COMPANY SELECTION MENU")
        print("=" * 80)
        
        companies = list(self.company_urls.keys())
        
        # Group companies by category
        indian_it = ['TCS', 'Infosys', 'Wipro', 'HCLTech', 'Tech Mahindra', 'Accenture', 'Cognizant']
        faang = ['Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Oracle', 'IBM']
        
        print("\n📋 Available Companies:")
        print("\n🇮🇳 Indian IT Giants:")
        for idx, company in enumerate(indian_it, 1):
            print(f"  {idx}. {company}")
        
        print("\n🌎 FAANG + Big Tech:")
        for idx, company in enumerate(faang, len(indian_it) + 1):
            print(f"  {idx}. {company}")
        
        print("\n" + "=" * 80)
        print("📝 Selection Options:")
        print("  • Enter numbers separated by commas (e.g., 1,3,5,8)")
        print("  • Type 'all' to select all companies")
        print("  • Type 'indian' for all Indian IT companies")
        print("  • Type 'faang' for all FAANG companies")
        print("  • Type 'naukri' to skip company sites and use only Naukri.com")
        print("  • Type 'none' to skip all company sites")
        print("=" * 80)
        
        while True:
            user_input = input("\n👉 Enter your selection: ").strip().lower()
            
            if user_input == 'all':
                selected = companies
                break
            elif user_input == 'indian':
                selected = indian_it
                break
            elif user_input == 'faang':
                selected = faang
                break
            elif user_input == 'naukri':
                selected = []
                print("\n✅ Using Naukri.com only")
                break
            elif user_input == 'none':
                selected = []
                print("\n✅ Skipping all company sites")
                break
            else:
                try:
                    # Parse comma-separated numbers
                    indices = [int(x.strip()) for x in user_input.split(',')]
                    selected = []
                    for idx in indices:
                        if 1 <= idx <= len(companies):
                            selected.append(companies[idx - 1])
                        else:
                            print(f"⚠️  Invalid number: {idx}")
                    
                    if selected:
                        break
                    else:
                        print("❌ No valid companies selected. Please try again.")
                except ValueError:
                    print("❌ Invalid input. Please enter numbers separated by commas.")
        
        if selected:
            print("\n✅ Selected Companies:")
            for company in selected:
                print(f"  ✓ {company}")
        
        print("=" * 80)
        return selected

    def analyze_job_with_ai(self, job_data: Dict) -> Dict:
        """Use Google Gemini to analyze job match"""
        prompt = f"""
You are a job matching AI assistant. Analyze this job posting and determine if it's a good match for the candidate.

JOB DETAILS:
Title: {job_data['title']}
Company: {job_data['company']}
Location: {job_data.get('location', 'Not specified')}
Experience Required: {job_data.get('experience', 'Not specified')}
Description: {job_data.get('description', 'Not available')[:1000]}

CANDIDATE RESUME:
{self.resume_text[:2000]}

ANALYSIS REQUIRED:
1. Calculate match score (0-100%) based on:
   - Skills match
   - Experience level match
   - Role relevance
   - Location preference

2. Provide brief reasoning (2-3 sentences)

3. Decision: Should we apply? (yes/no)

Respond in this exact format:
SCORE: [number]
REASONING: [your reasoning]
DECISION: [yes/no]
"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Parse response
            score_match = re.search(r'SCORE:\s*(\d+)', response_text)
            reasoning_match = re.search(r'REASONING:\s*(.+?)(?=DECISION:|$)', response_text, re.DOTALL)
            decision_match = re.search(r'DECISION:\s*(yes|no)', response_text, re.IGNORECASE)
            
            score = int(score_match.group(1)) if score_match else 50
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
            decision = decision_match.group(1).lower() == 'yes' if decision_match else False
            
            return {
                'match_score': score,
                'reasoning': reasoning,
                'should_apply': decision and score >= self.min_match_score
            }
            
        except Exception as e:
            self.log(f"❌ AI analysis error: {e}")
            return {
                'match_score': 0,
                'reasoning': f"Error: {str(e)}",
                'should_apply': False
            }

    def scrape_naukri_jobs(self, page, role: str, location: str) -> List[Dict]:
        """Scrape jobs from Naukri.com"""
        jobs = []
        
        try:
            role_slug = role.lower().replace(" ", "-")
            location_slug = location.lower().replace(" ", "-")
            search_url = f"https://www.naukri.com/{role_slug}-jobs-in-{location_slug}"
            
            self.log(f"🔍 Naukri: {role} in {location}")
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            page.wait_for_selector(".srp-jobtuple-wrapper", timeout=10000)
            job_cards = page.query_selector_all(".srp-jobtuple-wrapper")
            
            for idx, card in enumerate(job_cards[:10]):
                try:
                    title_elem = card.query_selector(".title")
                    company_elem = card.query_selector(".comp-name")
                    location_elem = card.query_selector(".locWdth")
                    exp_elem = card.query_selector(".expwdth")
                    link_elem = card.query_selector("a.title")
                    desc_elem = card.query_selector(".job-description")
                    
                    if not title_elem or not company_elem:
                        continue
                    
                    job_url = link_elem.get_attribute('href') if link_elem else ""
                    
                    job_data = {
                        'title': title_elem.inner_text().strip(),
                        'company': company_elem.inner_text().strip(),
                        'location': location_elem.inner_text().strip() if location_elem else location,
                        'experience': exp_elem.inner_text().strip() if exp_elem else "Not specified",
                        'url': job_url,
                        'job_id': f"naukri_{title_elem.inner_text().strip()}_{company_elem.inner_text().strip()}_{idx}".replace(" ", "_"),
                        'source': 'Naukri',
                        'search_role': role,
                        'search_location': location,
                        'description': desc_elem.inner_text().strip() if desc_elem else "Check job page for details"
                    }
                    
                    jobs.append(job_data)
                    self.log(f"  ✓ {job_data['title']} at {job_data['company']}")
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            self.log(f"❌ Error scraping Naukri: {e}")
        
        return jobs

    def scrape_company_careers(self, page, company_name: str, role: str) -> List[Dict]:
        """Scrape jobs from company career pages"""
        jobs = []
        
        try:
            career_url = self.company_urls.get(company_name)
            if not career_url:
                return jobs
            
            self.log(f"🔍 {company_name}: Checking career page...")
            page.goto(career_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Generic job card selectors (companies use different structures)
            job_selectors = [
                ".job-card", ".job-listing", ".career-card", ".position",
                "[data-job]", ".opportunity", ".opening", ".vacancy"
            ]
            
            job_cards = []
            for selector in job_selectors:
                try:
                    cards = page.query_selector_all(selector)
                    if cards and len(cards) > 0:
                        job_cards = cards[:10]  # Limit to 10
                        break
                except:
                    continue
            
            if not job_cards:
                self.log(f"  ⚠️  No standard job cards found on {company_name}")
                # Create a placeholder entry
                jobs.append({
                    'title': f'{role} - Check {company_name} Career Page',
                    'company': company_name,
                    'location': 'Multiple Locations',
                    'experience': 'Various',
                    'url': career_url,
                    'job_id': f"{company_name.lower().replace(' ', '_')}_manual_check",
                    'source': company_name,
                    'search_role': role,
                    'search_location': 'India',
                    'description': f'Visit {company_name} career page to search for {role} positions. This is a manual check entry.'
                })
                return jobs
            
            for idx, card in enumerate(job_cards):
                try:
                    # Try to extract job info
                    title = "Position Available"
                    link = career_url
                    
                    # Try various title selectors
                    title_selectors = ["h3", "h4", ".title", ".job-title", ".position-title"]
                    for sel in title_selectors:
                        try:
                            title_elem = card.query_selector(sel)
                            if title_elem:
                                title = title_elem.inner_text().strip()
                                break
                        except:
                            continue
                    
                    # Try to get link
                    try:
                        link_elem = card.query_selector("a")
                        if link_elem:
                            href = link_elem.get_attribute('href')
                            if href:
                                link = href if href.startswith('http') else career_url + href
                    except:
                        pass
                    
                    job_data = {
                        'title': title,
                        'company': company_name,
                        'location': 'India / Multiple Locations',
                        'experience': 'Check job details',
                        'url': link,
                        'job_id': f"{company_name.lower().replace(' ', '_')}_{idx}",
                        'source': company_name,
                        'search_role': role,
                        'search_location': 'India',
                        'description': f'Position at {company_name}. Visit link for full details.'
                    }
                    
                    jobs.append(job_data)
                    self.log(f"  ✓ {title}")
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            self.log(f"❌ Error scraping {company_name}: {e}")
        
        return jobs

    def login_to_naukri(self, page):
        """Login to Naukri.com"""
        try:
            self.log("🔐 Logging into Naukri.com...")
            page.goto("https://www.naukri.com/nlogin/login", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Try to fill email
            email_filled = False
            email_selectors = ["input#usernameField", "input[type='text']", "input[placeholder*='Email']"]
            
            for selector in email_selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem and elem.is_visible():
                        page.fill(selector, self.naukri_email, timeout=5000)
                        email_filled = True
                        self.log("  ✓ Email entered")
                        break
                except:
                    continue
            
            if not email_filled:
                self.log("⚠️  Could not auto-fill email. Please login manually.")
                self.log("⏸️  Press ENTER after logging in...")
                input()
                return True
            
            time.sleep(1)
            
            # Try to fill password
            password_filled = False
            password_selectors = ["input#passwordField", "input[type='password']"]
            
            for selector in password_selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem and elem.is_visible():
                        page.fill(selector, self.naukri_password, timeout=5000)
                        password_filled = True
                        self.log("  ✓ Password entered")
                        break
                except:
                    continue
            
            if not password_filled:
                self.log("⚠️  Could not auto-fill password. Please login manually.")
                self.log("⏸️  Press ENTER after logging in...")
                input()
                return True
            
            time.sleep(1)
            
            # Try to click login button
            login_selectors = ["button[type='submit']", "button.loginButton"]
            clicked = False
            
            for selector in login_selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem and elem.is_visible():
                        page.click(selector, timeout=5000)
                        clicked = True
                        self.log("  ✓ Login button clicked")
                        break
                except:
                    continue
            
            if not clicked:
                self.log("⚠️  Could not click login button. Please complete login manually.")
                self.log("⏸️  Press ENTER after logging in...")
                input()
                return True
            
            time.sleep(5)
            
            # Check if login was successful
            if "naukri.com/mnjuser/homepage" in page.url or "naukri.com/mnjuser" in page.url:
                self.log("✅ Login successful!")
                return True
            else:
                self.log("⚠️  Login verification unclear. Please verify manually.")
                self.log("⏸️  Press ENTER to continue...")
                input()
                return True
                
        except Exception as e:
            self.log(f"❌ Login error: {e}")
            self.log("⏸️  Press ENTER after manual login...")
            input()
            return True

    def run(self):
        """Main execution"""
        self.log("=" * 80)
        self.log("╔═══════════════════════════════════════════════════════════════════════════════╗")
        self.log("║           🤖 ENHANCED AI JOB APPLICATION BOT - MULTI COMPANY                 ║")
        self.log("║           👨‍💻 Developed by: Vignesh Yadala                                    ║")
        self.log("║           📅 Version: December 2025                                           ║")
        self.log("║           🚀 Powered by Google Gemini AI                                      ║")
        self.log("╚═══════════════════════════════════════════════════════════════════════════════╝")
        self.log("=" * 80)
        self.log(f"🎯 Target Roles: {', '.join(self.desired_roles)}")
        self.log(f"📍 Target Locations: {', '.join(self.desired_locations)}")
        self.log(f"📊 Min Match Score: {self.min_match_score}%")
        self.log(f"📝 Max Applications: {self.max_applications}")
        self.log("=" * 80)
        
        # Company selection (interactive or from web config)
        if self.selected_companies:
            self.log(f"✅ Using companies from web config: {', '.join(self.selected_companies)}")
            selected_companies = self.selected_companies
            use_naukri = 'naukri' in selected_companies
            selected_companies = [c for c in selected_companies if c != 'naukri']
        else:
            selected_companies = self.display_company_menu()
            use_naukri = True  # Default to using Naukri if no web config
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(
                    headless=False, 
                    channel="chrome",
                    args=['--start-maximized', '--window-size=1920,1080']
                )
            except:
                self.log("⚠️  Installing Chrome...")
                import subprocess
                subprocess.run(["playwright", "install", "chrome"])
                browser = p.chromium.launch(headless=False, channel="chrome")
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080},
                is_mobile=False
            )
            
            page = context.new_page()
            
            try:
                all_jobs = []
                
                # 1. Scrape Naukri.com (if selected)
                if use_naukri or 'naukri' in self.selected_companies:
                    self.login_to_naukri(page)
                    
                    self.log("\n🔍 PHASE 1: Scraping Naukri.com...")
                    for role in self.desired_roles:
                        for location in self.desired_locations:
                            jobs = self.scrape_naukri_jobs(page, role.strip(), location.strip())
                            all_jobs.extend(jobs)
                            time.sleep(2)
                else:
                    self.log("\n⏭️  PHASE 1: Skipped (Naukri not selected)")
                
                # 2. Scrape Selected Company Career Pages
                if selected_companies:
                    self.log(f"\n🔍 PHASE 2: Checking {len(selected_companies)} Selected Company Career Pages...")
                    for company_name in selected_companies:
                        if company_name in self.company_urls:
                            for role in self.desired_roles:
                                jobs = self.scrape_company_careers(page, company_name, role.strip())
                                all_jobs.extend(jobs)
                                time.sleep(3)
                else:
                    self.log("\n⏭️  PHASE 2: Skipped (No companies selected)")
                
                self.log(f"\n📊 Total jobs collected: {len(all_jobs)}")
                self.log("=" * 80)
                
                if len(all_jobs) == 0:
                    self.log("⚠️  No jobs found! Try selecting different companies or roles.")
                    return
                
                # Ask for confirmation (unless running from web)
                auto_apply = False
                if not self.web_config:
                    self.log("\n⚠️  Ready to analyze and apply to jobs?")
                    self.log("   Type 'yes' to auto-apply, 'no' to analyze only:")
                    user_input = input().strip().lower()
                    auto_apply = user_input == 'yes'
                    
                    if auto_apply:
                        self.log("✅ Auto-apply ENABLED!")
                    else:
                        self.log("✅ Analysis mode only - NO applications")
                else:
                    self.log("✅ Analysis mode - Review results on dashboard")
                
                self.log("=" * 80)
                
                # Analyze and apply
                applied_count = 0
                for idx, job in enumerate(all_jobs, 1):
                    if applied_count >= self.max_applications:
                        self.log(f"\n⚠️  Reached maximum applications limit ({self.max_applications})")
                        break
                    
                    self.log(f"\n[{idx}/{len(all_jobs)}] {job['title']} at {job['company']} ({job['source']})")
                    
                    analysis = self.analyze_job_with_ai(job)
                    
                    job.update({
                        'match_score': analysis['match_score'],
                        'reasoning': analysis['reasoning'],
                        'should_apply': analysis['should_apply'],
                        'applied': False,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    self.log(f"  📊 Match: {analysis['match_score']}% | {analysis['reasoning'][:80]}...")
                    
                    if auto_apply and analysis['should_apply']:
                        self.log(f"  🎯 Good match! Marking for application...")
                        job['applied'] = True
                        applied_count += 1
                    
                    self.results.append(job)
                    time.sleep(1)
                
                # Save results
                self.save_results()
                
                self.log("\n" + "=" * 80)
                self.log("✅ BOT COMPLETED!")
                self.log(f"📊 Analyzed: {len(self.results)}")
                self.log(f"🎯 High Matches: {sum(1 for r in self.results if r.get('should_apply', False))}")
                if self.results:
                    self.log(f"📈 Avg Score: {sum(r['match_score'] for r in self.results)/len(self.results):.1f}%")
                self.log("=" * 80)
                self.log("\n💡 View detailed results on the web dashboard!")
                
            except Exception as e:
                self.log(f"❌ Error: {e}")
                import traceback
                self.log(traceback.format_exc())
            finally:
                self.log("\n⏸️  Press ENTER to close browser...")
                if not self.web_config:
                    input()
                browser.close()

    def save_results(self):
        """Save results to CSV and JSON"""
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"job_results_{timestamp}.csv"
        df.to_csv(filename, index=False)
        self.log(f"💾 Results saved: {filename}")
        
        # Also save JSON for web interface
        json_file = self.data_dir / f"job_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)

if __name__ == "__main__":
    # Check if config file is provided (from web interface)
    config_file = None
    if len(sys.argv) > 2 and sys.argv[1] == '--config':
        config_file = sys.argv[2]
    
    bot = EnhancedJobApplicationBot(config_file=config_file)
    bot.run()
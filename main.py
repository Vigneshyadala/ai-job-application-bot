# main.py - Advanced AI Job Application Bot (Google Gemini + Chrome Version)
# Created by Vignesh Yadala
# Updated: December 2025 - Desktop Mode Fixed

import os
import json
import time
import re
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

class JobApplicationBot:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.naukri_email = os.getenv("NAUKRI_EMAIL")
        self.naukri_password = os.getenv("NAUKRI_PASSWORD")
        
        # Job preferences
        self.desired_roles = os.getenv("DESIRED_ROLES", "Python Developer").split(",")
        self.desired_locations = os.getenv("DESIRED_LOCATIONS", "Bangalore,Mumbai").split(",")
        self.min_experience = int(os.getenv("MIN_EXPERIENCE", "0"))
        self.max_experience = int(os.getenv("MAX_EXPERIENCE", "5"))
        self.min_match_score = int(os.getenv("MIN_MATCH_SCORE", "75"))
        self.max_applications = int(os.getenv("MAX_APPLICATIONS_PER_DAY", "10"))
        
        # Initialize Google Gemini
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
        """Scrape jobs from Naukri.com - ONLY COLLECT DATA, DON'T CLICK"""
        jobs = []
        
        try:
            # Build search URL
            role_slug = role.lower().replace(" ", "-")
            location_slug = location.lower().replace(" ", "-")
            search_url = f"https://www.naukri.com/{role_slug}-jobs-in-{location_slug}"
            
            self.log(f"🔍 Searching: {role} in {location}")
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Wait for job listings
            page.wait_for_selector(".srp-jobtuple-wrapper", timeout=10000)
            
            # Get all job cards
            job_cards = page.query_selector_all(".srp-jobtuple-wrapper")
            self.log(f"📋 Found {len(job_cards)} jobs")
            
            for idx, card in enumerate(job_cards[:15]):  # Limit to 15 jobs per search
                try:
                    # Extract job details WITHOUT CLICKING
                    title_elem = card.query_selector(".title")
                    company_elem = card.query_selector(".comp-name")
                    location_elem = card.query_selector(".locWdth")
                    exp_elem = card.query_selector(".expwdth")
                    link_elem = card.query_selector("a.title")
                    desc_elem = card.query_selector(".job-description, .desc, .ni-job-tuple-icon")
                    
                    if not title_elem or not company_elem:
                        continue
                    
                    job_url = link_elem.get_attribute('href') if link_elem else ""
                    
                    job_data = {
                        'title': title_elem.inner_text().strip(),
                        'company': company_elem.inner_text().strip(),
                        'location': location_elem.inner_text().strip() if location_elem else location,
                        'experience': exp_elem.inner_text().strip() if exp_elem else "Not specified",
                        'url': job_url,
                        'job_id': f"{title_elem.inner_text().strip()}_{company_elem.inner_text().strip()}_{idx}".replace(" ", "_"),
                        'source': 'naukri',
                        'search_role': role,
                        'search_location': location,
                        'description': desc_elem.inner_text().strip() if desc_elem else "Description will be fetched when applying"
                    }
                    
                    jobs.append(job_data)
                    self.log(f"  ✓ Extracted: {job_data['title']} at {job_data['company']}")
                    
                except Exception as e:
                    self.log(f"  ⚠️  Error extracting job {idx}: {e}")
                    continue
            
        except Exception as e:
            self.log(f"❌ Error scraping {role} in {location}: {e}")
        
        return jobs

    def apply_to_job(self, page, job_data: Dict) -> bool:
        """Attempt to apply to a job - ONLY IF SCORE IS HIGH"""
        try:
            # Check if already applied
            if job_data['job_id'] in self.applied_jobs:
                self.log(f"  ⏭️  Already applied to: {job_data['title']}")
                return False
            
            # Check daily limit
            if self.applications_today >= self.max_applications:
                self.log(f"  ⏸️  Daily application limit reached ({self.max_applications})")
                return False
            
            # Navigate to job page
            if not job_data.get('url'):
                self.log(f"  ❌ No URL for: {job_data['title']}")
                return False
            
            self.log(f"  🔗 Opening job: {job_data['url']}")
            page.goto(job_data['url'], wait_until="domcontentloaded", timeout=15000)
            time.sleep(3)
            
            # Look for apply button - try different selectors
            apply_selectors = [
                "button.btn-apply",
                "a.btn-apply",
                "button:has-text('Apply')",
                "a:has-text('Apply on Naukri')",
                ".apply-button",
                "#apply-button",
                "span:has-text('Apply')"
            ]
            
            apply_btn = None
            for selector in apply_selectors:
                try:
                    btn = page.query_selector(selector)
                    if btn and btn.is_visible():
                        apply_btn = btn
                        self.log(f"  ✓ Found apply button: {selector}")
                        break
                except:
                    continue
            
            if not apply_btn:
                self.log(f"  ⚠️  No apply button found for: {job_data['title']}")
                return False
            
            # Click apply button
            try:
                apply_btn.click()
                time.sleep(3)
                
                # Check if application was successful
                # Look for success message or confirmation
                success_indicators = [
                    "text=Application sent",
                    "text=Applied successfully",
                    "text=Your application has been submitted",
                    ".success-message"
                ]
                
                applied = False
                for indicator in success_indicators:
                    try:
                        if page.query_selector(indicator):
                            applied = True
                            break
                    except:
                        continue
                
                if applied or "applied" in page.url.lower():
                    self.log(f"  ✅ SUCCESS! Applied to: {job_data['title']} at {job_data['company']}")
                    self.save_applied_job(job_data['job_id'])
                    self.applications_today += 1
                    return True
                else:
                    # If we can't confirm, assume it worked (to avoid duplicates)
                    self.log(f"  ✅ Applied (unconfirmed) to: {job_data['title']} at {job_data['company']}")
                    self.save_applied_job(job_data['job_id'])
                    self.applications_today += 1
                    return True
                    
            except Exception as e:
                self.log(f"  ❌ Error clicking apply button: {e}")
                return False
            
        except Exception as e:
            self.log(f"  ❌ Error applying to {job_data['title']}: {e}")
            return False

    def login_to_naukri(self, page):
        """Login to Naukri.com"""
        try:
            self.log("🔐 Logging into Naukri.com...")
            page.goto("https://www.naukri.com/nlogin/login", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Try multiple selectors for email field
            email_selectors = [
                "input[type='text']",
                "input[placeholder*='Email']",
                "input[placeholder*='email']",
                "#usernameField",
                "input[name='email']"
            ]
            
            email_filled = False
            for selector in email_selectors:
                try:
                    if page.query_selector(selector):
                        page.fill(selector, self.naukri_email, timeout=5000)
                        self.log(f"  ✓ Email filled using selector: {selector}")
                        email_filled = True
                        break
                except:
                    continue
            
            if not email_filled:
                self.log("⚠️  Could not find email field. Please login manually in the browser window.")
                self.log("⏸️  Press ENTER after you've logged in manually...")
                input()
                return True
            
            time.sleep(1)
            
            # Try multiple selectors for password field
            password_selectors = [
                "input[type='password']",
                "input[placeholder*='Password']",
                "input[placeholder*='password']",
                "#passwordField",
                "input[name='password']"
            ]
            
            password_filled = False
            for selector in password_selectors:
                try:
                    if page.query_selector(selector):
                        page.fill(selector, self.naukri_password, timeout=5000)
                        self.log(f"  ✓ Password filled using selector: {selector}")
                        password_filled = True
                        break
                except:
                    continue
            
            if not password_filled:
                self.log("⚠️  Could not find password field. Please login manually.")
                self.log("⏸️  Press ENTER after you've logged in manually...")
                input()
                return True
            
            time.sleep(1)
            
            # Try to click login button
            login_selectors = [
                "button[type='submit']",
                "button:has-text('Login')",
                ".btn-primary",
                "button.loginButton"
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    if page.query_selector(selector):
                        page.click(selector, timeout=5000)
                        self.log(f"  ✓ Login button clicked")
                        login_clicked = True
                        break
                except:
                    continue
            
            if not login_clicked:
                self.log("⚠️  Could not find login button. Please click it manually.")
                self.log("⏸️  Press ENTER after you've logged in...")
                input()
                return True
            
            time.sleep(5)
            
            # Check if login successful
            if "naukri.com/mnjuser" in page.url or "naukri.com/mnj" in page.url:
                self.log("✅ Login successful!")
                return True
            else:
                self.log("⚠️  Waiting for login to complete...")
                self.log("⏸️  If you see CAPTCHA or need to verify, do it now.")
                self.log("⏸️  Press ENTER after you've logged in...")
                input()
                return True
                
        except Exception as e:
            self.log(f"❌ Login error: {e}")
            self.log("⏸️  Please login manually in the browser window.")
            self.log("⏸️  Press ENTER after you've logged in...")
            input()
            return True

    def run(self):
        """Main execution"""
        self.log("=" * 80)
        self.log("╔═══════════════════════════════════════════════════════════════════════════════╗")
        self.log("║                   🤖 ADVANCED AI JOB APPLICATION BOT                          ║")
        self.log("║                   👨‍💻 Developed by: Vignesh Yadala                              ║")
        self.log("║                   📅 Version: December 2025                                    ║")
        self.log("║                   🚀 Powered by Google Gemini AI                              ║")
        self.log("╚═══════════════════════════════════════════════════════════════════════════════╝")
        self.log("=" * 80)
        self.log(f"📧 Email: {self.naukri_email}")
        self.log(f"🎯 Target Roles: {', '.join(self.desired_roles)}")
        self.log(f"📍 Target Locations: {', '.join(self.desired_locations)}")
        self.log(f"📊 Min Match Score: {self.min_match_score}%")
        self.log(f"📝 Max Applications Today: {self.max_applications}")
        self.log("=" * 80)
        
        with sync_playwright() as p:
            # Launch Google Chrome browser in full desktop mode
            try:
                browser = p.chromium.launch(
                    headless=False, 
                    channel="chrome",
                    args=[
                        '--start-maximized',  # Open in full screen
                        '--window-size=1920,1080',  # Desktop resolution
                        '--disable-blink-features=AutomationControlled',  # Avoid bot detection
                        '--no-first-run',
                        '--no-default-browser-check',
                        '--disable-infobars'
                    ]
                )
            except Exception as e:
                self.log(f"⚠️  Chrome not found. Installing...")
                import subprocess
                subprocess.run(["playwright", "install", "chrome"])
                browser = p.chromium.launch(
                    headless=False, 
                    channel="chrome",
                    args=[
                        '--start-maximized',
                        '--window-size=1920,1080',
                        '--disable-blink-features=AutomationControlled',
                        '--no-first-run',
                        '--no-default-browser-check',
                        '--disable-infobars'
                    ]
                )
            
            # Create browser context with DESKTOP configuration
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                screen={'width': 1920, 'height': 1080},
                device_scale_factor=1,
                is_mobile=False,  # Critical: NOT a mobile device
                has_touch=False,  # Critical: NO touchscreen
                locale='en-US',
                timezone_id='Asia/Kolkata'
            )
            
            page = context.new_page()
            
            try:
                # Login
                if not self.login_to_naukri(page):
                    self.log("❌ Failed to login. Exiting.")
                    return
                
                # Search for jobs
                all_jobs = []
                for role in self.desired_roles:
                    for location in self.desired_locations:
                        jobs = self.scrape_naukri_jobs(page, role.strip(), location.strip())
                        all_jobs.extend(jobs)
                        time.sleep(2)  # Rate limiting
                
                self.log(f"\n📊 Total jobs found: {len(all_jobs)}")
                self.log("=" * 80)
                
                # Ask for confirmation before applying
                self.log("\n⚠️  IMPORTANT: The bot will now analyze jobs and apply to matching ones.")
                self.log(f"📝 Maximum applications today: {self.max_applications}")
                self.log(f"📊 Minimum match score: {self.min_match_score}%")
                self.log("\n🤔 Do you want to proceed with automatic applications?")
                self.log("   Type 'yes' to continue, or 'no' to just analyze without applying:")
                
                user_input = input().strip().lower()
                auto_apply = user_input == 'yes'
                
                if not auto_apply:
                    self.log("✅ Analysis mode only - will NOT apply to jobs automatically.")
                else:
                    self.log("✅ Auto-apply enabled - will apply to matching jobs!")
                
                self.log("=" * 80)
                
                # Analyze and apply
                applied_count = 0
                for idx, job in enumerate(all_jobs, 1):
                    # Stop if we hit the daily limit
                    if applied_count >= self.max_applications:
                        self.log(f"\n⏸️  Reached daily application limit ({self.max_applications}). Stopping.")
                        break
                    
                    self.log(f"\n[{idx}/{len(all_jobs)}] Analyzing: {job['title']} at {job['company']}")
                    
                    # AI analysis
                    analysis = self.analyze_job_with_ai(job)
                    
                    job.update({
                        'match_score': analysis['match_score'],
                        'reasoning': analysis['reasoning'],
                        'should_apply': analysis['should_apply'],
                        'applied': False,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    self.log(f"  📊 Match Score: {analysis['match_score']}%")
                    self.log(f"  💭 Reasoning: {analysis['reasoning'][:100]}...")
                    
                    # Apply ONLY if: auto_apply enabled + good match + below limit
                    if auto_apply and analysis['should_apply'] and applied_count < self.max_applications:
                        self.log(f"  🎯 GOOD MATCH! Attempting to apply...")
                        applied = self.apply_to_job(page, job)
                        job['applied'] = applied
                        
                        if applied:
                            applied_count += 1
                            self.log(f"  📊 Applications today: {applied_count}/{self.max_applications}")
                            time.sleep(5)  # Wait 5 seconds between applications
                    else:
                        if not auto_apply:
                            self.log(f"  ℹ️  Analysis only mode - not applying")
                        elif applied_count >= self.max_applications:
                            self.log(f"  ⏸️  Daily limit reached, skipping remaining jobs")
                        else:
                            self.log(f"  ⏭️  Skipping (score too low or not recommended)")
                    
                    self.results.append(job)
                    time.sleep(2)  # Rate limiting between job checks
                
                # Save results
                self.save_results()
                
                self.log("\n" + "=" * 80)
                self.log("✅ BOT COMPLETED!")
                self.log(f"📊 Total Analyzed: {len(self.results)}")
                self.log(f"✅ Applications Sent: {sum(1 for r in self.results if r.get('applied', False))}")
                self.log(f"📈 Average Match Score: {sum(r['match_score'] for r in self.results)/len(self.results):.1f}%")
                self.log("=" * 80)
                self.log("👨‍💻 Created with ❤️ by Vignesh Yadala")
                self.log("=" * 80)
                
            except Exception as e:
                self.log(f"❌ Fatal error: {e}")
                import traceback
                self.log(traceback.format_exc())
            finally:
                self.log("🔒 Closing browser...")
                browser.close()

    def save_results(self):
        """Save results to CSV"""
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"job_results_{timestamp}.csv"
        df.to_csv(filename, index=False)
        self.log(f"💾 Results saved to: {filename}")

if __name__ == "__main__":
    bot = JobApplicationBot()
    bot.run()
# 🤖 Advanced AI Job Application Bot

[![AI Powered](https://img.shields.io/badge/AI-Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-45ba4b?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)](https://github.com/Vigneshyadala/ai-job-application-bot)

### 🚀 Intelligent Job Matching & Automated Application System

*Revolutionizing job search with AI-powered matching, automated applications, and real-time analytics*

[🎯 Features](#-key-features) • [🏗 Architecture](#-system-architecture) • [🛠 Tech Stack](#-technology-stack) • [🚀 Setup](#-installation--setup) • [📊 Analytics](#-data-analytics)

---

**Version 2.0 | December 2025**

[![GitHub Stars](https://img.shields.io/github/stars/Vigneshyadala/ai-job-application-bot?style=social)](https://github.com/Vigneshyadala/ai-job-application-bot)
[![GitHub Forks](https://img.shields.io/github/forks/Vigneshyadala/ai-job-application-bot?style=social)](https://github.com/Vigneshyadala/ai-job-application-bot/fork)
[![Last Commit](https://img.shields.io/github/last-commit/Vigneshyadala/ai-job-application-bot)](https://github.com/Vigneshyadala/ai-job-application-bot/commits/main)

---

## 🎯 Problem Statement

Job seekers face significant challenges in today's competitive market:

| Challenge | Impact |
|-----------|--------|
| ⏰ **Time-consuming Manual Search** | Hours spent scrolling through dozens of job portals daily |
| 🔍 **Hard to Gauge Compatibility** | Difficult to know if your resume matches a job without deep analysis |
| 🔁 **Repetitive Applications** | Same information re-entered across multiple platforms |
| 📉 **No Intelligent Filtering** | Jobs shown regardless of experience, skills, or relevance |
| 📊 **No Tracking or Analytics** | Zero visibility into application history or success rates |

> **Result:** Wasted time, missed opportunities, and application fatigue.

---

## 💡 The Solution

A **comprehensive automation platform** that uses **Google Gemini AI** to intelligently discover, evaluate, and apply to jobs — with a full web dashboard and real-time analytics.

```
📄 Upload Resume → 🔍 Auto-Discover Jobs → 🧠 AI Match Score → ⚡ Auto-Apply → 📊 Track Results
```

---

## ✨ Key Features

### 🤖 AI-Powered Job Matching
- **Google Gemini 1.5 Flash** integration
- **0–100% match scoring** per job listing
- Detailed AI reasoning per recommendation
- Skills, experience & role compatibility analysis

### 🔍 Smart Job Discovery
- Multi-role simultaneous searching
- Cross-location job aggregation
- Experience-based filtering
- Company-specific scraping across **15+ platforms**

### ⚡ Automated Applications
- One-click multi-job application
- **Playwright** browser automation
- Auto-login & session management
- Success verification & tracking

### 📊 Professional Web Dashboard
- Real-time statistics display
- Interactive **Chart.js** visualizations
- Application history tracking
- Company-wise & location-wise analytics

### 📄 Resume Management
- Drag-and-drop PDF upload
- Automatic text extraction via **PyPDF2**
- Resume preview & validation
- Up to 16MB file support

### ⚙️ Configuration System
- Web-based settings editor
- Customizable match score thresholds
- Daily application limits
- Multi-company selection UI with category filters

---

## 🌐 Supported Platforms

### 🌐 Job Portal
| Platform | Description |
|----------|-------------|
| **Naukri.com** | India's #1 job portal — 70M+ registered users |

### 🇮🇳 Indian IT Giants (7)
| | | |
|--|--|--|
| TCS | Infosys | Wipro |
| HCLTech | Tech Mahindra | Accenture India |
| Cognizant | | |

### 🌎 FAANG + Big Tech (7)
| | | |
|--|--|--|
| Google | Microsoft | Amazon |
| Apple | Meta | Oracle |
| IBM | | |

---

## 🏗 System Architecture

### Core Components

| Component | File | Lines | Description |
|-----------|------|-------|-------------|
| 🤖 **Bot Engine** | `enhanced_main.py` | 689 | Orchestrates scraping, AI analysis & browser automation |
| 🌐 **Web Backend** | `app.py` | 487 | Flask REST API with 10+ endpoints |
| 🎨 **Dashboard UI** | `index.html` | 1,245 | Modern web interface with charts & control panel |
| 📊 **CLI Analytics** | `dashboard.py` | 143 | Terminal-based analytics for quick stats |

### Data Flow
```python
# Step 1: Resume Processing
Resume (PDF) → PyPDF2 → Extracted Text

# Step 2: Job Discovery
Job Portals → Playwright Browser → Job Data (JSON/CSV)

# Step 3: AI Analysis
Job Listing + Resume Text → Google Gemini 1.5 Flash → Match Score + Reasoning

# Step 4: Auto Application
High Match Jobs → Playwright Automation → Applied ✅

# Step 5: Results
All Data → CSV/JSON Storage → Dashboard Visualization
```

---

## 🛠 Technology Stack

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-45ba4b?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)

| Technology | Purpose | Version |
|------------|---------|---------|
| **Playwright** | Browser automation & web scraping | 1.40+ |
| **Flask** | Web server & REST API backend | 2.3.0 |
| **Google Gemini AI** | AI-powered job-resume matching | 1.5 Flash |
| **PyPDF2** | PDF resume text extraction | 3.0.1 |
| **Pandas** | Data analysis & CSV handling | 2.0.0 |
| **Chart.js** | Dashboard visualizations | 4.4.0 |
| **Python-dotenv** | Environment variable management | 1.0.0 |

---

## 💻 Technical Implementation

### 1. Resume Processing
```python
import PyPDF2

def extract_resume_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
```

### 2. AI Job Matching Engine
```python
import google.generativeai as genai

model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_job_with_ai(job_data, resume_text):
    prompt = f"""
    Analyze this job posting against the candidate resume:
    JOB: {job_data['title']} at {job_data['company']}
    LOCATION: {job_data['location']}
    RESUME: {resume_text[:2000]}
    
    Return: Match score (0-100%), reasoning, apply recommendation (yes/no)
    """
    response = model.generate_content(prompt)
    return parse_ai_response(response.text)
```

### 3. Playwright Web Scraping
```python
from playwright.sync_api import sync_playwright

def scrape_naukri_jobs(page, role, location):
    page.goto(f"https://www.naukri.com/{role}-jobs-in-{location}")
    job_cards = page.query_selector_all(".job-card")
    return [extract_job_data(card) for card in job_cards]
```

### 4. Flask API Endpoints
```
GET  /api/stats           → Application statistics
POST /api/resume/upload   → Upload resume PDF
POST /api/start-bot       → Start bot with config
GET  /api/bot-status      → Check bot running status
GET  /api/results         → Fetch job results
POST /api/stop-bot        → Stop the bot
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager
- Google Gemini API key (free tier available)
- Chrome/Chromium (auto-installed by Playwright)
- 4GB RAM minimum

### Step-by-Step

**1. Clone the repository**
```bash
git clone https://github.com/Vigneshyadala/ai-job-application-bot.git
cd ai-job-application-bot
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
playwright install chrome
```

**3. Configure `.env` file**
```env
GOOGLE_API_KEY=your_gemini_api_key_here
NAUKRI_EMAIL=your_email@example.com
NAUKRI_PASSWORD=your_password
DESIRED_ROLES=Python Developer,Software Engineer
DESIRED_LOCATIONS=Bangalore,Mumbai,Chennai
MIN_EXPERIENCE=0
MAX_EXPERIENCE=5
MIN_MATCH_SCORE=75
MAX_APPLICATIONS_PER_DAY=20
```

**4. Add your resume**
```bash
mkdir data
cp your_resume.pdf data/resume.pdf
```

**5. Launch the dashboard**
```bash
python app.py
```
Open browser at: **http://localhost:5000**

---

## 📖 Usage Guide

| Step | Action | Details |
|------|--------|---------|
| 1️⃣ | **Upload Resume** | Resume tab → drag & drop PDF |
| 2️⃣ | **Configure Settings** | Set Gemini API key, match threshold (75%), daily limit (20) |
| 3️⃣ | **Select Companies** | Choose from Naukri, Indian IT Giants, FAANG+ |
| 4️⃣ | **Set Job Preferences** | Roles, locations, experience range |
| 5️⃣ | **Start the Bot** | Click "Start Job Application Bot" |
| 6️⃣ | **View Results** | Overview tab → real-time charts & stats |

---

## 📊 Data Analytics

### Metrics Tracked

| Metric | Description |
|--------|-------------|
| Total Jobs Analyzed | All jobs scraped and evaluated |
| Applications Sent | Jobs where bot successfully applied |
| Average Match Score | Mean AI compatibility % across all jobs |
| Score Distribution | Poor / Fair / Good / Excellent breakdown |
| Company Distribution | Jobs per company |
| Location Analysis | Geographic job distribution |

### Match Score Ranges
```
🔥 Excellent  (90–100%)  → Auto-apply
✅ Good       (75–89%)   → Auto-apply  
⚠️  Fair       (60–74%)   → Skipped
❌ Poor        (< 60%)    → Skipped
```

### Dashboard Charts
- 📊 **Bar Chart** — Applications by company (top 10)
- 🍩 **Doughnut Chart** — Match score distribution
- 🥧 **Pie Chart** — Location-based breakdown
- 📈 **Line Chart** — Application timeline

### Export Formats
- **CSV** → `data/job_results_YYYYMMDD_HHMMSS.csv`
- **JSON** → `data/job_results_YYYYMMDD_HHMMSS.json`

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| ⚡ Jobs processed/minute | 10–15 |
| 🧠 AI analysis time | 2–3 seconds/job |
| 📄 PDF processing | < 1 second |
| 💾 RAM usage (typical) | 200–300 MB |
| 📦 Max jobs per session | 1,000+ |

---

## 📁 Project Structure

```
ai-job-application-bot/
│
├── enhanced_main.py        # 🤖 Main bot engine (689 lines)
├── app.py                  # 🌐 Flask web server (487 lines)
├── dashboard.py            # 📊 CLI analytics viewer (143 lines)
│
├── templates/
│   └── index.html          # 🎨 Web dashboard UI (1,245 lines)
│
├── data/
│   ├── resume.pdf          # 📄 Your resume
│   ├── job_results_*.csv   # 📋 Application results
│   └── applied_jobs.json   # ✅ Tracking file
│
├── logs/
│   └── bot_*.log           # 📝 Daily activity logs
│
├── .env                    # ⚙️ Configuration
├── requirements.txt        # 📦 Dependencies
└── README.md               # 📖 Documentation
```

---

## 🔐 Security & Privacy

| Practice | Details |
|----------|---------|
| ✅ Local Storage Only | All data stored on your machine — no cloud uploads |
| ✅ Encrypted API Calls | All Gemini API calls over HTTPS |
| ✅ Credential Safety | Passwords & keys in `.env` (git-ignored) |
| ✅ No Third-Party Sharing | Resume sent only to Google Gemini for analysis |
| ✅ Rate Limiting | Configurable limits prevent account flagging |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| ❌ Bot fails to start | Check `GOOGLE_API_KEY` in `.env`, verify Python 3.8+ |
| ❌ Resume upload fails | Ensure PDF < 16MB, contains searchable text (not scanned) |
| ❌ No jobs found | Try different roles/locations, select more companies |
| ❌ Charts not loading | Clear browser cache Ctrl+F5, check console F12 |
| ❌ Login fails | Verify Naukri email & password in `.env` |

---

## 🚀 Future Roadmap

| Feature | Phase |
|---------|-------|
| 🔗 LinkedIn Easy Apply | Phase 1 |
| 🌐 Indeed.com Support | Phase 1 |
| 📧 Daily Email Summary | Phase 1 |
| 📝 AI Cover Letter Generator | Phase 2 |
| 📱 React Native Mobile App | Phase 2 |
| ☁️ AWS/Heroku 24/7 Deployment | Phase 3 |
| 🔄 Interview Auto-Scheduler | Phase 3 |
| 📊 ML Predictive Analytics | Phase 3 |

---

## 📊 Project Stats

| | | | |
|--|--|--|--|
| 📝 **2,564** Lines of Code | 📁 **4** Core Files | 🔌 **10+** API Endpoints | 🏢 **15** Platforms |
| ⏱️ **40+** Dev Hours | 🤖 **100%** AI-Powered | ⚡ **10-15** Jobs/Min | 🎯 **0-100%** Match Score |

### Skills Demonstrated
1. **Web Scraping** — Playwright DOM automation
2. **AI Integration** — Google Gemini API
3. **Full-Stack Dev** — Flask + Vanilla JS frontend
4. **Data Analysis** — Pandas, CSV, statistics
5. **UI/UX Design** — Responsive web dashboard
6. **REST API** — Flask RESTful architecture
7. **Browser Automation** — Playwright session management
8. **File Handling** — PDF parsing, JSON/CSV storage

---

## 📜 License

MIT License — free for personal use with attribution.
Copyright © 2025 Vignesh Yadala

**⚠️ Ethical Usage**
- Provide accurate information in all applications
- Respect job portal rate limits
- Do not spam companies
- Use for genuine job search only

---

## 👨‍💻 Developer

### Vignesh Yadala

[![GitHub](https://img.shields.io/badge/GitHub-Vigneshyadala-181717?style=for-the-badge&logo=github)](https://github.com/Vigneshyadala)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-vignesh--yadala-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/vignesh-yadala)
[![Email](https://img.shields.io/badge/Email-vignesh.yadala%40gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:vignesh.yadala@gmail.com)
[![Phone](https://img.shields.io/badge/Phone-+91_9032478898-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](tel:+919032478898)

*Python | AI | Automation | Full-Stack Development*

---

### 🌟 If this project helped you, please give it a star! 🌟

> *"Automating success, one application at a time"* 🚀

**© 2025 Vignesh Yadala. All rights reserved.**

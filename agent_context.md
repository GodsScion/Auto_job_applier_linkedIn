# Auto Job Applier LinkedIn - Agent Context Documentation

## 📋 Project Overview

**Project Name:** LinkedIn AI Auto Job Applier  
**Repository:** [GodsScion/Auto_job_applier_linkedIn](https://github.com/GodsScion/Auto_job_applier_linkedIn)  
**Version:** 25.07.20.9.30 Community Alpha  
**Author:** Sai Vignesh Golla  
**License:** GNU Affero General Public License v3.0  
**Project Location:** `c:\Users\Sanjay\Desktop\Projects\AUTO APPLY\Auto_job_applier_linkedIn`

### Purpose
This is an advanced web scraping automation bot that streamlines the job application process on LinkedIn. It searches for relevant jobs, automatically fills out application forms, customizes resumes based on job requirements (skills, description, company info), and can apply to 100+ jobs in less than 1 hour.

### Key Capabilities
- Automated LinkedIn job search and application
- Intelligent question answering using AI (OpenAI, DeepSeek, Gemini)
- Custom resume generation based on job descriptions
- Company blacklisting and filtering
- Experience-based job filtering
- External application link collection
- Comprehensive application tracking and history
- Flask-based UI for managing applied jobs

---

## 👤 User Profile: Sanjay Nainwal

### Personal Information
- **Name:** Sanjay Nainwal
- **Location:** Dehradun, Uttarakhand, India (Zip: 248001)
- **Phone:** 9720423975
- **Email:** sanjaynainwal129@gmail.com
- **LinkedIn:** [https://www.linkedin.com/in/sanjay-nainwal/](https://www.linkedin.com/in/sanjay-nainwal/)
- **Portfolio:** [https://sanjaynainwal.vercel.app/](https://sanjaynainwal.vercel.app/)

### Professional Details
- **Current Position:** SDE-2 at BharatPe (Remote)
- **Years of Experience:** 5 years
- **Current Company:** BharatPe
- **Current CTC:** ₹37,00,000 (₹37 lakhs / ~₹3.08 lakhs per month)
- **Desired CTC:** ₹50,00,000 (₹50 lakhs / ~₹4.17 lakhs per month)
- **Notice Period:** Immediate (0 days)

### Professional Profile
- **Headline:** "Backend Engineer with Bachelors in Computer Science and 5+ years of experience"
- **Summary:** "I'm Sanjay Nainwal, a Software Development Engineer with 5 years of experience in backend development, currently based in Dehradun, India and working as an SDE-2 at BharatPe (Remote). I'm reaching out to explore backend engineering roles where I can leverage my expertise in large-scale data management, security, and high-performance systems."

### Demographics
- **Gender:** Male
- **Ethnicity:** Asian
- **Disability Status:** No
- **Veteran Status:** No
- **Citizenship:** Non-citizen allowed to work for any employer
- **Visa Sponsorship Required:** No
- **Education:** Bachelors in Computer Science
- **Masters Degree:** No

---

## 🎯 Job Search Configuration

### Target Positions
Sanjay is searching for the following roles:
1. Java
2. Backend Engineer
3. Software Engineer
4. Software Developer
5. Senior Software Engineer
6. Senior Backend Developer
7. SDE-3
8. SSE

### Geographic Preferences
**Search Locations (Randomized):**
- India
- United States
- Asia
- Australia
- Canada
- Europe
- UAE
- Middle East

**Search Location Randomization:** Enabled

### Job Search Filters

#### Applied Filters
- **Easy Apply Only:** Yes
- **Work Style:** Remote, Hybrid (preferred: remote)
- **Sort By:** Most relevant
- **Date Posted:** Past week
- **Salary Range:** Not specified
- **Switch After:** 20 applications per search term
- **Search Order:** Randomized

#### Experience Level
- Current experience: 5 years
- Open to all experience levels
- Will consider jobs requiring up to 7 years if Masters-related content found

#### Job Type
- Open to all job types (Full-time, Part-time, Contract, etc.)

#### Special Filters
- **Under 10 Applicants:** No
- **In Your Network:** No
- **Fair Chance Employer:** No

### Company Preferences

#### Blacklisted Companies
Companies to avoid (in About Company section):
- Crossover
- BharatPe (current employer)
- EPAM

#### Job Description Filters
Avoid jobs mentioning:
- "US Citizen" / "USA Citizen"
- "No C2C" / "No Corp2Corp"
- ".NET"
- "Embedded Programming"
- "PHP"
- "Ruby"
- "CNC"

#### Other Filters
- **Security Clearance:** Not available (will skip jobs requiring it)
- **Experience Filter:** Skip jobs requiring > 5 years (+ 2 if Masters mentioned)

---

## 🤖 AI Configuration

### AI Provider Setup
- **AI Enabled:** Currently disabled (`use_AI = False`)
- **Provider:** DeepSeek
- **API URL:** `https://api.deepseek.com/v1`
- **API Key:** `sk-c101c45ee7af44c19e77e9ff43f59bd9`
- **Model:** `deepseek-chat`
- **Stream Output:** Disabled

### AI Capabilities
When enabled, AI can:
- Answer unknown text questions
- Generate cover letters
- Extract skills from job descriptions
- Answer textarea questions
- Provide intelligent responses to application questions

---

## ⚙️ Bot Configuration

### Application Settings
- **Default Resume Path:** `all resumes/default/resume.pdf`
- **Follow Applied Companies:** No
- **Overwrite Previous Answers:** Yes
- **Pause Before Submit:** Yes
- **Pause At Failed Question:** Yes
- **Confidence Level:** 10/10

### Automation Settings
- **Run in Background:** No (visible browser)
- **Close External Tabs:** No
- **Disable Extensions:** Yes
- **Safe Mode:** No
- **Smooth Scroll:** No
- **Keep Screen Awake:** Yes
- **Stealth Mode:** No
- **Click Gap:** 1 second

### Continuous Operation
- **Run Non-Stop:** No
- **Alternate Sort By:** Yes
- **Cycle Date Posted:** Yes
- **Stop Date Cycle at 24hr:** No

### File Paths
- **Applied Jobs History:** `all excels/all_applied_applications_history.csv`
- **Failed Jobs History:** `all excels/all_failed_applications_history.csv`
- **Logs Folder:** `logs/`
- **Generated Resumes:** `all resumes/`

---

## 📂 Project Structure

```
Auto_job_applier_linkedIn/
├── config/                          # Configuration files
│   ├── personals.py                # Personal information
│   ├── questions.py                # Application question answers
│   ├── search.py                   # Job search preferences
│   ├── secrets.py                  # LinkedIn credentials & AI config
│   ├── settings.py                 # Bot behavior settings
│   └── resume.py                   # Resume generation config
├── modules/                        # Core functionality modules
│   ├── ai/                        # AI integration modules
│   │   ├── deepseekConnections.py # DeepSeek API integration
│   │   ├── geminiConnections.py   # Google Gemini integration
│   │   ├── openaiConnections.py   # OpenAI API integration
│   │   └── prompts.py             # AI prompt templates
│   ├── resumes/                   # Resume processing
│   │   ├── generator.py           # Resume generation
│   │   └── extractor.py           # Resume data extraction
│   ├── clickers_and_finders.py    # Selenium utilities
│   ├── helpers.py                 # Helper functions
│   ├── open_chrome.py             # Chrome browser automation
│   └── validator.py               # Configuration validation
├── templates/                      # Flask web UI templates
│   └── index.html                 # Job history UI
├── all excels/                    # Application tracking
│   ├── all_applied_applications_history.csv
│   └── all_failed_applications_history.csv
├── all resumes/                   # Resume storage
├── logs/                          # Application logs
├── runAiBot.py                    # Main automation script (1253 lines)
├── app.py                         # Flask web UI server
├── test.py                        # Testing utilities
├── test_gemini.py                 # Gemini AI testing
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

---

## 🔧 Technical Stack

### Core Dependencies
```
undetected-chromedriver    # Bypass anti-bot detection
selenium                   # Web automation
PyAutoGUI                  # GUI automation
flask                      # Web UI backend
flask-cors                 # CORS support
openai                     # AI integration
google-generativeai        # Gemini AI
setuptools                 # Python packaging
```

### Browser Requirements
- Google Chrome (latest version)
- ChromeDriver (automatically managed in stealth mode)

---

## 🚀 Key Features

### Automation Features
1. **Auto Login:** Uses saved credentials or manual login
2. **Smart Filtering:** Applies comprehensive job filters
3. **Intelligent Answering:** Auto-fills common questions
4. **Experience Matching:** Skips jobs with mismatched experience requirements
5. **Company Blacklisting:** Avoids unwanted companies
6. **External Job Tracking:** Collects non-Easy Apply job links
7. **Screenshot Capture:** Takes screenshots of failed applications
8. **Question Learning:** Saves and reuses previous answers

### Stealth Features
1. **Undetected ChromeDriver:** Bypasses anti-bot scripts
2. **Randomized Click Intervals:** Human-like behavior
3. **Smooth Scrolling:** Natural element interaction

### Data Collection
- Job ID, Title, Company, Location
- Work Style (Remote/Hybrid/On-site)
- HR Information (Name, LinkedIn)
- Application Date & Time
- Job Description & Requirements
- Skills Required
- Experience Required
- Application Link (Easy Apply & External)

### UI Features
- Flask-based web interface on `http://localhost:5000`
- View applied jobs history
- Update application dates
- Track external application links
- Filter and search applied jobs

---

## 📊 Application Workflow

1. **Initialization**
   - Validate configuration
   - Initialize AI client (if enabled)
   - Open Chrome browser
   - Login to LinkedIn

2. **Job Search**
   - Apply search filters
   - Randomize search terms (if enabled)
   - Iterate through search results

3. **Job Filtering**
   - Check against blacklisted companies
   - Verify experience requirements
   - Check for security clearance requirements
   - Scan for bad words in job description

4. **Application Process**
   - Click Easy Apply button
   - Upload resume
   - Answer all questions (select, radio, text, textarea, checkbox)
   - Use AI for unknown questions (if enabled)
   - Follow/unfollow company (based on config)
   - Submit application

5. **Data Recording**
   - Save to applied jobs CSV
   - Update application counters
   - Log any errors to failed jobs CSV
   - Capture screenshots on failure

6. **Pagination & Cycling**
   - Move to next page
   - Switch search terms after quota
   - Cycle through date filters
   - Alternate sorting methods

---

## 🎨 User-Specific Answer Mappings

### Common Question Responses
| Question Type | Sanjay's Answer |
|--------------|-----------------|
| Years of Experience | 5 |
| Visa Sponsorship | No |
| Current Location | Dehradun |
| Citizenship | Non-citizen allowed to work for any employer |
| Gender | Male |
| Disability Status | No |
| Veteran Status | No |
| Current Employer | BharatPe |
| Notice Period | Immediate (0 days) |
| Desired Salary | ₹50,00,000 |
| Current CTC | ₹37,00,000 |
| LinkedIn Profile | https://www.linkedin.com/in/sanjay-nainwal/ |
| Portfolio | https://sanjaynainwal.vercel.app/ |
| Confidence Level | 10 |

---

## 🔍 Important Notes

### Current Status
- ✅ Bot is configured and ready to use
- ⚠️ AI integration is currently **disabled**
- ⚠️ Resume path needs verification: `all resumes/default/resume.pdf`
- ✅ User profile is complete and detailed
- ✅ Search preferences are comprehensive

### Recommendations
1. Enable AI (`use_AI = True`) for better question answering
2. Verify default resume exists at configured path
3. Consider adjusting `current_experience` filter based on roles
4. Recommend testing with `pause_before_submit = True` initially
5. Monitor logs regularly for failed applications
6. Use Flask UI to track application history

### Security Considerations
- ⚠️ **CRITICAL:** LinkedIn credentials are stored in plain text in `config/secrets.py`
- ⚠️ **CRITICAL:** DeepSeek API key is exposed in `config/secrets.py`
- 🔒 Add `.gitignore` rules to prevent credential commits
- 🔒 Consider using environment variables for sensitive data

---

## 📝 Usage Commands

### Start the Bot
```bash
python runAiBot.py
```

### Start the Web UI
```bash
python app.py
# Then navigate to: http://localhost:5000
```

### Install Dependencies
```bash
pip install undetected-chromedriver pyautogui setuptools openai flask-cors flask
```

---

## 🤝 Project Attribution

**Original Author:** Sai Vignesh Golla  
**GitHub:** [@GodsScion](https://github.com/GodsScion)  
**LinkedIn:** [saivigneshgolla](https://www.linkedin.com/in/saivigneshgolla/)  
**Email:** saivigneshgolla@outlook.com

**Contributors:**
- Dheeraj Deshwal (@dheeraj9811)
- Yang Li (@MARKYangL)
- Tim L (@tulxoro)
- WINDY_WINDWARD (@karthik.sarode23)
- Karthik Sarode (UI for excel files)

---

## 📅 Recent Updates

### December 29, 2024
- Version: 24.12.29.12.30
- Updated configurations across all files
- Enhanced AI integration support
- Improved question answering logic

### November 28, 2024
- Patched for latest LinkedIn changes
- Follow/unfollow company selection feature
- AI frameworks added
- Skills extraction from job descriptions

---

## 🎯 Current User Goals

Based on the configuration, Sanjay is:
1. Seeking **Backend/Java engineering roles** primarily
2. Open to **remote or hybrid positions**
3. Targeting **global opportunities** (India, US, Asia, Australia, Canada, Europe, UAE, Middle East)
4. Looking for roles matching **5 years of experience**
5. Expecting salary around **₹50 lakhs annually**
6. Available for **immediate joining** (0 days notice)
7. Focusing on **most relevant jobs posted in the past week**
8. Willing to apply to **~20 jobs per search term** before switching

---

*This document was generated on January 18, 2026, to provide comprehensive context about the Auto Job Applier LinkedIn project and its configuration for Sanjay Nainwal.*

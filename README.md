# LinkedIn Auto Job Applier 🤖
This is an web scraping bot that automates the process of job applications on LinkedIn. It customizes your resume based on the collected job information, such as skills required, description, about company, etc. Answers all questions and applies to the job. 


## 📽️ See it in Action
[![Auto Job Applier demo video](https://github.com/GodsScion/Auto_job_applier_linkedIn/assets/100998531/429f7753-ebb0-499b-bc5e-5b4ee28c4f69)](https://youtu.be/gMbB1fWZDHw)
Click on above image to watch the demo or use this link https://youtu.be/gMbB1fWZDHw


## ✨ Content
- [Introduction](#linkedin-auto-job-applier-)
- [Demo Video](#%EF%B8%8F-see-it-in-action)
- [Index](#-content)
- [How to install](#%EF%B8%8F-how-to-install)
- [Feature List](#-feature-list)
  - [General Features](#general-features-)
  - [Stealth features](#stealth-features-)
  - [Upcoming Features](#upcoming-features-or-currently-in-development-%EF%B8%8F)
  - [Currently Broken](#currently-broken-)
- [My letter for YOU ❤️](#%EF%B8%8F-my-heartfelt-letter-to-you-%EF%B8%8F)
- [Update History](#%EF%B8%8F-update-history)
- [Disclaimer](#-disclaimer)
- [Terms and Conditions](#%EF%B8%8F-terms-and-conditions)
- [License](#%EF%B8%8F-license)
- [Socials](#-socials)
- [Support and Discussions](#-community-support-and-discussions)


## ⚙️ How to install
* [Python 3](https://www.python.org/) or above. Visit https://www.python.org/downloads/ to download and install Python, or for windows you could visit Microsoft Store and search for "Python". **Please make sure Python is added to Path in System Environment Variables**.
* Install necessary [Undetected Chromedriver](https://pypi.org/project/undetected-chromedriver/), [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) and [Setuptools](https://pypi.org/project/setuptools/) packages. After Python is installed, OPEN a console/terminal or shell, Use below command that uses the [pip](https://pip.pypa.io/en/stable) command-line tool to install these 3 package.
  ```
  pip install undetected-chromedriver pyautogui setuptools
  ```
* Download and install latest version of [Google Chrome](https://www.google.com/chrome) in it's default location, visit https://www.google.com/chrome to download it's installer.
* Clone the current git repo or download it as a zip file, url to the latest update https://github.com/GodsScion/Auto_job_applier_linkedIn.
* Download and install the appropriate [Chrome Driver](https://googlechromelabs.github.io/chrome-for-testing/) for Google Chrome and paste it in the location Chrome was installed, visit https://googlechromelabs.github.io/chrome-for-testing/ to download.
  <br> <br>
  ***OR*** 
  <br> <br>
  If you are using Windows, click on `windows-setup.bat` available in the `/setup` folder, this will install the latest chromedriver automatically.
* Open `config.py` file in `/setup` folder and enter your details, configure the tool as per your needs.
* Run `autoJobApplierLinkedIn.py` and see the magic happen.
* If you have questions or need help setting it up or to talk in general, join the github server: https://discord.gg/fFp7uUzWCY

## 🤩 Feature List
(I'm yet to complete the documentation, I'm adding in more features, still in development)

#### General Features 🚀:

- Opens browser with default logged in google account (Yet to test with browsers having multiple profiles)
- **Auto Login**: If configured or already saved in browser (not saved passwords)
- Apply filters (Salary, Companies, Experience Level,... ) Must config
- Region specific searches
- Opens job search and searches key words
- Easy applies
- Auto Answers questions answered in config
- Collects urls of career page if have to Apply externally
- Collects HR Info
- Collects skills required (In Development)
- Collects experience required and skips if not applicable to you, must be configured
- Auto Filters jobs based on your experience and black list key words
- Skips blacklisted jobs
- Can be configured to skip jobs requiring Security Clearance
- You can add exceptions to blacklist key words
- Only applies to filtered jobs
- Auto selects next pages until it hits the quota you configured
- Selects your default resume
- Auto Submits
- Saves all the info of applied jobs, failed to apply jobs in excels and logs
- Takes screenshot of questions answered to fail, for future debugging
- Saves info of all questions, it's options, previous answer and current answer in application
- Option to overwrite previous answers
- Continuous applications non stop (beta)
- No need for fear of missing out, Goes through all possible filters and sorts combinations with each cycle if configured (Most Recent, Most Relevant, Newest First, Past 24 Hrs, Past Month, Past Week etc)
- Option to randomize the search order
- Run in background, headless browser
- Auto collects a looooooooooooooooooot of info about your jobs, check applied-jobs.excel and failed_jobs.excel for info after each run.
- Optional pause before submit application.
- Optional pause if stuck at a question.




#### Stealth features 🥸🤫:  
- Undetected Chromedriver to bypass anti-bot scripts (Browser, Undetected ChromeDriver versions must be compatible) (Beta) {If problem occurs uninstall and install undetected chromedriver, update browser, selenium and chromedriver}
- Click intervals can be randomized and increased to avoid suspicions
- Smooth Scrolls the elements into view before click

#### Upcoming Features or currently in development 🤖🛠️:
- Answer questions with help of chatGpt or other LLMs
- Humanize clicks and mouse movements for stealth 
- Auto send personalized messages to HR that accept messages
- Custom resume generator based on Skills required gathering (In Development)
- Customize resume for every job using LLMs ChatGPT (In Development). (Halted decision pending, will probably implement api or utilize other LLMs or Web Scrape)

#### Currently Broken 🥲😭: 
- All ChatGPT features (depends on Undetected Chrome driver):
    - ChatGPT Login 
    - ChatGPT resume chat window opener
      
[back to index](#-content)

<br>




## ✉️ My Heartfelt letter to you ❤️...

My Dear User,

Thank you for using the job application tool! Your support means everything to me. 

As you continue your job search, I hope this tool has provided you with valuable assistance and streamlined your efforts.

To continue improving and maintaining this tool, I rely on the support of users like you. If you believe in its mission and want to contribute, you can support me by sharing about this project with your peers and network.

If you need a post to communicate about it: https://www.linkedin.com/posts/saivigneshgolla_jobsearch-jobapplication-careerdevelopment-activity-7166416367628341249-WE_8

By doing so, you can empower others in their job hunt, just as you've been empowered.. Every contribution, big or small, makes a significant impact!

As an independent developer, I pour my heart and soul into creating tools like this, driven by the genuine desire to make a positive impact. Your support, whether through donations or simply spreading the word, means the world to me and helps keep this project alive and thriving.

You can connect and reach me out at:
- LinkedIn  :  https://www.linkedin.com/in/saivigneshgolla/
- Email     :  saivigneshgolla@outlook.com

<br>

Thank you for being part of this journey, and remember that together, we can make a real difference in the lives of job seekers worldwide.

With heartfelt appreciation, <br>
**Sai Vignesh Golla**

<br>
<br>



## 🗓️ Update History:
### June 19, 2024
- Major Bug fixes (Text Area type questions)
- Made uploading default resume as not required

### May 15, 2024
- Added functionality for textarea type questions `summary`, `cover_letter`(Summary, Cover letter); checkbox type questions (acknowledgements)
- Added feature to skip irrelevant jobs based on `bad_words` 
- Improved performance for answering questions
- Logic change for masters students skipping
- Change variable names `blacklist_exceptions` -> `about_company_good_words` and `blacklist_words` -> `about_company_bad_words`
- Added session summary for logs
- Added option to turn off "Pause before Submit" until next run

### May 05, 2024
- For questions similar to "What is your current location?", City posted in Job description will be posted as the answer if `current_city` is left empty in the configuration
- Added option to over write previously saved answers for a question `overwrite_previous_answers`
- Tool will now save previous answer of a question
- Tool will now collect all available options for a Radio type or Select type question
- Major update in answering logic for Easy Apply Application questions
- Added Safe mode option for quick stable launches `safe_mode`

### May 04, 2024
- Added option to fill in "City, state, or zip code" search box `search_location`
- Bug fixes in answering City or location question


[back to index](#-content)

<br>

## 📜 Disclaimer

**This program is for educational purposes only. By downloading, using, copying, replicating, or interacting with this program or its code, you acknowledge and agree to abide by all the Terms, Conditions, Policies, and Licenses mentioned, which are subject to modification without prior notice. The responsibility of staying informed of any changes or updates bears upon yourself. For the latest Terms & Conditions, Licenses, or Policies, please refer to [Auto Job Applier](https://github.com/GodsScion/Auto_job_applier_linkedIn). Additionally, kindly adhere to and comply with LinkedIn's terms of service and policies pertaining to web scraping. Usage is at your own risk. The creators and contributors of this program emphasize that they bear no responsibility or liability for any misuse, damages, or legal consequences resulting from its usage.**


## 🏛️ Terms and Conditions

Please consider the following:

- **LinkedIn Policies**: LinkedIn has specific policies regarding web scraping and data collection. The responsibility to review and comply with these policies before engaging, interacting, or undertaking any actions with this program bears upon yourself. Be aware of the limitations and restrictions imposed by LinkedIn to avoid any potential violation(s).

- **No Warranties or Guarantees**: This program is provided as-is, without any warranties or guarantees of any kind. The accuracy, reliability, and effectiveness of the program cannot be guaranteed. Use it at your own risk.

- **Disclaimer of Liability**: The creators and contributors of this program shall not be held responsible or liable for any damages or consequences arising from the direct or indirect use, interaction, or actions performed with this program. This includes but is not limited to any legal issues, loss of data, or other damages incurred.

- **Use at Your Own Risk**: It is important to exercise caution and ensure that your usage, interactions, and actions with this program comply with the applicable laws and regulations. Understand the potential risks and consequences associated with web scraping and data collection activities.

- **Chrome Driver**: This program utilizes the Chrome Driver for web scraping. Please review and comply with the terms and conditions specified for [Chrome Driver](https://chromedriver.chromium.org/home).


## ⚖️ License

Copyright (C) 2024 Sai Vignesh Golla  <saivigneshgolla@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

See [AGPLv3 LICENSE](LICENSE) for more info.


<br>

## 🐧 Socials
- **LinkedIn** : https://www.linkedin.com/in/saivigneshgolla/
- **Email**    : saivigneshgolla@outlook.com
- **Discord**  : godsscion

## 🙌 Community Support and Discussions
- **Discord Server** : https://discord.gg/fFp7uUzWCY
- **GitHub**
    - [All Discussions](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions)
    - [Announcements](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/announcements)
    - [General](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/general)
    - [Feature requests or Ideas](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/feature-requests-or-ideas)
    - [Polls](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/polls)
    - [Community Flex](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/community-flex)
    - [Support Q&A](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/support-q-a)

---

[back to the top](#linkedin-auto-job-applier-)

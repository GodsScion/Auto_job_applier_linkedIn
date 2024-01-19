# LinkedIn Job Application Tool

**Disclaimer: This program is for educational purposes only. By downloading, using, copying, replicating, or interacting with this program or its code, you acknowledge and agree to abide by all the Terms, Conditions, Policies, and Licenses mentioned, which are subject to modification without prior notice. It is your responsibility to stay informed of any changes or updates. For the latest Terms & Conditions, Licenses, or Policies, please refer to [Auto Job Applier](https://github.com/GodsScion/Auto_job_applier_linkedIn). Additionally, kindly adhere to and comply with LinkedIn's terms of service and policies pertaining to web scraping. Usage is at your own risk. The creators and contributors of this program emphasize that they bear no responsibility or liability for any misuse, damages, or legal consequences resulting from its usage.**

## Introduction

This is a web scraping tool that automates the process of job applications on LinkedIn. It collects job listings information such as job titles, companies, URLs etc. from LinkedIn job search results. 

## Feature List (I'm yet to complete the documentation, I'm adding in more features)

**General Features:**

- Opens browser with default logged in google account (Yet to test with browsers having multiple profiles)
- **Auto Login**: If configged or already saved in browser (not saved passwords)
- Apply filters (Salary, Companies, Experience Level,... ) Must config
- Opens job search and searches key words
- Easy applies
- Auto Answers questions answered in config
- Collects urls of carrer page if have to Apply externally
- Collects HR Info
- Collects skills required (In Development)
- Collects experience required and skips if not applicable to you, must be configured
- Auto Filters jobs based on your experience and black list key words
- Only applies to filtered jobs
- Auto selects next pages until it hits the quota you configured
- Selects your default resume
- Auto Submits
- Saves all the info of applied jobs, failed to apply jobs in excels and logs
- Takes screenshot of questions answered to fail, for future debugging
- Saves info of all questions and answers for those questions
- Continuous applications non stop (beta)
- No need for fear of missing out, Goes through all possible filters and sorts combinations with each cycle if configged (Most Recent, Most Relevant, Newest First, Past 24 Hrs, Past Month, Past Week etc)
- Run in background, headless browser
- Auto collects a looooooooooooooooooooooot of info about your jobs, check applied-jobs.excel and failed_jobs.excel for info after each run.



**Stealth features:**  (Vetowed with lack of undetected chromedriver or stealth browsers 😭)
- Click intervals can be randomised and increased to avoid suspicions
- Scroll to view before click

**Upcoming Features or currently in developmnet:**
- Answer questions with help of chatGpt or other LLMS
- humanise and smoothen scroll speed and mouse movements for stealth 
- Auto send personalised messages to HR that accept messages
- Custom resume generator based on Skills required gathering (In Development)
- Customise resume for every job using LLMs ChatGPT (In Development). (Halted because of undetected-chromedriver is broken, ChatGPT is protected from bots and scraping 😑, will probably implement api or utilize other LLMs)

**Currently Broken 🥲:** 
- Undetected Chrome driver (Browser, Selenium version incomapatability) (Hot ptched, might work if compatable versions are installed)
  

## How to install


## Terms and Conditions

Please consider the following:

- **LinkedIn Policies**: LinkedIn has specific policies regarding web scraping and data collection. It is your responsibility to review and comply with these policies before engaging, interacting, or undertaking any actions with this program. Be aware of the limitations and restrictions imposed by LinkedIn to avoid any potential violation(s).

- **No Warranties or Guarantees**: This program is provided as-is, without any warranties or guarantees of any kind. The accuracy, reliability, and effectiveness of the program cannot be guaranteed. Use it at your own risk.

- **Disclaimer of Liability**: The creators and contributors of this program shall not be held responsible or liable for any damages or consequences arising from the direct or indirect use, interaction, or actions performed with this program. This includes but is not limited to any legal issues, loss of data, or other damages incurred.

- **Use at Your Own Risk**: It is important to exercise caution and ensure that your usage, interactions, and actions with this program comply with the applicable laws and regulations. Understand the potential risks and consequences associated with web scraping and data collection activities.

## Chrome Selenium Driver

This program utilizes the Chrome Selenium driver for web scraping. Please review and comply with the terms and conditions specified by the Chrome Selenium driver.

## A Heartfelt letter to you...
My Dear Ladies and Gentle Men,

Thank you for using the job application tool! Your support means everything to me. 

As you continue your job search, I hope this tool has provided you with valuable assistance and streamlined your efforts.

Sharing is caring! If you found this tool helpful, consider sharing it with your peers and network. By doing so, you can empower others in their job hunt, just as you've been empowered.

To continue improving and maintaining this tool, I rely on the support of users like you. If you believe in its mission and want to contribute, you can support me on <PATREON_LINK>. Every contribution, big or small, makes a significant impact!

As an independent developer, I pour my heart and soul into creating tools like this, driven by the genuine desire to make a positive impact. Your support, whether through donations or simply spreading the word, means the world to me and helps keep this project alive and thriving.

Thank you for being part of this journey, and remember that together, we can make a real difference in the lives of job seekers worldwide.

With heartfelt appreciation,
Sai Vignesh Golla

You can connect and reach me out at:
https://www.linkedin.com/in/saivigneshgolla/


## License

This program is released under the [MIT License](LICENSE).

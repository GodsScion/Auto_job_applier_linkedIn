# LinkedIn AI Auto Job Applier 🤖
This is a free, open-source tool that automates job applications on LinkedIn. It runs entirely on your own computer, using your own LinkedIn account. It finds jobs relevant to you, fills in the application questions, tailors your resume to each job's details (required skills, description, about the company, etc.), and applies. Can apply to 100+ jobs in under an hour. 


## 📽️ See it in Action
[![Auto Job Applier demo video](https://github.com/GodsScion/Auto_job_applier_linkedIn/assets/100998531/429f7753-ebb0-499b-bc5e-5b4ee28c4f69)](https://youtu.be/gMbB1fWZDHw)
Click on above image to watch the demo or use this link https://youtu.be/gMbB1fWZDHw


## ✨ Content
- [Introduction](#linkedin-ai-auto-job-applier-)
- [Demo Video](#%EF%B8%8F-see-it-in-action)
- [Index](#-content)
- [Easy start (recommended)](#-easy-start-recommended)
- [Install](#%EF%B8%8F-how-to-install)
- [Configure](#-how-to-configure)
- [Contributor Guidelines](#‍-contributor-guidelines)
- [Updates](%EF%B8%8F-major-updates-history)
- [Disclaimer](#-disclaimer)
- [Terms and Conditions](#%EF%B8%8F-terms-and-conditions)
- [License](#%EF%B8%8F-license)
- [Socials](#-socials)
- [Support and Discussions](#-community-support-and-discussions)

<br>

## 🚀 Easy start (recommended)

New here, or not comfortable editing code? Use the built-in control panel. You set everything up in your web browser and run the tool with a button - no editing Python files, no terminal commands.

1. **Install Python once.** Get it from https://www.python.org/downloads/ (on Windows, tick **"Add Python to PATH"** during install). You also need [Google Chrome](https://www.google.com/chrome).
2. **Download this project** (green "Code" button → "Download ZIP", then unzip; or clone it).
3. **Double-click the launcher for your system:**
    - **macOS:** `start.command`
    - **Windows:** `start.bat`
    - **Linux:** `start.sh` (run `./start.sh` in a terminal)

    The first run sets things up automatically (it may take a minute). After that it's quick.
4. Your browser opens the **control panel** automatically (the exact address, e.g. `http://127.0.0.1:5000`, is shown in the launcher window). Fill in the tabs - **Account, Profile, Search, Filters, Run settings** - and click **Save**.
5. Go to the **Run** tab and click **Start**. A Chrome window opens and begins applying - keep it in the foreground. You can watch progress in the log and click **Stop** any time.

Everything stays on your own computer: your details are saved locally in `user_config.json` (never uploaded), and the control panel is reachable only from this machine. If you prefer the classic setup, the manual steps below still work exactly as before.

[back to index](#-content)

<br>

## ⚙️ How to install

[![Auto Job Applier setup tutorial video](https://github.com/user-attachments/assets/9e876187-ed3e-4fbf-bd87-4acc145880a2)](https://youtu.be/f9rdz74e1lM?si=4fRBcte0nuvr6tEH)
Click on above image to watch the tutorial for installation and configuration or use this link https://youtu.be/f9rdz74e1lM (Recommended to watch it in 2x speed)

1. [Python 3.10](https://www.python.org/) or above. Visit https://www.python.org/downloads/ to download and install Python, or for windows you could visit Microsoft Store and search for "Python". **Please make sure Python is added to Path in System Environment Variables**.
2. Install the required Python packages. After Python is installed, open a console/terminal in the project folder and run the command below (it uses [pip](https://pip.pypa.io/en/stable) to install everything listed in `requirements.txt`).
  ```
  pip install -r requirements.txt
  ```
3. Download and install latest version of [Google Chrome](https://www.google.com/chrome) in it's default location, visit https://www.google.com/chrome to download it's installer.
4. Clone the current git repo or download it as a zip file, url to the latest update https://github.com/GodsScion/Auto_job_applier_linkedIn.
5. (Not needed if you set `auto_manage_driver = True` in `config/settings.py`, which downloads the matching driver for you automatically.) Otherwise, download the [Chrome Driver](https://googlechromelabs.github.io/chrome-for-testing/) that matches your Google Chrome version and place it where Chrome is installed. Visit https://googlechromelabs.github.io/chrome-for-testing/ to download.
  <br> <br>
  ***OR*** 
  <br> <br>
  If you are using Windows, click on `windows-setup.bat` available in the `/setup` folder, this will install the latest chromedriver automatically.
6. If you have questions or need help setting it up or to talk in general, join the github server: https://discord.gg/fFp7uUzWCY

[back to index](#-content)

<br>

## 🔧 How to configure
1. Open `personals.py` file in `/config` folder and enter your details like name, phone number, address, etc. Whatever you want to fill in your applications.
2. Open `questions.py` file in `/config` folder and enter your answers for application questions, configure wether you want the bot to pause before submission or pause if it can't answer unknown questions.
3. Open `search.py` file in `/config` folder and enter your search preferences, job filters, configure the bot as per your needs (these settings decide which jobs to apply for or skip).
4. Open `secrets.py` file in `/config` folder and enter your LinkedIn username, password to login and OpenAI API Key for generation of job tailored resumes and cover letters (This entire step is optional). If you do not provide username or password or leave them as default, it will login with saved profile in browser, if failed will ask you to login manually.
5. Open `settings.py` file in `/config` folder to configure settings like keep screen awake, click interval (time to wait between actions), run in background, automatic Chrome-driver management, etc. as per your needs.
6. (Optional) Don't forget to add you default resume in the location you mentioned in `default_resume_path = "all resumes/default/resume.pdf"` given in `/config/questions.py`. If one is not provided, it will use your previous resume submitted in LinkedIn or (In Development) generate custom resume if OpenAI APT key is provided!
7. Run `runAiBot.py` and see the magic happen.
8. To run the local control panel (settings, run controls, and Applied Jobs history), run `app.py` - it prints the address to open (e.g. `http://127.0.0.1:5000`, or another port if 5000 is busy).
8. If you have questions or need help setting it up or to talk in general, join the github server: https://discord.gg/fFp7uUzWCY

[back to index](#-content)

<br>


## 🧑‍💻 Contributor Guidelines
Thank you for your efforts and being a part of the community. All contributions are appreciated no matter how small or big. Once you contribute to the code base, your work will be remembered forever.

NOTE: Only Pull request to `community-version` branch will be accepted. Any other requests will be declined by default, especially to main branch.
Once your code is tested, your changes will be merged to the `main` branch in next cycle.

### Code Guidelines
  #### Functions:
  1. All functions or methods are named lower case and snake case
  2. Must have explanation of their purpose. Write explanation surrounded in `''' Explanation '''` under the definition `def function() -> None:`. Example:
      ```python
      def function() -> None:
        '''
        This function does nothing, it's just an example for explanation placement!
        '''
      ```
  4. The Types `(str, list, int, list[str], int | float)` for the parameters and returns must be given. Example:
      ```python
      def function(param1: str, param2: list[str], param3: int) -> str:
      ```
  5. Putting all that together some valid examples for function or method declarations would be as follows.
      ```python
      def function_name_in_camel_case(parameter1: driver, parameter2: str) -> list[str] | ValueError:
        '''
        This function is an example for code guidelines
        '''
        return [parameter2, parameter2.lower()]
      ```
  6. The hashtag comments on top of functions are optional, which are intended for developers `# Comments for developers`.
      ```python
      # Enter input text function
      def text_input_by_ID(driver: WebDriver, id: str, value: str, time: float=5.0) -> None | Exception:
          '''
          Enters `value` into the input field with the given `id` if found, else throws NotFoundException.
          - `time` is the max time to wait for the element to be found.
          '''
          username_field = WebDriverWait(driver, time).until(EC.presence_of_element_located((By.ID, id)))
          username_field.send_keys(Keys.CONTROL + "a")
          username_field.send_keys(value)
      
      ```
   
  #### Variables
  1. All variables must start with lower case, must be in explainable full words. If someone reads the variable name, it should be easy to understand what the variable stores.
  2. All local variables are camel case. Examples:
      ```python
      jobListingsElement = None
      ```
      ```python
      localBufferTime = 5.5
      ```
  3. All global variables are snake case. Example:
      ```
      total_runs = 1
      ```
  4. Mentioning types are optional.
      ```python
      localBufferTime: float | int = 5.5
      ```
  
  #### Configuration variables
  1. All config variables are treated as global variables. They have some extra guidelines.
  2. Must have variable setting explanation, and examples of valid values. Examples:
      ```python
      # Explanation of what this setting will do, and instructions to enter it correctly
      config_variable = "value1"    #  <Valid values examples, and NOTES> "value1", "value2", etc. Don't forget quotes ("")
      ```
      ```python
      # Do you want to randomize the search order for search_terms?
      randomize_search_order = False     # True of False, Note: True or False are case-sensitive
      ```
      ```python
      # Avoid applying to jobs if their required experience is above your current_experience. (Set value as -1 if you want to apply to all ignoring their required experience...)
      current_experience = 5             # Integers > -2 (Ex: -1, 0, 1, 2, 3, 4...)
      ```
      ```python
      # Search location, this will be filled in "City, state, or zip code" search box. If left empty as "", tool will not fill it.
      search_location = "United States"               # Some valid examples: "", "United States", "India", "Chicago, Illinois, United States", "90001, Los Angeles, California, United States", "Bengaluru, Karnataka, India", etc.

      ```
  4. Add the config variable in appropriate `/config/file`.
  5. Every config variable must be validated. Go to `/modules/validator.py` and add it over there. Example:
      For config variable `search_location = ""` found in `/config/search.py`, string validation is added in file `/modules/validator.py` under the method `def validate_search()`.
      ```python
      def validate_search() -> None | ValueError | TypeError:
          '''
          Validates all variables in the `/config/search.py` file.
          '''
          check_string(search_location, "search_location")
      ```

  [back to index](#-content)
  
  ### Attestation
  1. All contributions require proper attestion. Format for attestation:
  ```python
  ##> ------ <Your full name> : <github id> OR <email> - <Type of change> ------
      print("My contributions 😍") # Your code
  ##<
  ```
  2. Examples for proper attestation:
  New feature example
  ```python
  ##> ------ Sai Vignesh Golla : godsscion - Feature ------
  def alert_box(title: str, message: str) -> None:
    '''
    Shows an alert box with the given `title` and `message`.
    '''
    from pyautogui import alert
    return alert(title, message)

  ##<
  ```
  
  Bug fix example
  ```python
  def alert_box(title: str, message: str) -> None:
    '''
    Shows an alert box with the given `title` and `message`.
    '''
    from pyautogui import alert

  ##> ------ Sai Vignesh Golla : saivigneshgolla@outlook.com - Bug fix ------
    return alert(message, title)
  ##<
  ```

[back to index](#-content)

## 🗓️ Major Updates History:
### Jan 20, 2026
- You can now simultaneously use chrome, while bot continues applying in a new window

### Jul 20, 2024
- Contributions from community have been added
- Better AI support, minor bug fixes

### Nov 28, 2024
- Patched to work for latest changes in Linkedin.
- Users can now select to follow or not follow companies when submitting application.
- Frameworks for future AI Developments have been added.
- AI can now be used to extract skills from job description. 

### Oct 16, 2024
- Framework for OpenAI API and Local LLMs
- Framework for RAG

### Sep 09, 2024
- Smarter Auto-fill for salaries and notice periods
- Robust Search location filter, will work in window mode (No need for full screen)
- Better logic for Select and Radio type questions
- Proper functioning of Decline to answer questions in Equal Employment opportunity questions
- Checkbox questions select fail bug fixed
- Annotations are clearer in instructions for setup

### Sep 07, 2024
- Annotations for developers
- Robust input validations
- Restructured config file
- Fixed pagination bug

### Aug 21, 2024
- Performance improvements (skip clicking on applied jobs and blacklisted companies)
- Stop when easy apply application limit is reached
- Added ability to discard from pause at submission dialogue box
- Added support for address input
- Bug fixed radio questions, added support for physical disability questions
- Added framework for future config file updates

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

**This tool runs on your own computer and acts through your own accounts. It is provided free and open source, with no warranty of any kind. You are responsible for how you use it, including making sure your use complies with the terms of any website or service you use it with. The authors and contributors accept no liability for how it is used.**


## 🏛️ Terms and Conditions

Please consider the following:

- **LinkedIn Policies**: LinkedIn has policies regarding automated activity on its platform. It is your responsibility to review and comply with them before using this tool with your account.

- **No Warranties or Guarantees**: This program is provided as-is, without any warranties or guarantees of any kind. The accuracy, reliability, and effectiveness of the program cannot be guaranteed. Use it at your own risk.

- **Disclaimer of Liability**: The creators and contributors of this program shall not be held responsible or liable for any damages or consequences arising from the direct or indirect use, interaction, or actions performed with this program. This includes but is not limited to any legal issues, loss of data, or other damages incurred.

- **Use at Your Own Risk**: It is important to exercise caution and ensure that your usage, interactions, and actions with this program comply with applicable laws, regulations, and the terms of the services you use it with.

- **Chrome Driver**: This program uses the Chrome Driver to control your browser. Please review and comply with the terms and conditions specified for [Chrome Driver](https://chromedriver.chromium.org/home).


## ⚖️ License

Copyright (c) 2024-2026 Sai Vignesh Golla  <saivigneshgolla@outlook.com>

This project is licensed under the **MIT License**. You are free to use, copy, modify, and distribute it — including in commercial and closed-source work — as long as the copyright notice and permission notice are preserved. It is provided "as is", without warranty of any kind.

Releases before August 2026 were licensed under the AGPL-3.0. See [`NOTICE`](NOTICE) for the relicensing history, and the [`LICENSE`](LICENSE) file for the full MIT text.


<br>

[back to index](#-content)

<br>

## 🐧 Socials
- **LinkedIn** : https://www.linkedin.com/in/saivigneshgolla/
- **Email**    : saivigneshgolla@outlook.com
- **X/Twitter**: https://x.com/saivigneshgolla
- **Discord**  : godsscion


## 🙌 Community Support and Discussions
- **Discord Server** : https://discord.gg/fFp7uUzWCY
alternate link: https://discord.gg/ykfDjRFB
- **GitHub**
    - [All Discussions](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions)
    - [Announcements](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/announcements)
    - [General](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/general)
    - [Feature requests or Ideas](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/feature-requests-or-ideas)
    - [Polls](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/polls)
    - [Community Flex](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/community-flex)
    - [Support Q&A](https://github.com/GodsScion/Auto_job_applier_linkedIn/discussions/categories/support-q-a)


#### ℹ️ Version: 26.01.20.5.08

---

[back to the top](#linkedin-ai-auto-job-applier-)

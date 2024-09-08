'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

'''

import os
from time import sleep
from random import randint
from datetime import datetime, timedelta
from config.settings import logs_folder_path 


#### Common functions ####

#< Directories related
# Function to create missing directories
def make_directories(paths: list[str]) -> None:
    for path in paths:  
        path = path.replace("//","/")
        if '/' in path and '.' in path: path = path[:path.rfind('/')]
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except Exception as e:
            print(f'Error while creating directory "{path}": ', e)

# Function to search for Chrome Profiles
def find_default_profile_directory() -> str | None:
    # List of default profile directory locations to search
    default_locations = [
        r"%LOCALAPPDATA%\Google\Chrome\User Data",
        r"%USERPROFILE%\AppData\Local\Google\Chrome\User Data",
        r"%USERPROFILE%\Local Settings\Application Data\Google\Chrome\User Data"
    ]
    for location in default_locations:
        profile_dir = os.path.expandvars(location)
        if os.path.exists(profile_dir):
            return profile_dir
    return None
#>


#< Logging related
# Function to log critical errors
def critical_error_log(possible_reason: str, stack_trace: Exception) -> None:
    print_lg(possible_reason, stack_trace, datetime.now())

# Function to log and print
def print_lg(*msgs: str) -> None:
    try:
        message = "\n".join(str(msg) for msg in msgs)
        path = logs_folder_path+"/log.txt"
        with open(path.replace("//","/"), 'a+', encoding="utf-8") as file:
            file.write(message + '\n')
        print(message)
    except Exception as e:
        critical_error_log("Log.txt is open or is occupied by another program!", e)
#>


# Function to wait within a period of selected random range
def buffer(speed: int=0) -> None:
    if speed<=0:
        return
    elif speed <= 1 and speed < 2:
        return sleep(randint(6,10)*0.1)
    elif speed <= 2 and speed < 3:
        return sleep(randint(10,18)*0.1)
    else:
        return sleep(randint(18,round(speed)*10)*0.1)
    

# Function to ask and validate manual login
def manual_login_retry(is_logged_in: function, limit: int = 2) -> None:
    count = 0
    while not is_logged_in():
        from pyautogui import alert
        print_lg("Seems like you're not logged in!")
        button = "Confirm Login"
        message = 'After you successfully Log In, please click "{}" button below.'.format(button)
        if count > limit:
            button = "Skip Confirmation"
            message = 'If you\'re seeing this message even after you logged in, Click "{}". Seems like auto login confirmation failed!'.format(button)
        count += 1
        if alert(message, "Login Required", button) and count > limit: return


# Function to calculate date posted
def calculate_date_posted(time_string: str) -> datetime | None:
    time_string = time_string.strip()
    # print_lg(f"Trying to calculate date job was posted from '{time_string}'")
    now = datetime.now()
    if "second" in time_string:
        seconds = int(time_string.split()[0])
        date_posted = now - timedelta(seconds=seconds)
    elif "minute" in time_string:
        minutes = int(time_string.split()[0])
        date_posted = now - timedelta(minutes=minutes)
    elif "hour" in time_string:
        hours = int(time_string.split()[0])
        date_posted = now - timedelta(hours=hours)
    elif "day" in time_string:
        days = int(time_string.split()[0])
        date_posted = now - timedelta(days=days)
    elif "week" in time_string:
        weeks = int(time_string.split()[0])
        date_posted = now - timedelta(weeks=weeks)
    elif "month" in time_string:
        months = int(time_string.split()[0])
        date_posted = now - timedelta(days=months * 30)
    elif "year" in time_string:
        years = int(time_string.split()[0])
        date_posted = now - timedelta(days=years * 365)
    else:
        date_posted = None
    return date_posted
    









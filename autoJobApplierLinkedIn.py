from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def apply_to_jobs(keywords):
    # Set up WebDriver (assuming you have the appropriate driver executable in your PATH)
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    
    # Track the job application history
    application_history = []
    
    for keyword in keywords:
        url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
        driver.get(url)
        
        # Wait until job listings are loaded
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "job-card-container")))
        
        # Find all job listings
        job_listings = driver.find_elements(By.CLASS_NAME, "job-card-container")
        
        for job in job_listings:
            # Extract job details
            title = job.find_element(By.CLASS_NAME, "job-card-search__title").text
            company = job.find_element(By.CLASS_NAME, "job-card-container__company-name").text
            apply_button = job.find_element(By.CLASS_NAME, "job-card-container__apply-method")
            application_link = apply_button.get_attribute("href")
            
            # Check if job has already been applied
            if application_link in application_history:
                continue
            
            # Click on "Quick Apply" button
            apply_button.click()
            
            # Complete the application process (fill out forms, upload resume, etc.)
            # You'll need to identify the necessary form fields and interact with them using Selenium
            
            # Once the application is submitted successfully, add the application link to the history
            application_history.append(application_link)
            
            # Go back to the job listings page
            driver.back()
        
    # Close the browser
    driver.quit()

# Example usage
keywords = ["Junior Software Engineer", "Entry level Software Developer", "ReactJs Developer"]
apply_to_jobs(keywords)

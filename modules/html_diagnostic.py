"""
HTML Capture Diagnostic Tool for Recruiter Messaging
This script captures the actual HTML from job pages to verify "Meet the hiring team" section
"""

import os
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

def save_job_page_html(driver: WebDriver, job_id: str, job_title: str, company: str):
    """
    Saves the current job page HTML to a file for analysis
    """
    try:
        # Create directory for HTML dumps
        html_dir = "debug_html_dumps"
        if not os.path.exists(html_dir):
            os.makedirs(html_dir)
        
        # Get page source
        page_html = driver.page_source
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        filename = f"{html_dir}/{timestamp}_{job_id}_{safe_title}.html"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(page_html)
        except UnicodeEncodeError:
            # Fall back to latin-1 encoding for problematic characters
            with open(filename, 'w', encoding='latin-1', errors='replace') as f:
                f.write(page_html)
        
        # Check if "Meet the hiring team" exists in HTML
        has_meet_team = "Meet the hiring team" in page_html
        has_heading_medium = 'class="text-heading-medium' in page_html
        has_artdeco_card = 'class="job-details-people-who-can-help__section--two-pane artdeco-card' in page_html
        has_jobs_poster_name = 'jobs-poster__name' in page_html
        has_entry_point = 'class="entry-point' in page_html
        
        # Create analysis file
        analysis_file = f"{html_dir}/ANALYSIS_{timestamp}.txt"
        try:
            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write(f"HTML Analysis for: {job_title} at {company}\n")
                f.write(f"Job ID: {job_id}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"HTML File: {filename}\n")
                f.write(f"\n{'='*60}\n\n")
                f.write("CHECKLIST - Does HTML contain:\n")
                f.write(f"  [{'YES' if has_meet_team else 'NO'}] 'Meet the hiring team' text\n")
                f.write(f"  [{'YES' if has_heading_medium else 'NO'}] 'text-heading-medium' class\n")
                f.write(f"  [{'YES' if has_artdeco_card else 'NO'}] 'artdeco-card' class\n")
                f.write(f"  [{'YES' if has_jobs_poster_name else 'NO'}] 'jobs-poster__name' class\n")
                f.write(f"  [{'YES' if has_entry_point else 'NO'}] 'entry-point' class\n")
                f.write(f"\n{'='*60}\n\n")

                if has_meet_team:
                    f.write("SUCCESS: HTML HAS 'Meet the hiring team' section!\n")
                    f.write("If XPath still fails, there's a selector bug.\n")
                else:
                    f.write("SKIP: HTML does NOT have 'Meet the hiring team' section.\n")
                    f.write("Bot correctly skipped - no recruiter visible on this job.\n")

                # Extract the section if it exists
                if has_meet_team:
                    f.write(f"\n{'='*60}\n")
                    f.write("Searching for the section in HTML...\n\n")

                    # Find the section
                    start_idx = page_html.find("Meet the hiring team")
                    if start_idx > 0:
                        # Go back to find the start of the section
                        section_start = page_html.rfind("<div", max(0, start_idx - 2000), start_idx)
                        # Find the end of section
                        section_end = page_html.find("</div>", start_idx, start_idx + 5000)

                        if section_start > 0 and section_end > 0:
                            section_html = page_html[section_start:section_end + 6]
                            f.write("HTML SECTION FOUND:\n")
                            f.write(section_html[:2000])  # First 2000 chars
                            f.write("\n...\n")
        except UnicodeEncodeError:
            # Fall back to latin-1 encoding for analysis file
            with open(analysis_file, 'w', encoding='latin-1', errors='replace') as f:
                f.write(f"HTML Analysis for: {job_title} at {company}\n")
                f.write(f"Job ID: {job_id}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"HTML File: {filename}\n")
                f.write(f"\n{'='*60}\n\n")
                f.write("CHECKLIST - Does HTML contain:\n")
                f.write(f"  [{'YES' if has_meet_team else 'NO'}] 'Meet the hiring team' text\n")
                f.write(f"  [{'YES' if has_heading_medium else 'NO'}] 'text-heading-medium' class\n")
                f.write(f"  [{'YES' if has_artdeco_card else 'NO'}] 'artdeco-card' class\n")
                f.write(f"  [{'YES' if has_jobs_poster_name else 'NO'}] 'jobs-poster__name' class\n")
                f.write(f"  [{'YES' if has_entry_point else 'NO'}] 'entry-point' class\n")
                f.write(f"\n{'='*60}\n\n")

                if has_meet_team:
                    f.write("SUCCESS: HTML HAS 'Meet the hiring team' section!\n")
                    f.write("If XPath still fails, there's a selector bug.\n")
                else:
                    f.write("SKIP: HTML does NOT have 'Meet the hiring team' section.\n")
                    f.write("Bot correctly skipped - no recruiter visible on this job.\n")
        
        print(f"SUCCESS: HTML saved: {filename}")
        print(f"SUCCESS: Analysis saved: {analysis_file}")
        print(f"   Has 'Meet the hiring team': {has_meet_team}")

        return filename, has_meet_team

    except Exception as e:
        print(f"ERROR: Failed to save HTML: {e}")
        return None, False


def check_xpath_on_saved_html(html_file: str):
    """
    Test XPath selectors on saved HTML file using a real browser
    """
    print(f"\n{'='*60}")
    print(f"Testing XPath on: {html_file}")
    print(f"{'='*60}\n")
    
    # This would require loading the HTML into a driver
    # For now, just manual file inspection is needed
    print("MANUAL VERIFICATION NEEDED:")
    print(f"1. Open: {html_file}")
    print("2. Search for: 'Meet the hiring team'")
    print("3. Check if classes match:")
    print("   - text-heading-medium")
    print("   - artdeco-card")
    print("   - jobs-poster__name")
    print("   - entry-point")

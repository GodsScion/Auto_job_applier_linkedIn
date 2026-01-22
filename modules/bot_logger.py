'''
Bot Session Logger - Comprehensive logging for debugging and improvement
Logs every step, action, and HTML snapshot the bot takes.
'''

import os
from datetime import datetime
from typing import Optional

# Session-specific log directory
_session_dir = None
_session_log_file = None
_step_counter = 0

def init_session_logger():
    '''Initialize a new logging session with timestamp-based directory'''
    global _session_dir, _session_log_file, _step_counter
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    _session_dir = f"logs/sessions/session_{timestamp}"
    os.makedirs(_session_dir, exist_ok=True)
    os.makedirs(f"{_session_dir}/html_snapshots", exist_ok=True)
    
    _session_log_file = f"{_session_dir}/session_log.txt"
    _step_counter = 0
    
    # Write session header
    with open(_session_log_file, 'w', encoding='utf-8') as f:
        f.write(f"=" * 80 + "\n")
        f.write(f"BOT SESSION LOG - Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"=" * 80 + "\n\n")
    
    return _session_dir

def log_step(action: str, details: str = "", level: str = "INFO"):
    '''Log a step with incremental step number'''
    global _step_counter
    
    if not _session_log_file:
        init_session_logger()
    
    _step_counter += 1
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    log_entry = f"[{timestamp}] STEP {_step_counter:04d} | {level:5s} | {action}"
    if details:
        log_entry += f"\n         └─ {details}"
    log_entry += "\n"
    
    try:
        with open(_session_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except:
        pass
    
    # Also print to console for real-time feedback
    print(f"📋 [{_step_counter:04d}] {action}")

def log_html_snapshot(driver, name: str, reason: str = ""):
    '''Save HTML snapshot at current state'''
    global _step_counter
    
    if not _session_dir:
        init_session_logger()
    
    try:
        timestamp = datetime.now().strftime("%H%M%S")
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in name[:50])
        filename = f"{_session_dir}/html_snapshots/step_{_step_counter:04d}_{timestamp}_{safe_name}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"<!-- SNAPSHOT: {name} -->\n")
            f.write(f"<!-- REASON: {reason} -->\n")
            f.write(f"<!-- TIME: {datetime.now().isoformat()} -->\n")
            f.write(f"<!-- URL: {driver.current_url} -->\n")
            f.write("<!-- ===================================== -->\n\n")
            f.write(driver.page_source)
        
        log_step(f"HTML_SNAPSHOT: {safe_name}", f"Saved to: {filename}")
        return filename
    except Exception as e:
        log_step(f"HTML_SNAPSHOT_FAILED: {name}", str(e), level="ERROR")
        return None

def log_action(action: str, element_info: str = "", success: bool = True):
    '''Log an action like click, type, etc.'''
    status = "✅" if success else "❌"
    level = "INFO" if success else "ERROR"
    log_step(f"{status} {action}", element_info, level)

def log_decision(decision: str, reason: str):
    '''Log a decision point (e.g., skip job, proceed with application)'''
    log_step(f"🔀 DECISION: {decision}", reason, level="INFO")

def log_error(error: str, details: str = ""):
    '''Log an error'''
    log_step(f"❌ ERROR: {error}", details, level="ERROR")

def log_job_start(job_title: str, job_id: str, company: str):
    '''Log start of processing a job'''
    log_step(f"📌 JOB START: {job_title}", f"ID: {job_id} | Company: {company}")
    
def log_job_end(job_title: str, result: str):
    '''Log end of processing a job'''
    log_step(f"📌 JOB END: {job_title}", f"Result: {result}")

def log_recruiter_action(recruiter_name: str, action: str, result: str = ""):
    '''Log recruiter messaging action'''
    log_step(f"👤 RECRUITER: {recruiter_name}", f"Action: {action} | Result: {result}")

def log_section_separator(title: str):
    '''Add a visual section separator'''
    if not _session_log_file:
        return
    try:
        with open(_session_log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "-" * 60 + "\n")
            f.write(f">>> {title} <<<\n")
            f.write("-" * 60 + "\n\n")
    except:
        pass

def get_session_summary():
    '''Get summary of current session'''
    return {
        'session_dir': _session_dir,
        'log_file': _session_log_file,
        'total_steps': _step_counter
    }

def finalize_session(summary_stats: dict = None):
    '''Write session summary and close'''
    if not _session_log_file:
        return
    
    try:
        with open(_session_log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"SESSION ENDED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"TOTAL STEPS: {_step_counter}\n")
            if summary_stats:
                f.write("\nSUMMARY STATS:\n")
                for key, value in summary_stats.items():
                    f.write(f"  {key}: {value}\n")
            f.write("=" * 80 + "\n")
    except:
        pass

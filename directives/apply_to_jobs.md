# Directive: Apply to Jobs

## Goal
Automate the process of applying to jobs on LinkedIn using the `Auto_job_applier_linkedIn` bot, including automated recruiter messaging.

## Inputs
- **Config**: User settings in `config/` (secrets, search params, etc).
- **Resume**: Valid resume file path (configured in settings).
- **AI Client**: For generating personalized recruiter messages (optional).

## Tools
- `execution/run_bot.py`: The main script that runs the automation.

## Instructions
1. **Verify Config**: Ensure `config/secrets.py`, `config/search.py`, and `config/recruiter_messaging.py` are set up.
2. **Run Bot**: Execute the bot script.
   ```bash
   python execution/run_bot.py
   ```
3. **Monitor**: Watch logs for "Login successful", job application progress, and recruiter messaging activities.
4. **Handle Errors**: If bot fails, check `logs/`, `all excels/recruiter_messages_history.csv`, and refer to `DEBUGGING_RECOMMENDATIONS.md`.

## Outputs
- **Logs**: Application logs in `logs/`.
- **CSV**: Record of applied jobs (usually in `all excels/`).
- **Recruiter Messages CSV**: History of sent recruiter messages in `all excels/recruiter_messages_history.csv`.

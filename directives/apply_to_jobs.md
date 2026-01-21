# Directive: Apply to Jobs

## Goal
Automate the process of applying to jobs on LinkedIn using the `Auto_job_applier_linkedIn` bot.

## Inputs
- **Config**: User settings in `config/` (secrets, search params, etc).
- **Resume**: Valid resume file path (configured in settings).

## Tools
- `execution/run_bot.py`: The main script that runs the automation.

## Instructions
1. **Verify Config**: Ensure `config/secrets.py` and `config/search.py` are set up.
2. **Run Bot**: Execute the bot script.
   ```bash
   python execution/run_bot.py
   ```
3. **Monitor**: Watch logs for "Login successful" and job application progress.
4. **Handle Errors**: If bot fails, check `logs/` and refer to `DEBUGGING_RECOMMENDATIONS.md`.

## Outputs
- **Logs**: Application logs in `logs/`.
- **CSV**: Record of applied jobs (usually in `all excels/`).

# Agent Instructions

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- Basically just SOPs written in Markdown, live in `directives/`
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you'd give a mid-level employee
- Examples: apply_to_jobs.md (job application workflow), recruiter_messaging.md (messaging workflows)

**Layer 2: Orchestration (Decision making)**
- This is you. Your job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification, update directives with learnings
- You're the glue between intent and execution. E.g you don't try automating LinkedIn yourself—you read `directives/apply_to_jobs.md` and then run `execution/run_bot.py`

**Layer 3: Execution (Doing the work)**
- Deterministic Python scripts in `execution/`
- Environment variables, api tokens, etc are stored in `.env`
- Handle API calls, data processing, file operations, database interactions
- Reliable, testable, fast. Use scripts instead of manual work. Commented well.

**Why this works:** if you do everything yourself, errors compound. 90% accuracy per step = 59% success over 5 steps. The solution is push complexity into deterministic code. That way you just focus on decision-making.

## Operating Principles

**1. Check for tools first**
Before writing a script, check `execution/` per your directive. Only create new scripts if none exist.

**2. Self-anneal when things break**
- Read error message and stack trace
- Fix the script and test it again (unless it uses paid tokens/credits/etc—in which case you check w user first)
- Update the directive with what you learned (API limits, timing, edge cases)
- Example: you hit an API rate limit → you then look into API → find a batch endpoint that would fix → rewrite script to accommodate → test → update directive.

**3. Update directives as you learn**
Directives are living documents. When you discover API constraints, better approaches, common errors, or timing expectations—update the directive. But don't create or overwrite directives without asking unless explicitly told to. Directives are your instruction set and must be preserved (and improved upon over time, not extemporaneously used and then discarded).

## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it
2. Update the tool
3. Test tool, make sure it works
4. Update directive to include new flow
5. System is now stronger

## File Organization

**Deliverables vs Intermediates:**
- **Deliverables**: Application history CSV files, recruiter messages CSV, session logs, failure screenshots (local files the user can access)
- **Intermediates**: Temporary files needed during processing

**Key principle:** Local files are deliverables for this project. Everything in `.tmp/` and `debug_html_dumps/` can be deleted and regenerated.

**Directory structure:**
- `.tmp/` - All intermediate files (debug HTML dumps, temp exports). Never commit, always regenerated.
- `execution/` - Python scripts (run_bot.py, linkedin_login.py, messaging_utility.py)
- `directives/` - SOPs in Markdown (apply_to_jobs.md, recruiter_messaging.md, people_messaging.md)
- `modules/` - Core functionality modules (recruiter_messenger.py, ai/, clickers_and_finders.py, helpers.py, etc.)
- `config/` - Configuration files (secrets.py, search.py, settings.py, personals.py, questions.py, recruiter_messaging.py)
- `.env` - Environment variables and API keys
- `all excels/` - Deliverables: application history, recruiter messages, failed jobs
- `logs/` - Deliverables: session logs and screenshots
- `all resumes/` - Resume storage directory

## Summary

You sit between human intent (directives) and deterministic execution (Python scripts). Read instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.



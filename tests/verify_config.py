import os
import sys
import importlib.util

def check_file(path, description):
    if os.path.exists(path):
        print(f"✅ Found {description}: {path}")
        return True
    else:
        print(f"❌ Missing {description}: {path}")
        return False

def check_field(module, field, type_expected):
    if hasattr(module, field):
        val = getattr(module, field)
        if isinstance(val, type_expected):
             print(f"✅ Config '{field}' is present and valid ({type(val).__name__})")
             return True
        else:
             print(f"❌ Config '{field}' is present but WRONG TYPE (Expected {type_expected}, got {type(val)})")
             return False
    else:
        print(f"❌ Config '{field}' is MISSING")
        return False

def main():
    print("========================================")
    print("CONFIGURATION VALIDATION WORKFLOW")
    print("========================================")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(base_dir)

    # 1. Check Config Files
    config_success = True
    config_success &= check_file(os.path.join(base_dir, 'config', 'recruiter_messaging.py'), "Recruiter Messaging Config")
    config_success &= check_file(os.path.join(base_dir, 'config', 'secrets.py'), "Secrets Config")
    
    if not config_success:
        print("🛑 Critical config files missing. Aborting validation.")
        sys.exit(1)

    # 2. Load and Validate Config Content
    try:
        import config.recruiter_messaging as rm_config
        print("\n[recruiter_messaging.py] Validation:")
        check_field(rm_config, 'enable_recruiter_messaging', bool)
        check_field(rm_config, 'max_messages_per_day', int)
        check_field(rm_config, 'message_subject', str)
        check_field(rm_config, 'skip_if_already_applied', bool)
        check_field(rm_config, 'messaging_only_mode', bool)
        check_field(rm_config, 'only_free_messages', bool)
        check_field(rm_config, 'skip_inmail_required', bool)
        
    except Exception as e:
        print(f"❌ Failed to import config.recruiter_messaging: {e}")

    # 3. Check Module Integrity
    print("\n[Module] Integrity Check:")
    modules_to_check = [
        ('modules/recruiter_messenger.py', 'Recruiter Messenger Module'),
        ('execution/run_bot.py', 'Main Bot Execution Script')
    ]
    
    for rel_path, desc in modules_to_check:
        full_path = os.path.join(base_dir, rel_path)
        if check_file(full_path, desc):
            # Try basic syntax check by compiling
            try:
                with open(full_path, 'r') as f:
                    compile(f.read(), full_path, 'exec')
                print(f"✅ Syntax Check Passed: {rel_path}")
            except Exception as e:
                print(f"❌ Syntax Error in {rel_path}: {e}")

    print("\n========================================")
    print("VALIDATION COMPLETE")
    print("========================================")

if __name__ == "__main__":
    main()

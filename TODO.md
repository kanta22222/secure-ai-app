# TODO: Improve Functions in Secure AI App

## Step 1: Refactor duplicated login and registration code in main.py ✅
- Create helper functions `attempt_login` and `attempt_register` to handle both user and admin flows
- Reduce code duplication between user and admin login/registration dialogs

## Step 2: Enhance error handling and logging in auth.py ✅
- Add try-except blocks and logging to `register_user`, `authenticate_user`, `list_users`, `log_activity`, `send_verification_email`
- Improve exception handling for database operations and email sending

## Step 3: Add activity logging for user actions in main.py ✅
- Integrate `log_activity` calls for successful logins, registrations, and failed attempts
- Ensure activity logs capture relevant details like username and action type

## Step 4: Test and verify improvements ✅ 
- Run the application to ensure login, registration, and logging work correctly
- Check logs for proper error handling and activity tracking

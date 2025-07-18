import pandas as pd
import os
from datetime import datetime

USERS_FILE = "data/users.xlsx"
LOGS_FILE = "data/logs.xlsx"

def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_excel(USERS_FILE)
    else:
        return pd.DataFrame(columns=["Full Name", "Email", "Password", "Role"])

def save_users(df):
    df.to_excel(USERS_FILE, index=False)

def signup_user(name, email, password, role):
    users = load_users()
    if email in users['Email'].values:
        return False
    new_user = pd.DataFrame([[name, email, password, role]], columns=users.columns)
    users = pd.concat([users, new_user], ignore_index=True)
    save_users(users)
    return True

def authenticate_user(email, password):
    users = load_users()
    user_row = users[(users['Email'] == email) & (users['Password'] == password)]
    if not user_row.empty:
        return {
            "name": user_row.iloc[0]["Full Name"],
            "email": user_row.iloc[0]["Email"],
            "role": user_row.iloc[0]["Role"]
        }
    return None

def log_user_activity(email, action):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = pd.DataFrame([[email, action, timestamp]],
                             columns=["Email", "Action", "Timestamp"])
    if os.path.exists(LOGS_FILE):
        existing_logs = pd.read_excel(LOGS_FILE)
        log_entry = pd.concat([existing_logs, log_entry], ignore_index=True)
    log_entry.to_excel(LOGS_FILE, index=False)

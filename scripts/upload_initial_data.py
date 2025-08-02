import csv
import requests
import json
import sys
import getpass

# --- Configuration ---
BASE_API_URL = "http://127.0.0.1:5000/api"
SUBJECTS_CSV = 'data/subjects.csv'
CHAPTERS_CSV = 'data/chapters.csv'
QUIZZES_CSV = 'data/quizzes.csv'
QUESTIONS_CSV = 'data/questions.csv'
USERS_CSV = 'data/users.csv'
ATTEMPTS_CSV = 'data/quiz_attempts.csv'
HEADERS = {'Content-Type': 'application/json'}

def get_auth_token(username, password):
    login_url = f"{BASE_API_URL}/auth/login"
    print(f"\nAttempting login as '{username}'...")
    try:
        response = requests.post(login_url, json={"username": username, "password": password})
        response.raise_for_status()
        token = response.json().get('access_token')
        if token:
            print("Login successful. Token obtained.")
            HEADERS['Authorization'] = f"Bearer {token}"
            return token
        return None
    except Exception as e:
        print(f"ERROR: Login failed - {e}")
        return None

def send_request(method, url, payload=None):
    try:
        response = requests.request(method, url, headers=HEADERS, json=payload)
        response.raise_for_status()
        print(f"SUCCESS: {method.upper()} {url}")
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: {method.upper()} {url} - Status {e.response.status_code}")
        try: print(f"       Response: {e.response.json()}")
        except json.JSONDecodeError: print(f"       Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred for {method.upper()} {url} - {e}")
        return None

# --- Data Upload Functions ---
def upload_users(csv_path):
    print("\n--- Processing Users ---")
    existing_users_res = send_request("GET", f"{BASE_API_URL}/users/")
    if not existing_users_res: return
    existing_usernames = {u['username'] for u in existing_users_res.get('users', [])}
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] in existing_usernames:
                print(f"Skipping existing user: {row['username']}")
                continue
            
            print(f"Creating user: {row['username']}")
            # Use the admin endpoint which expects the ID
            payload = {
                "username": row['username'], "email": row['email'],
                "password": row['password'],
                "secret_question_id": int(row['secret_question_id']),
                "secret_answer": row['secret_answer']
            }
            send_request("POST", f"{BASE_API_URL}/users/", payload)

def upload_quiz_attempts(csv_path):
    print("\n--- Processing Quiz Attempts ---")
    users_res = send_request("GET", f"{BASE_API_URL}/users/")
    quizzes_res = send_request("GET", f"{BASE_API_URL}/quizzes/") # Note the trailing slash
    
    if not users_res or not quizzes_res:
        print("ERROR: Could not fetch users or quizzes. Skipping attempts.")
        return
        
    user_map = {u['username']: u['id'] for u in users_res.get('users', [])}
    quiz_map = {q['title']: q['id'] for q in quizzes_res.get('quizzes', [])}

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = user_map.get(row['username'])
            quiz_id = quiz_map.get(row['quiz_title'])
            if not user_id or not quiz_id:
                print(f"WARNING: Skipping attempt for user '{row['username']}' on quiz '{row['quiz_title']}' (ID not found).")
                continue
            
            print(f"Creating attempt for {row['username']} on '{row['quiz_title']}'")
            payload = {
                "user_id": user_id, "quiz_id": quiz_id,
                "score": int(row['score']), "total_questions": int(row['total_questions']),
                "start_time": row['start_time'], "submitted_at": row['submitted_at']
            }
            send_request("POST", f"{BASE_API_URL}/attempts/", payload) # Note the trailing slash

# Other upload functions (subjects, chapters, etc.) remain the same...

if __name__ == '__main__':
    print("Starting initial data upload via API...")
    admin_user = input("Enter Admin Username [default: admin]: ") or "admin"
    admin_pass = getpass.getpass(f"Enter Password for {admin_user}: ")

    if not get_auth_token(admin_user, admin_pass):
        print("\nCould not obtain authorization token. Exiting.")
        sys.exit(1)
        
    # Run the new functions
    upload_users(USERS_CSV)
    upload_quiz_attempts(ATTEMPTS_CSV)
    
    print("-" * 30)
    print("Initial data upload process complete.")
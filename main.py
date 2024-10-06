import requests
import json
import time
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from tqdm import tqdm

API_URL = "https://api.phantom.app/user/v1/profiles/{}"
USERNAMES_FILE = "usernames.txt"
OUTPUT_AVAILABLE = "available_usernames.txt"
OUTPUT_BLACKLISTED = "blacklisted_usernames.txt"
OUTPUT_TAKEN = "taken_usernames.txt"
MAX_THREADS = 20 # Change the amount of threads
REQUEST_TIMEOUT = 10

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,en-AU;q=0.8",
    "content-type": "application/json",
    "priority": "u=1, i",
    "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "none",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "x-phantom-version": "24.19.0",
}

lock_available = threading.Lock()
lock_blacklisted = threading.Lock()
lock_taken = threading.Lock()

def load_usernames(file_path: str) -> List[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            usernames = [line.strip() for line in file if line.strip()]
        print(f"Loaded {len(usernames)} usernames from {file_path}.")
        return usernames
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []

def check_username(username: str) -> str:
    url = API_URL.format(username)
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code == 404:
            return "available"
        elif response.status_code == 403:
            return "blacklisted"
        elif response.status_code == 200:
            data = response.json()
            if "username" in data:
                return "taken"
            else:
                return "error"
        else:
            return "error"
    except requests.RequestException:
        return "error"

def save_result(username: str, status: str):
    if status == "available":
        with lock_available:
            with open(OUTPUT_AVAILABLE, 'a', encoding='utf-8') as file:
                file.write(username + '\n')
    elif status == "blacklisted":
        with lock_blacklisted:
            with open(OUTPUT_BLACKLISTED, 'a', encoding='utf-8') as file:
                file.write(username + '\n')
    elif status == "taken":
        with lock_taken:
            with open(OUTPUT_TAKEN, 'a', encoding='utf-8') as file:
                file.write(username + '\n')

def process_username(username: str) -> str:
    status = check_username(username)
    save_result(username, status)
    return status

def main():
    usernames = load_usernames(USERNAMES_FILE)
    if not usernames:
        return

    total = len(usernames)
    available = 0
    blacklisted = 0
    taken = 0
    errors = 0

    for filename in [OUTPUT_AVAILABLE, OUTPUT_BLACKLISTED, OUTPUT_TAKEN]:
        open(filename, 'w', encoding='utf-8').close()

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_username = {executor.submit(process_username, username): username for username in usernames}
        for future in tqdm(as_completed(future_to_username), total=total, desc="Checking Usernames"):
            username = future_to_username[future]
            try:
                status = future.result()
                if status == "available":
                    available += 1
                elif status == "blacklisted":
                    blacklisted += 1
                elif status == "taken":
                    taken += 1
                else:
                    errors += 1
            except Exception as e:
                print(f"Error processing username '{username}': {e}")
                errors += 1

    print("\n=== Summary ===")
    print(f"Total usernames checked: {total}")
    print(f"Available: {available}")
    print(f"Blacklisted: {blacklisted}")
    print(f"Taken: {taken}")
    print(f"Errors: {errors}")
    print("\nResults saved to:")
    print(f" - {OUTPUT_AVAILABLE}")
    print(f" - {OUTPUT_BLACKLISTED}")
    print(f" - {OUTPUT_TAKEN}")

if __name__ == "__main__":
    main()

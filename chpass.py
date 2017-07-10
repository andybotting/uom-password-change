#!/usr/bin/env python

import getpass
import logging
import random
import re
import requests
import string
import sys

# Python 2.x/3.x compat
try:
    from html.parser import HTMLParser
except ImportError:
    import HTMLParser

try:
    input = raw_input
except NameError:
    pass


PASSWORD_CHANGES = 11
SPECIAL_CHARS = '~!@#$%^*()'

# Simple coloured output
logging.addLevelName(logging.DEBUG,
                     "\033[1;32m %s \033[1;m" %
                     logging.getLevelName(logging.DEBUG))
logging.addLevelName(logging.INFO,
                     "\033[1;36m %s  \033[1;m" %
                     logging.getLevelName(logging.INFO))
logging.addLevelName(logging.WARNING,
                     "\033[1;33m%s\033[1;m" %
                     logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.ERROR,
                     "\033[1;31m %s \033[1;m" %
                     logging.getLevelName(logging.ERROR))

FORMAT = "[%(levelname)s] %(message)s"

logging.basicConfig(
    format=FORMAT,
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def password_valid(password):
    for c in list(SPECIAL_CHARS + string.digits):
        if c in password:
            return True
    return False


def generate_password():
    chars = string.ascii_letters + string.digits + SPECIAL_CHARS
    while True:
        password = ''.join(random.choice(chars) for x in range(16))
        if password_valid(password):
            return password


def login(username, password):
    logging.info('Logging in')
    # For cookies
    session = requests.Session()
    payload = {
        'id': '',
        'command': 'login',
        'activeControl': '',
        'accountId': username,
        'password': password,
    }
    r = session.post('https://idm.unimelb.edu.au/idm/user/login.jsp',
                     data=payload)
    output = r.text

    if 'Login attempt failed for user' in output:
        logging.error('Login failed')
        sys.exit(1)

    # Successful login should return either
    if 'Your username is' or 'Logged in as' in output:
        return session

    # Unknown state
    logging.debug(output)
    logging.error('Unknown error while logging in')
    sys.exit(1)


def logout(session):
    logging.info('Logging out')
    r = session.get('https://idm.unimelb.edu.au/idm/user/userLogout.jsp')
    logging.debug(r.text)
    return True


def change_password(session, password):
    payload = {
        'id': '',
        'command': 'Save',
        'activeControl': '',
        'resourceAccounts.selectAll': 'true',
        'resourceAccounts.password': password,
        'resourceAccounts.confirmPassword': password,
    }
    r = session.post('https://idm.unimelb.edu.au/idm/user/changePassword.jsp',
                     data=payload)
    output = r.text

    if 'Operation Successful' in output:
        logging.info('Change password successful')
        return True

    if 'Policy Violation' in output:
        err_msg = re.search("<div class='AlrtMsgTxt'>"
                            "Policy Violation:&#xA;(.*)</div>",
                            output)
        if err_msg:
            h = HTMLParser()
            msg = h.unescape(err_msg.group(1))
            logging.error('Password policy violation: %s' % msg)
            sys.exit(1)
        else:
            logging.error('Unknown password policy violation')
            sys.exit(1)

    # Unknown state
    logging.debug(r.text)
    logging.error("Unknown error trying to change password to %s" % password)
    sys.exit(1)


def do_change(username, password, new_password):
    # Attempt initial login
    session = login(username, password)
    if not session:
        logging.error('Error logging in with your password')
        sys.exit(1)

    password_list = [password]

    while len(password_list) <= PASSWORD_CHANGES:

        if len(password_list) == PASSWORD_CHANGES:
            temp_password = new_password
            logging.info('Changing password (%d/%d) to your desired password' %
                         (len(password_list), PASSWORD_CHANGES))
        else:
            temp_password = generate_password()
            logging.info('Changing password (%d/%d) to "%s"' %
                         (len(password_list), PASSWORD_CHANGES, temp_password))
            password_list.append(temp_password)

        successful = change_password(session, temp_password)
        # Password change not successful, try again
        if not successful:
            logging.error('Unknown error changing password')
            sys.exit(1)

        logout(session)

        # Try to log in with new password
        session = login(username, temp_password)

        if new_password == temp_password:
            logging.info('Success!')
            sys.exit(0)


def main():

    username = input('Username: ')
    if not username:
        logging.error('Username is required')
        sys.exit(1)

    current_password = getpass.getpass('Current password: ')
    if not current_password:
        logging.error('Password is required')
        sys.exit(1)

    new_password = getpass.getpass('Desired password (if different): ')
    if new_password:

        if not password_valid(new_password):
            logging.error('Desired password is not valid '
                          '(hint: add a number or special character)')
            sys.exit(1)

        new_password_again = getpass.getpass('Desired password (again): ')
        if new_password != new_password_again:
            logging.error('Desired passwords do not match')
            sys.exit(1)
    else:
        new_password = current_password

    do_change(username, current_password, new_password)


if __name__ == '__main__':
    main()

#!/usr/bin/env python

import getpass
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
    from urllib.parse import quote
except ImportError:
    from urllib import quote

try:
    input = raw_input
except NameError:
    pass


PASSWORD_CHANGES = 11
SPECIAL_CHARS = '~!@#$%^*()'


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
    print('Logging in')
    # For cookies
    session = requests.Session()
    payload = {
        'id': '',
        'command': 'login',
        'activeControl': '',
        'accountId': username,
        'password': password,
    }
    r = session.post('https://idm.unimelb.edu.au/idm/user/login.jsp', data=payload)
    output = r.text

    if output.find('Login attempt failed for user') > -1:
        raise Exception('Login failed')

    # Successful login should return either
    if (output.find('Your username is') > -1 or
        output.find('Logged in as')):
        return session

    # Unknown state
    #print(r.text)
    raise Exception('Unknown error while logging in')


def logout(session):
    print('Logging out')
    r = session.get('https://idm.unimelb.edu.au/idm/user/userLogout.jsp')
    #print(r.text)
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
    r = session.post('https://idm.unimelb.edu.au/idm/user/changePassword.jsp', data=payload)
    output = r.text

    if output.find('Operation Successful') > -1:
        print('Change password successful')
        return True

    if output.find('Policy Violation') > -1:
        err_msg = re.search("<div class='AlrtMsgTxt'>Policy Violation:&#xA;(.*)</div>", output)
        if err_msg:
            h = HTMLParser.HTMLParser()
            msg = h.unescape(err_msg.group(1))
            raise Exception('Password policy violation: %s' % msg)
        else:
            raise Exception('Unknown password policy violation')

    # Unknown state
    #print(r.text)
    raise Exception("Unknown error trying to change password to %s" % password)


def do_change(username, password, new_password):
    # Attempt initial login
    session = login(username, password)
    if not session:
        raise Exception('Error logging in with your password')

    password_list = [password]

    while len(password_list) <= PASSWORD_CHANGES:

        if len(password_list) == PASSWORD_CHANGES:
            temp_password = new_password
            print("Changing password (%d/%d) to your desired password" % (len(password_list), PASSWORD_CHANGES))
        else:
            temp_password = generate_password()
            print("Changing password (%d/%d) to '%s'" % (len(password_list), PASSWORD_CHANGES, temp_password))
            password_list.append(temp_password)

        successful = change_password(session, temp_password)
        # Password change not successful, try again
        if not successful:
            raise Exception('Unknown error changing password')

        logout(session)

        # Try to log in with new password
        session = login(username, temp_password)

        if new_password == temp_password:
            print('Success!')
            sys.exit(0)


def main():

    username = input('Username: ')
    if not username:
        print('Username is required')
        sys.exit(1)

    current_password = getpass.getpass('Current password: ')
    if not current_password:
        print('Password is required')
        sys.exit(1)

    new_password = getpass.getpass('Desired password (if different): ')
    if new_password:

        if not password_valid(new_password):
            print("Desired password is not valid (hint: add a number or special character)")
            sys.exit(1)

        new_password_again = getpass.getpass('Desired password (again): ')
        if new_password != new_password_again:
            print('Desired passwords do not match')
            sys.exit(1)
    else:
        new_password = current_password 

    do_change(username, current_password, new_password)


if __name__ == '__main__':
    main()


# UoM Password changer

UoM enforces a passsword policy that requires users to periodically change their
passwords.

While this might seem like a good idea from a security perspective, in practice
it encorages bad passwords, and users to work around the policy.

A great quote from the article [_Time to rethink mandatory password changes_](https://www.ftc.gov/news-events/blogs/techftc/2016/03/time-rethink-mandatory-password-changes)
describes the issue:

> I go on to explain that there is a lot of evidence to suggest that users who
> are required to change their passwords frequently select weaker passwords to
> begin with, and then change them in predictable ways that attackers can guess
> easily. Unless there is reason to believe a password has been compromised or
> shared, requiring regular password changes may actually do more harm than good
> in some cases. (And even if a password has been compromised, changing the
> password may be ineffective, especially if other steps aren’t taken to correct
> security problems.)

This script works by changing your password randomly 10 times, before resetting
your password back to your original password, and thereby allowing you to reuse
your existing, non-weak password that you can remember.

## Using the script

This script requires Python (2.7 or 3+) with the requests library, and takes no
arguments, but will prompt for details.

```sh
$ ./chpass.py
Username: yourusername
Current password: <password hidden>
Desired password (if different):
Logging in
Changing password (1/11) to 'T~Wm8SCtNWHWtSXk'
Change password successful
Logging out
Logging in
Changing password (2/11) to '(w0cqqeJ1D(133~@'
Change password successful
Logging out
Logging in
Changing password (3/11) to 'rrHbk7yL8T(VnORj'
Change password successful
Logging out
Logging in
Changing password (4/11) to 'rvUt)9FvZOSUf82v'
Change password successful
Logging out
Logging in
Changing password (5/11) to 'HNct$yJOEy0y@$88'
Change password successful
Logging out
Logging in
Changing password (6/11) to '*eBR(~AAERa*nmHn'
Change password successful
Logging out
Logging in
Changing password (7/11) to '(^m#firMp1~j0$XV'
Change password successful
Logging out
Logging in
Changing password (8/11) to 'JRZPAe%NFFaKhJYJ'
Change password successful
Logging out
Logging in
Changing password (9/11) to 'Vg5opJNOT4zqoQmQ'
Change password successful
Logging out
Logging in
Changing password (10/11) to 'gjvnadEjT^7)HAkj'
Change password successful
Logging out
Logging in
Changing password (11/11) to your desired password
Change password successful
Logging out
Logging in
Success!
```



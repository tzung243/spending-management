import re


def is_valid_password(password, username=None):
    """
    Check if a password is valid.
    Return an error message if the password is invalid, or None if the password is valid.
    """
    # Check the length of the password
    if len(password) < 8 or len(password) > 64:
        return "Password must be between 8-64 characters long."

    # Check the security of the password
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]+$"
    if not re.match(pattern, password):
        return "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character."

    # Check if the password contains personal information
    if username and username.lower() in password.lower():
        return "Password cannot contain your personal information."

    # Password is valid
    return None

import re

EMAIL_PATTERN = r"[\w\.\-]+@\w+\.\w+"

# Returns a Boolean true/false if the entire email address is validated by matching
# the RegEx pattern
def validate_email_address(email: str):
    result = re.fullmatch(EMAIL_PATTERN, email)
    if result is None:
        return False
    else:
        return True
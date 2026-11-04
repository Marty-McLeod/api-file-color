import secrets
import string

# Returns a secret key of specified character count from all alphabet chars or
# numeric digits. Returns lower case by default!
def generate_api_key(length=40, lower=True):
    char_range = string.ascii_letters + string.digits
    new_key = ''.join(secrets.choice(char_range) for _ in range(length))
    
    # Return result, lower case option if True
    return new_key.lower() if lower else new_key

CHAR_COUNT = 8
API_KEY_MIN_LEN = CHAR_COUNT
API_KEY_MAX_LEN = CHAR_COUNT
TEST_ACTIVATION_URL_HTTP = "http://127.0.0.1:8000/api/activate?apikey="
ACTIVATION_URL_HTTP = "http://colorswap.site/api/activate?apikey="
ACTIVATION_URL_HTTPS = "https://colorswap.site/api/activate?apikey="

EMAIL_FROM_FIELD_NAME = "ColorSwap"
EMAIL_FROM_FIELD_ADDRESS = "noreply@colorswap.site"
EMAIL_FROM_FIELD = f"{EMAIL_FROM_FIELD_NAME} <{EMAIL_FROM_FIELD_ADDRESS}>"

EMAIL_BODY_HTML =\
'''<p>Here is your key: <strong>{apikey}</strong></p> \
<p>Please append it to all your API requests. (Key is not case sensitive)</p> \
<p>Example: http://colorswap.site/api/test-apikey/?apikey={apikey}</p> \
<p>Click the following URL to activate your key: <a href={activation_url}{apikey}>{activation_url}{apikey}</a></p> \
<p><em><small>If you did not make this request please disregard this email.</small></em></p>
'''
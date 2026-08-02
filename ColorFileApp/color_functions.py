"""
Color code functions module. Data (color codes) passed in a function call are validated using the
error handler, which returns error objects (dictionaries), as needed. Color functions handle color
code format conversion.
"""
from .utils.file_functions import load_dict_from_json, write_log_file


def color_code_error_handler(value, value_type, option="", color_dict=None) -> dict | None:
    """
    General error handler for color code functions. This function handles often-used checks on the
    color value data type, length, etc.

    Returns an error code(s) as needed based on the type of data, value, etc...

    Accepts:
    value = color code value (typically only a string)
    value_type: Used to determine tests required; Types = "hex", "rgb", "hsl", "hsv"
    check = (TBD)
    option: optional for color swap functions, 

    Returns: A dict containing an error code + message or None if no errors are found.
    """
    value_types = [ "hex", "rgb", "hsl", "hsv" ]
    options = [ "r_to_g", "g_to_r", "g_to_b", "b_to_g", "r_to_b", "b_to_r", "lighten", "darken" ]
    
    errors = {"error": [] }

    if not value_type in value_types:
        return errors["error"].append(f"Bad value type specified in function all: '{value_type}'")
    # If color swap function has been called (order is non-empty), check for a valid type
    if not option == "" and not option in options:
             errors["error"].append(f"Color swap option {option} is not valid")
    
    # Check values based on their color code type
    match value_type:
        case "hex":
            # Validate data parameter; return early if found as we don't need mutliple errors if it's not a string
            if not isinstance(value, str):
                errors["error"].append(f"Hex value should be a string data type: '{value}'")
                return errors
            # If a string is present, check length & characters: 3 or 6 alphanumeric hexadecimal-complaint chars.
            value = value.strip("#")
            
            # Test for length & valid characters
            if not (len(value) == 3 or len(value) == 6):
                errors["error"].append(f"Invalid length of {len(value)} in '{value}'")  
            
            if not all(c in "ABCDEFabcdef0123456789" for c in value):
                errors["error"].append(f"Invalid char in '{value}'")
                
        case "rgb":
            # validate data length & values. data syhould be pre-converted to tuple prior to calling here
            if not len(value) == 3:
                errors["error"].append(f"RGB value passed must contain 3 elements only: '{value}'")
            for val in value:
                if val < 0 or val > 255:
                    errors["error"].append(f"Color values must be between 0-255 in '{value}'")
                
        case "hsl":
            # validate type, data length, & values. data syhould be pre-converted to tuple prior to arriving here
            if not (type(value) == tuple or type(value) == list):
                errors["error"].append(f"HSL color value must be of type 'tuple' or 'list': '{value}'")
                return errors
            if not all(isinstance(val, int) for val in value):
                errors["error"].append(f"A non-integer value was passed in '{value}'")
                return errors
            if not len(value) == 3:
                errors["error"].append(f"HSL color must contain 3 values only: '{value}'")
                return errors # Return early as an invalid length will cause a fatal error (indexing) below
            if (value[0] < 0 or value[0] > 360) or (value[1] < 0 or value[1] > 100) \
                or (value[2] < 0 or value[2] > 100):
                errors["error"].append(f"Invalid value passed in '{value}'")
                
        case "hsv":
            # validate type, data length, & values. data syhould be pre-converted to tuple prior to arriving here
            if not (type(value) == tuple or type(value) == list):
                errors["error"].append(f"HSV color value must be of type 'tuple' or 'list': '{value}'")
                return errors
            if not all(isinstance(val, int) for val in value):
                errors["error"].append(f"A non-integer value was passed in '{value}'")
                return errors
            if not len(value) == 3:
                errors["error"].append(f"HSV color must contain 3 values only: '{value}'")
                return errors # Return early as an invalid length will cause a fatal error (indexing) below
            if (value[0] < 0 or value[0] > 360) or (value[1] < 0 or value[1] > 100) \
                or (value[2] < 0 or value[2] > 100):
                errors["error"].append(f"Invalid value passed in (H, S, V) value '{value}'")
        case "name":
            # Validate min. number of chars and that the color name is supported (found in the CSS color names list/dict)
            if not len(value) > 2:    # Min. char. count is 3 (Ex: red )
                errors["error"].append(f"Invalid length of {len(value)} in '{value}'")  
            if not value in color_dict:
                errors["error"].append(f"Color name '{value}' not found in CSS colors list.")
            
    # Return errors, if present; else, return None
    if not errors["error"]:
        return None
    else:
        return errors
    
# ===== Hex conversion functions =====
def hex_to_rgb(hex_color, to_string=True) -> str | tuple:
    """
    Converts hexadecimal string to decimal RGB format.
    Checks for a leading '#' and removes it, if present; Missing '#' is ignored otherwise
    if length is valid. CSS HEX color code shorthand (ex: '#fff') will be converted to 6 chars.

    Returns:
    (default): Tuple of integers, ex: (221, 83, 53)
    (to_string=False): CSS style string format, ex: "rgb(221, 83, 53)"
    """
    # Validate color code passed; return errors if non-zero
    errors = color_code_error_handler(hex_color, "hex")
    if errors: return errors
        
    # Strip '#' & convert 3-char shorthand CSS color codes to 6 chars. if needed
    hex = hex_color.strip("#")
    hex = ''.join([ hex[0], hex[0], hex[1], hex[1], hex[2], hex[2] ]) if len(hex) == 3 else hex
        
    # Convert from hex strings (base 16) to decimal integers
    R = int(hex[:2], 16)
    G = int(hex[2:4], 16)
    B = int(hex[4:], 16)   
    
    if to_string==True:
        return f"rgb({R}, {G}, {B})"
    else:
        return R, G, B
    

def hex_to_hsl(hex_color, to_string=True) -> str | tuple:
    """
    Converts hexadecimal string to decimal integer HSL format.
    Checks for a leading '#' and removes it, if present; Missing '#' is ignored if the string length is valid.
    CSS HEX color code shorthand (ex: 'fff') will be converted to 6 chars.

    Returns: Color code format with values ranges (0-360, 0-100, 0-100) representing:
    (color wheel angle in degrees, color saturation (gray level) percent, lightness (white) percent).
    
    (default): CSS style HSL formatted string, ex: "hsl(221, 83%, 53%)"
    (to_string=False): tuple format, decimal integers, ex: (221, 83, 53)
    """
    
    # Validate the color code value passed. If error(s), return w/ errros early. Else, we'll get RGB from 
    # HEX as a tuple
    result = hex_to_rgb(hex_color, to_string=False)
    if isinstance(result, dict): return result
    
    # Normalize each value based on the 0-255 value range
    RGBp = (result[0]/255, result[1]/255, result[2]/255)
    
    # Find Chroma min & max values + Chroma (C) value, lightness (L) and saturation (S)
    # Maintain normalized 0-1 values until end of function as calculations are based on 
    # norm. values
    max_val = max(RGBp)
    min_val = min(RGBp)
    Chroma = max_val - min_val
    L = (max_val + min_val)/2
    S = (Chroma/(1 - abs(2*L - 1))) if Chroma > 0 else 0
    
    # print("Chroma, S, L", Chroma, S, L)
    
    # Find hue angle (H, 'hue')
    if Chroma == 0:
        hue = 0
    elif max_val == RGBp[0]:
        hue = 60 * ( ((RGBp[1] - RGBp[2])/Chroma) % 6 )
    elif max_val == RGBp[1]:
        hue = 60 * ( ((RGBp[2] - RGBp[0])/Chroma) + 2 )
    elif max_val == RGBp[2]:
        hue = 60 * ( ((RGBp[0] - RGBp[1])/Chroma) + 4)

    # print("hue:", hue)

    # Round all to whole integers
    hue_dec = round(hue)
    L_dec = round(L * 100)
    S_dec = round(S * 100)
    
    if to_string == True:
        return f"hsl({hue_dec}, {S_dec}%, {L_dec}%)"
    else:
        return (hue_dec, S_dec, L_dec)
    

# ===== hsl conversion functions =====
def hsl_to_hex(hsl_value) -> str:
    """
    Converts a color value in HSL (hue, saturation, lightness) color vectorspace format to a standard 
    RGB hexidecimal
   
    Accepts either of 2 value formats (handled automatically):
    1. Standard CSS style HSL color format, ex: "hsl(221, 83%, 53%)" string
    2. Enumerable data structure such as a list, tuple, or dictionary values. Valid data values:
    Hue 0-360, sat. 0-100, lightness 0-100). Ex: (221, 83, 53) or [221, 83, 53] etc...
    
    Returns: Color value as uppercase 6 character string with leading "#" symbol. Ex: #2563EB, #000000
    """
    # Determine data type passed; if a string, extract the integer values as a tuple
    if isinstance(hsl_value, str):
        # Strip special chars. after splitting; convert to list of integers
        hsl_value = [int(x.strip("hsl(%)")) for x in hsl_value.lower().split(",")]

    # Validate (H,S,L) data values (pass as a tuple); return if errors are found
    errors = color_code_error_handler(hsl_value, "hsl")
    if errors: return errors
        
    # # Validate data parameter is correct length.
    # if not len(hsl_value) == 3:
    #     raise TypeError("HSL color value must contain 3 values / enumarable values.")

    # if (hsl_value[0] < 0 or hsl_value[0] > 360) or (hsl_value[1] < 0 or hsl_value[1] > 100) \
    #     or (hsl_value[2] < 0 or hsl_value[2] > 100):
    #     raise ValueError(f"Invalid value passed in (H, S, L): {hsl_value}")

    # Create a mutable object just in case a tuple data object is passed for the HSL color
    hsl_val_temp = list(hsl_value) if isinstance(hsl_value, tuple) else hsl_value
    
    # Ensure 360° is represented as 0 degrees in case it's somehow passed to the function
    hsl_val_temp[0] = 0 if hsl_val_temp[0] == 360 else hsl_val_temp[0]
    
    # Get color vectorspace values needed to find R, G, B, components: Hue [0-360) range, saturation [0,1],
    # and lightness (L) [0,1] range. X is an intermediate value resulting as a color code component value
    Hp = hsl_val_temp[0]/60 # Find H' (H prime) from Hue (H)
    Sat = hsl_val_temp[1]/100  # Normalize saturation value
    L = hsl_val_temp[2]/100    # Normalize lightness
    Chroma = (1 - abs(2*L - 1)) * Sat # Chroma (C) as a function of lightness & saturation level
    X = Chroma * (1 - abs((Hp % 2) - 1) )
    
    # Find intermediate color component values
    match Hp:
        case Hp if Hp >= 0 and Hp < 1:
            R1G1B1 = (Chroma, X, 0)
        case  Hp if Hp >= 1 and Hp < 2:
            R1G1B1 = (X, Chroma, 0)
        case  Hp if Hp >= 2 and Hp < 3:
            R1G1B1 = (0, Chroma, X)
        case  Hp if Hp >= 3 and Hp < 4:
            R1G1B1 = (0, X, Chroma)
        case  Hp if Hp >= 4 and Hp < 5:
            R1G1B1 = (X, 0, Chroma)
        case  Hp if Hp >= 5 and Hp < 6:
            R1G1B1 = (Chroma, 0, X)

    # Find R,G,B values based on lightness and chroma, using our intermediate color comp. values
    m = L - Chroma/2

    RGB_list = [R1G1B1[0] + m, R1G1B1[1] + m, R1G1B1[2] + m]

    RGB_list = [round(x * 255) for x in RGB_list] # Denormalize values to get RGB decimal integers

    # Return HEX RGB string as '#AABBCC'
    return f"#{format(RGB_list[0],'02X')}{format(RGB_list[1],'02X')}{format(RGB_list[2],'02X')}"
    # return '#' + ''.join([format(c, '02X') for c in RGB_list])
    

def hsl_to_rgb(hsl_value, to_string=True) -> str | tuple:
    """
    Converts a color value in HSL (hue, saturation, lightness) color vectorspace format to a standard 
    RGB 3-value integer format. Calls hsl_to_hex() to get RGB color values before handling the formatting.
    NOTE: hsl_to_hex() can return a hex string OR error dictionary objects if data validation fails.
    
    Accepts either of 2 value formats:
    1. Standard CSS style HSL color format, ex: "hsl(221, 83%, 53%)" string
    2. Enumerable data structure such as a list, tuple, or dictionary values. Valid data values:
    Hue 0-360, sat. 0-100, lightness 0-100) 
    
    Returns one of 3 options:
    1. (Default, rgb_dec=False) color value as uppercase 6 character string with leading "#" symbol. 
        Ex: #2563EB, #000000
    2. rgb_dec = True, rgb_string = False: RGB decimal format, tuple type
    3. rgb_dec = True, rgb_string = True: CSS style RGB formatted string, ex: "rgb(221, 83, 53)"
    """
    # Calls the HSL to HEX fuction to get the RGB values from color vector space, and also validates the color value.
    # Converts to hexadecimal RGB format, returning a string. We'll strip the special character and convert to 3
    # integers
    # If color value val. fails, errors will be returned, which will result in returning those instead
    result = hsl_to_hex(hsl_value) # Call to converto to hex RGB from HSL color vectorspace
    # If errors were returned, no Hex RGB value, returned, so return the error objects
    if isinstance(result, dict): return result
        
    # Validation passed, so we have a 
    rgb_hex = result.strip("#") # Returns "#AABBCC" type hex string
    rgb = (int(rgb_hex[:1], 16), int(rgb_hex[2:3], 16), int(rgb_hex[4:5], 16) )
    
    if to_string == True:
        return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
    else:
        # Return as a tuple of integers
        return ( rgb[0], rgb[1], rgb[2])
    

def hsl_to_hsv(hsl_value, to_string=True) -> str | tuple:
    """
    Converts a color value in HSL (hue, saturation, lightness) color to HSV (hue, saturation, value).
   
    Accepts either of 2 value formats:
    1. Standard CSS style HSL color format, ex: "hsl(221, 83%, 53%)" string
    2. Enumerable data structure such as a list, tuple, or dictionary values. Valid data values:
    Hue 0-360, sat. 0-100, lightness 0-100) 
    
    Returns one of 3 options:
    1. (Default, to_string=False): CSS style HSV color code string, ex: "hsv(221, 85%, 92%)".
    2. Tuple of integer values: ex: (221, 85, 92)
    """
    # Extract integer values from string if a string is passedL
    if isinstance(hsl_value, str):
        hsl_value = tuple([int(x.strip("hsl(%)")) for x in hsl_value.lower().split(",")])

    # Validate data parameter is correct length; return early if errors
    errors = color_code_error_handler(hsl_value, "hsl")
    if errors: return errors
    
    # if not len(hsl_value) == 3:
    #     raise TypeError("HSL color value must contain 3 values / enumarable values.")

    # if (hsl_value[0] < 0 or hsl_value[0] > 360) or (hsl_value[1] < 0 or hsl_value[1] > 100) \
    #     or (hsl_value[2] < 0 or hsl_value[2] > 100):
    #     raise ValueError(f"Invalid value passed in (H, S, L): {hsl_value}")

    # Assign hue to new hsv data object. If 360 degrees is passed for hue, replace with 0 degrees, in case
    hsv = (0,) if hsl_value[0] == 360 else (hsl_value[0],)
    
    # Normalize HSL values for calculations needed
    L = hsl_value[2]/100
    Sat_l = hsl_value[1]/100
    V = L + Sat_l*min([L, (1-L)])
    Sat_v = 0 if V == 0 else 2*(1 - L/V)
    
    # Convert to HSV format, de-normalize sat. & value
    hsv += (round(Sat_v*100), round(V*100) )

    # values = { "L": L, "Sat_l": Sat_l, "V": V, "Sat_v": Sat_v } 
    # print("values: ", values)

    # Return based on option passed
    if to_string==True:
        return f"hsv({hsv[0]}, {hsv[1]}%, {hsv[2]}%)"
    else:
        return hsv
    

# ===== rgb conversion functions =====
def rgb_to_hsl(rgb_value, to_string=True) -> str | tuple:
    """
    Converts a R,G,B format color code to HSL (hue, sautration, lightness) format.

    Accepts either of 2 value formats (handled automatically):
    1. Standard CSS style RGB color format, ex: "rgb( 36, 99, 235)" string
    2. Enumerable data structure such as a list, tuple, or dictionary values. Ex: (221, 83, 53) or
    [221, 83, 53] etc. Valid values are 0-255 each.
    
    Returns: 
    (default): CSS style string format, ex: "hsl(221, 83%, 53%)"
    (to_string = False): (H,S,L) color code format with values ranges (0-360, 0-100, 0-100), values only.
    
    NOTE: color rgb_value is validated in the called function, not he
    """
    # Determine data type passed; if a string, extract the integer values as a tuple
    if isinstance(rgb_value, str):
        # Strip special chars. after splitting; convert to list of integers
        rgb_value = [int(x.strip("rgb()")) for x in rgb_value.lower().split(",")]

    # Else, for existing or newly converted tuple/list, check for errors before proceeding
    errors = color_code_error_handler(rgb_value, "rgb")
    if errors: return errors

    # Convert (R,G,B) value to HEX RGB format in order to use the hex_to_hsl function call
    hex_rgb = format(rgb_value[0], '02X') + format(rgb_value[1], '02X') + format(rgb_value[2], '02X')

    # Convert hex value to HSL format & return as a string
    return hex_to_hsl(hex_rgb, to_string=to_string)


def rgb_to_hex(rgb_value, to_tuple=False) -> str | tuple:
    """
    Converts an RGB format color code to HEX RGB color code. Accepts both a CSS string format "rgb(36, 99, 235)" or
    RGB tuple format, ex: (36, 99, 235).

    Validates data length and value range (0-255) for the passed RGB value.
    
    Returns:
    (default): Hexadecimal RGB in string format, with "#" symbol. Ex: "#2463EB"
    (to_tuple=True): hex values (as strings) in a tuple, ex: ("24", "63", "EB")
    """
    # Extract integer values from string if a string is passed
    if isinstance(rgb_value, str):
        rgb_list = list(rgb_value.lower().strip("rgb(,)").split(","))
        rgb_temp = tuple([int(val) for val in rgb_list])
    else:
        rgb_temp = rgb_value

    # validate data length & values; return early if errors are present
    errors = color_code_error_handler(rgb_temp, "rgb")
    if errors: return errors
    
    # Convert to hexadecimal
    rgb_hex = ()
    for val in rgb_temp:
        rgb_hex += (format(val, '02X'),) # use format() instead of hex() to avoid '0x' hex prefix

    # Return as hex or  string, as needed
    if to_tuple == True:
        return rgb_hex
    else:
        return f"#{rgb_hex[0]}{rgb_hex[1]}{rgb_hex[2]}"
    

# ===== hsv conversion functions =====
def hsv_to_hex(hsv_value, to_string=True) -> str | tuple:
    """
    Converts a color value in HSV (hue, saturation, value) color vectorspace format to a standard 
    RGB hexidecimal or RGB integer format.
   
    Accepts either of two types:
    1. CSS string format hsv color code, ex: "hsv(221, 85, 92)"
    2. An enumerable data structure such as a list, tuple, or dictionary values. Valid data values:
    Hue 0-360, sat. 0-100, value 0-100)
    
    Returns 1 of 2 types:
    (Default): Hexadecimal RGB color code in cSS style format, ex: "#2463EB"
    (to_string=False): Tuple containing RGB hex values as strings, ex: ("24", "63", "EB")
    """
    # Extract integer values from string if a string is passed
    if isinstance(hsv_value, str):
        hsv_value = tuple([int(x.strip("hsv(%)")) for x in hsv_value.lower().split(",")])

    # Validate data parameter is correct length.
    errors = color_code_error_handler(hsv_value, "hsv")
    if errors: return errors
    
    # if not len(hsv_value) == 3:
    #     raise TypeError("HSV color value must contain 3 values / enumarable values.")

    # if (hsv_value[0] < 0 or hsv_value[0] > 360) or (hsv_value[1] < 0 or hsv_value[1] > 100) \
    #     or (hsv_value[2] < 0 or hsv_value[2] > 100):
    #     raise ValueError(f"Invalid value passed in (H, S, V): {hsv_value}")

    # Create a mutable object just in case a tuple data object is passed for the HSL color
    hsv_val_temp = list(hsv_value)
    
    # Ensure 360° is represented as 0 degrees in case it's somehow passed to the function
    hsv_val_temp[0] = 0 if hsv_val_temp[0] == 360 else hsv_val_temp[0]
    
    # Get color vectorspace values needed to find R, G, B, components: Hue [0-360) range, saturation [0,1],
    # and lightness (L) [0,1] range. X is an intermediate value resulting as a color code component value
    Hp = hsv_val_temp[0]/60 # Find H' (H prime) from Hue (H)
    Sat = hsv_val_temp[1]/100  # Normalize saturation value
    V = hsv_val_temp[2]/100    # Normalize value (V) parameter
    Chroma = V * Sat # Chroma (C) as a function of lightness & saturation level
    X = Chroma * (1 - abs((Hp % 2) - 1) )
    
    # Find intermediate color component values
    match Hp:
        case Hp if Hp >= 0 and Hp < 1:
            R1G1B1 = (Chroma, X, 0)
        case  Hp if Hp >= 1 and Hp < 2:
            R1G1B1 = (X, Chroma, 0)
        case  Hp if Hp >= 2 and Hp < 3:
            R1G1B1 = (0, Chroma, X)
        case  Hp if Hp >= 3 and Hp < 4:
            R1G1B1 = (0, X, Chroma)
        case  Hp if Hp >= 4 and Hp < 5:
            R1G1B1 = (X, 0, Chroma)
        case  Hp if Hp >= 5 and Hp < 6:
            R1G1B1 = (Chroma, 0, X)

    # Find R,G,B values based on value (V) and chroma using our intermediate color comp. values
    m = V - Chroma

    hex_list = [R1G1B1[0] + m, R1G1B1[1] + m, R1G1B1[2] + m]
    # NOTE! There is a precision descrepancy in which the end results are lower than for hsl to RGB values.
    # To compensate for this, round to 2 decimal point places
    hex_list = [round(x,2) for x in hex_list]

    # Denormalize values to get RGB decimal integers & convert to 2-char. strings
    hex_list = [format(round(x * 255), '02X') for x in hex_list] 

    # If option is set, return RGB decimal format, else return as RGB hex. string
    if to_string==True:
        # Return HEX RGB string as '#AABBCC'
        return '#' + ''.join(hex_list)        
    else:
        # Return integers in tuple format
        return tuple(hex_list)
    

def hsv_to_rgb(hsv_value, to_string=True) -> str | tuple:
    """
    Converts a color value in HSV (hue, saturation, value) color vectorspace format to a standard 
    RGB integer format.
   
    Accepts either of two types:
    1. CSS string format hsv color code, ex: "hsv(221, 85, 92)"
    2. An enumerable data structure such as a list, tuple, or dictionary values. Valid data values:
    Hue 0-360, sat. 0-100, value 0-100)
    
    Returns 1 of 2 types:
    (Default): RGB color code in cSS style format, ex: "rgb(36, 99, 235)"
    (to_string=False): Tuple containing RGB hex values as strings, ex: (36, 99, 235)
    """
    # Extract integer values from string if a string is passedL
    if isinstance(hsv_value, str):
        hsv_value = tuple([int(x.strip("hsv(%)")) for x in hsv_value.lower().split(",")])

    # Validate data parameter is correct length; return early if errors
    errors = color_code_error_handler(hsv_value, "hsv")
    if errors: return errors
        
    # Returns a tuple containing hex strings
    hsv_list = hsv_to_hex(hsv_value, to_string=False)
    
    if to_string==True:
        return f"rgb({hsv_list[0]}, {hsv_list[1]}, {hsv_list[2]})"
    else:
        return (int(hsv_list[0],16), int(hsv_list[1],16), int(hsv_list[2], 16))


def hsv_to_hsl(hsv_value, to_string=True) -> str | tuple:
    """
    Converts a color value in HSV (hue, saturation, value) color to HSL (hue, saturation, lightness).
   
    Accepts either of 2 value formats:
    1. Standard CSS style HSV color format, ex: "hsV(221, 85%, 92%)" string
    2. Enumerable data structure such as a list, tuple, or dictionary values. Valid data values:
    Hue 0-360, sat. 0-100, value 0-100) 
    
    Returns one of 3 options:
    1. (Default, to_string=False): CSS style HSL color code string, ex: "hsl(221, 83%, 53%)".
    2. Tuple of integer values: ex: (221, 83, 53)
    """
    # Extract integer values from string if a string is passedL
    if isinstance(hsv_value, str):
        hsv_value = tuple([int(x.strip("hsv(%)")) for x in hsv_value.lower().split(",")])

    # Validate data parameter is correct length; return early if errors
    errors = color_code_error_handler(hsv_value, "hsv")
    if errors: return errors
    
    # if not len(hsv_value) == 3:
    #     raise TypeError("HSV color value must contain 3 values / enumarable values.")

    # if (hsv_value[0] < 0 or hsv_value[0] > 360) or (hsv_value[1] < 0 or hsv_value[1] > 100) \
    #     or (hsv_value[2] < 0 or hsv_value[2] > 100):
    #     raise ValueError(f"Invalid value passed in (H, S, V): {hsv_value}")

    # Assign hue to new hsv data object. If 360 degrees is passed for hue, replace with 0 degrees, in case
    hsl = (0,) if hsv_value[0] == 360 else (hsv_value[0],)
    
    # Normalize HSL values for calculations needed
    V = hsv_value[2]/100
    Sat_v = hsv_value[1]/100
    L = V*(1 - Sat_v/2)
    Sat_l = 0 if (L == 0 or L == 1) else (V - L)/min(L, (1 - L))
    
    # Convert to HSV format, de-normalize sat. & value
    hsl += (round(Sat_l*100), round(L*100) )

    values = { "L": L, "Sat_v": Sat_v, "V": V, "Sat_l": Sat_l } 

    # Return based on option passed
    if to_string==True:
        return f"hsl({hsl[0]}, {hsl[1]}%, {hsl[2]}%)"
    else:
        return hsl


# ===== color swap functions =====
def color_swap_hex(color_val, order) -> str:
    """
    Swaps color values in order to generate a new color.
    Accepts: 
    1. String hexadecimal RGB color, ex: "#AABBCC", 2. R/G/B swap order string, defined as:
    { red/green: "r_to_g" or "g_to_r", green/blue: "g_to_b", "b_to_g", red/blue: "r_to_b", "b_to_r")
    
    Returns:
    Hexadecimal string, ex: "#BBAACC" with '#' if one was passed originally.
    """
    # options = {"r_to_g", "g_to_r", "g_to_b", "b_to_g", "r_to_b", "b_to_r"}
    
    # Validate data parameter
    # if not isinstance(color_val, str):
    #     raise TypeError("Hex value should be a string data type.")

    # Validate color code passed; return errors if non-zero
    errors = color_code_error_handler(color_val, "hex", option=order)
    if errors: return errors
        
    # Strip '#' & convert 3-char shorthand CSS color codes to 6 chars. if needed
    hex = color_val.strip("#")
    hex = ''.join([ hex[0], hex[0], hex[1], hex[1], hex[2], hex[2] ]) if len(hex) == 3 else hex    
    
    # if len(hex) != 6 or not all(c in "ABCDEFabcdef0123456789" for c in hex):
    #     raise ValueError(f"Invalid HEX value: invalid length or char in {hex}")

    # if order not in options:
    #     raise ValueError(f"Color swap option '{order}' must be a valid option: ", options)
        
    # Swap color values
    match order:
        case order if order == "r_to_g" or order == "g_to_r":
            hex_out = ''.join([ hex[2:4], hex[:2], hex[4:] ]) # Swap red & green
        case order if order == "g_to_b" or order == "b_to_g":
            hex_out = ''.join([ hex[:2], hex[4:], hex[2:4] ]) # Swap green & blue
        case order if order == "r_to_b" or order == "b_to_r":
            hex_out = ''.join([ hex[4:], hex[2:4], hex[:2] ]) # Swap red & blue
        
    # print("order: ", order, " hex_out: ", hex_out)

    if color_val[0] == '#':
        return '#' + hex_out
    else:
        return hex_out


def color_swap_rgb(color_val, order, to_string=True) -> str | tuple:
    """
    Swaps color values in order to generate a new color.
    Accepts: 
    A. CSS style string format RGB color code, ex: "rgb(36, 99, 235)" -OR- tuple or list containing integer
    values, ex: (36, 99, 235), [36, 99, 235].
    
    B. R/G/B swap order string, defined as:
    { red/green: "r_to_g" or "g_to_r", green/blue: "g_to_b", "b_to_g", red/blue: "r_to_b", "b_to_r")
    
    C. Return type option (Boolean) for string or tuple.
    
    Returns:
    (default): CSS style RGB string with color values swapped, ex: "rgb(99, 36, 235)"
    (to_string=False): tuple format with integers, ex: (99, 39, 235)
    """
    # options = {"r_to_g", "g_to_r", "g_to_b", "b_to_g", "r_to_b", "b_to_r"}
    
    # Extract integer values from string if a string is passed
    if isinstance(color_val, str):
        rgb_temp = list(color_val.lower().strip("rgb(,)").split(","))
        rgb_temp = tuple([int(val) for val in rgb_temp])
    else:
        rgb_temp = color_val

    # validate data length & values
    errors = color_code_error_handler(rgb_temp, "rgb", option=order)
    if errors: return errors
    
    # if not len(rgb_temp) == 3:
    #     raise ValueError(f"RGB value passed must contain 3 elements only: ->{color_val}")
    # for val in rgb_temp:
    #     if val < 0 or val > 255:
    #         raise ValueError(f"Color values must be between 0-255: {color_val} is invalid")
    # # Validate order option argument
    # if order not in options:
    #     raise ValueError(f"Color swap option '{order}' must be a valid option: ", options)
        
    # Swap color values
    match order:
        case order if order == "r_to_g" or order == "g_to_r":
            rgb_out = (rgb_temp[1], rgb_temp[0], rgb_temp[2]) # Swap red & green
        case order if order == "g_to_b" or order == "b_to_g":
            rgb_out = (rgb_temp[0], rgb_temp[2], rgb_temp[1]) # Swap green & blue
        case order if order == "r_to_b" or order == "b_to_r":
            rgb_out = (rgb_temp[2], rgb_temp[1], rgb_temp[0]) # Swap red & blue
        
    # print("order: ", order, " hex_out: ", hex_out)

    if to_string==True:
        return f"rgb{rgb_out}"
    else:
        return rgb_out


# ===== adjust lightness functions =====
def adjust_lightness_rgb(color_val, percent=10, mode="lighten", to_string=True) -> str | tuple:
    """
    Function to lighten or darken colors passed.
    
    Accepts: 
    A. CSS style string format RGB color code, ex: "rgb(36, 99, 235)" -OR- tuple or list containing integer
    values, ex: (36, 99, 235), [36, 99, 235].
    
    B. lighten & darken values as an integer representing the percentage, i.e., 10 = 10%, etc.
    
    C. Mode option: "lighten" or "darken" to indicate which to perform
    D. Return string true/false option
    
    Returns:
    (default): CSS style RGB string with color values swapped, ex: "rgb(99, 36, 235)"
    (to_string=False): tuple format with integers, ex: (99, 39, 235)
    """
    MIN_VAL = 0
    MAX_VAL = 255
    
    # Extract integer values from string if a string is passed
    if isinstance(color_val, str):
        rgb_temp = list(color_val.lower().strip("rgb(,)").split(","))
        rgb_temp = tuple([int(val) for val in rgb_temp])
    else:
        rgb_temp = color_val

    # Find pre-calculated percentage to integer value; if not a pre-calc. value, compute the value
    adjust_vals = { 10: 25, 15: 38, 20: 51, 30: 76, 40: 102, 50: 127 }

    if percent not in adjust_vals.keys():
        adjust_val = round(percent/100 * MAX_VAL)
    else:
        adjust_val = adjust_vals[percent]

    R = rgb_temp[0]
    G = rgb_temp[1]
    B = rgb_temp[2]

    # print("RGB: ", R, G, B)
    
    # Adjust color based on mode & value. Also handle cases where the value would exceed the R,G,or B min./max. value
    if mode=="lighten":
        R = R + adjust_val if (MAX_VAL - R) >= adjust_val else MAX_VAL
        G = G + adjust_val if (MAX_VAL - G) >= adjust_val else MAX_VAL
        B = B + adjust_val if (MAX_VAL - B) >= adjust_val else MAX_VAL
    elif mode=="darken":
        R = R - adjust_val if (R - MIN_VAL) >= adjust_val else MIN_VAL
        G = G - adjust_val if (G - MIN_VAL) >= adjust_val else MIN_VAL
        B = B - adjust_val if (B - MIN_VAL) >= adjust_val else MIN_VAL

    if to_string==True:
        return f"rgb{(R,G,B)}"
    else:
        return (R, G, B)



def adjust_lightness_hex(color_val, percent=10, mode="lighten", to_string=True) -> str | tuple:
    """
    Function to lighten or darken colors passed.
    
    Accepts: 
    A. CSS style string format hexadecimal RGB color code, ex: "#2463EB" or "#ABF", "AABBCC" etc.
    
    B. lighten & darken values as an integer representing the percentage, i.e., 10 = 10%, etc.
    
    C. Mode option: "lighten" or "darken" to indicate which to perform
    D. Return string true/false option
    
    Returns:
    (default): CSS style hex. RGB string with color values swapped, ex: "#2463EB"
    (to_string=False): tuple format with hex values a string, ex: ("24", "63", "EB")
    """

    # Validate the color code value & format; if errors are returned, return early/with the rrors
    errors = color_code_error_handler(color_val, "hex", option=mode)
    if errors: return errors
        
    # Remove '#' prefix. Convert 3-char shorthand CSS color codes to 6 chars.
    hex = color_val.strip("#")
    hex = ''.join([ hex[0], hex[0], hex[1], hex[1], hex[2], hex[2] ]) if len(hex) == 3 else hex

    
    # if len(hex) != 6 or not all(c in "ABCDEFabcdef0123456789" for c in hex):
    #     raise ValueError(f"Invalid HEX value: invalid length or char in {hex}")

    # if not (mode == "lighten" or mode == "darken"):
    #     raise ValueError(f"Light adjust. '{mode}' must be 'lighten' or 'darken'.")
    
    # Pass the color value as integers to the RGB versionL function; return an integer tuple
    temp = (int(hex[:2], 16), int(hex[2:4], 16), int(hex[4:6], 16))
    
    rgb_temp = adjust_lightness_rgb( temp, percent=percent, mode=mode, to_string=False)
    
    # Convert RGB values to hex. strings
    rgb_temp = (format(rgb_temp[0], '02X'), format(rgb_temp[1], '02X'), format(rgb_temp[2], '02X') )
    
    if to_string == True:
        hex_str = f"{rgb_temp[0]}{rgb_temp[1]}{rgb_temp[2]}"
        return "#" + hex_str if color_val[0] == '#' else hex_str
    else:
        return rgb_temp




# ===== color name conversion functions =====
def named_color_to_value(color_name, color_name_dict, code_format="hex") -> str:
    """
    Replaces a passed standard CSS color name string with a hexadecimal RGB or rgb(...) style string.
    
    Accepts:
    - color_name = a string, ex: "aliceblue" as a standard supported CSS color.
    - code_format: Code format to fetch; i.e., "hex" (default) or "rgb" option
        EX: code_format="hex", returns: "#2463EB"
        code_format="rgb", returns: "rgb(36, 99, 235)"
    - color_name_dict: Dictionary data object containing all color name dictionaries with color values.
        Ex: {
          "aliceblue":{ "hex":"#F0F8FF", "rgb":"rgb(240, 248, 255)"),
          "antiquewhite":{ "hex":"#FAEBD7", "rgb":"rgb(250, 235, 215)"), ... }

    Invalid/not found color names will return an error object. The function references a list of known
    CSS color name/HEX/RGB values.

    Returns: 
    - color code in string hex or rgb() format cooresponding to the color name, if supported.
    - Error, if not found in the color name dictionary
    """
    # Validate the color names/values dictionary is loaded/passed
    errors = color_code_error_handler(color_name, "name")
    if errors: return errors
        
    value = color_name_dict[color_name]["hex"] if code_format == "hex" else color_name_dict[color_name]["rgb"]

    return value



#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
from pathlib import Path
import re
import random

# Reload upon changes
get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# In[3]:


cwd = os.getcwd()
cwd


# In[4]:


get_ipython().system('ls')


# In[5]:


test_dict = { "hex": True, "named": False, "rgb": False, "rgba": False, "rgb_shthand": True, "color_val": "#0000FF" }

options = { 
    "hex_rgb": True, 
    "hex_hsl": False,

    "name_hex": False,
    "name_rgb": False,

    "rgb_hsl": False,
    "rgb_hex": False,

    "hsl_hex": False,
    "hsl_rgb": False,
    "hsl_hsv": False,

    "hsv_hsl": False,
    "hsv_hex": False,
    "hsv_rgb": False,

    "lightdark_hex": { "active": False, "mode": "lighten", "percent": 10 },
    "lightdark_rgb": { "active": False, "mode": "lighten", "percent": 10 },
    "colorswap_hex": { "active": False, "order": "r_to_g"},
    "colorswap_rgb": { "active": False, "order": "r_to_g"}

}


# In[6]:


def color_code_error_handler(value, value_type, option="", color_dict=None) -> dict | None:
    '''
    General error handler for color code functions. This function handles often-used checks on the
    color value data type, length, etc.

    Returns an error code(s) as needed based on the type of data, value, etc...

    Accepts:
    value = color code value (typically only a string)
    value_type: Used to determine tests required; Types = "hex", "rgb", "hsl", "hsv"
    check = (TBD)
    option: optional for color swap functions, 

    Returns: A dict containing an error code + message or None if no errors are found.
    '''
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


# In[7]:


# Pre-compile RegEx expression for more effcient use / use as 'constants'
REGEX_HEX_DEFAULT = re.compile(r"(:\s*#)([a-zA-Z0-9]{3,6})(;)") # matches ':  #AAbb12;' indep. of spaces after ':'
REGEX_HEX_DEFAULT6 = re.compile(r"(:\s*#)([a-zA-Z0-9]{6})(;)") # matches ':  #AAbb12;' indep. of spaces after ':'
REGEX_HEX_DEFAULT3OR6 = re.compile(r"(:\s*)(#)([a-zA-Z0-9]{3}|[a-zA-Z0-9]{6})(;)") # matches ':  #AAbb12;' indep. of spaces after ':'

REGEX_HEX_DEF_NOSEMI = re.compile(r"(:\s*#)([a-zA-Z0-9]{6})")  # matches ':  #AAbb12', as above
REGEX_HEX_NOCOLON = re.compile(r"(#)([a-zA-Z0-9]{6})")  # matches '#AAbb12', no semicolon or spaces (value only)


# In[8]:


# Opens test file for viewing (printing)

try:
    file = open("test.txt", "r")
    text_content = file.read()
    print(text_content)

finally:
    file.close()


# In[9]:


REGEX_HEX_DEFAULT3OR6.sub(r"\g<1>\g<2>" + test_dict["color_val"].strip('#') + r"\g<4>","background: #a1a1A1;")


# In[10]:


with open("test.txt", "r+") as file:
    lines = file.readlines()
    # Subsitutes hex values, if present
    newlines = []

    # RGB option (default) - match ':  #aabbcc;' pattern and replace
    count = 0
    for line in lines:
        # Check if current line is a comment line
        
        # Replace old color value w/ new value(s) and count the num. of substitutions made. Returns the modified
        # line (string) as well as sub. count as an unpacked tuple.
        # newlines.append(REGEX_HEX_DEFAULT3OR6.sub(r"\g<1>" + options["color_val"].strip('#') + r"\g<3>",line))
        mod_line, num_of_subs = REGEX_HEX_DEFAULT3OR6.subn(r"\g<1>" + test_dict["color_val"].strip('#') + r"\g<3>",line)
        newlines.append(mod_line)
        count += num_of_subs
        
    for line in newlines:
        print(line)

    # with open(f"test_{random.randint(1,1000)}.txt", "x") as newfile:
    #     for line in lines:
    #         newfile.write(line)
    print("--" * 12)
    print(f"{count} replacements made out of {len(lines)} lines.")


# In[11]:


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


# In[12]:


print(hex_to_rgb("#a3d"))
print(hex_to_rgb("#aa33dd"))
print("--"*4)
print(hex_to_rgb("2463EB"))
print(hex_to_rgb("2463EB", to_string=False))


# In[13]:


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
    


# In[14]:


print(hex_to_hsl("2563EB"))
print(hex_to_hsl("2563EB", to_string=False))
print("--"*4)
print(hex_to_hsl("000"))
print(hex_to_hsl("000000"))
print(hex_to_hsl("FFFEFE"))


# In[15]:


def hsl_to_hex(hsl_value) -> str:
    '''
    Converts a color value in HSL (hue, saturation, lightness) color vectorspace format to a standard 
    RGB hexidecimal
   
    Accepts either of 2 value formats (handled automatically):
    1. Standard CSS style HSL color format, ex: "hsl(221, 83%, 53%)" string
    2. Enumerable data structure such as a list, tuple, or dictionary values. Valid data values:
    Hue 0-360, sat. 0-100, lightness 0-100). Ex: (221, 83, 53) or [221, 83, 53] etc...
    
    Returns: Color value as uppercase 6 character string with leading "#" symbol. Ex: #2563EB, #000000
    '''
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



# In[16]:


def hsl_to_rgb(hsl_value, to_string=True) -> str | tuple:
    '''
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
    '''
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
  


# In[17]:


# Test HSL to HEX
print("--" * 5, " HSL to HEX, error test", "--"*5)
# Test using error values
print(hsl_to_hex("hsl(361, 83, 53)")) # Contains invalid value
print(hsl_to_hex((221,83,53, 40)))  # Invalid value count
print(hsl_to_hex((0,0))) # Too few values
print(hsl_to_hex((0,0, "AA"))) # Contains a string

# Test with valid values
print("\n", "--" * 5, " HSL to HEX, valid values", "--"*5)
print(hsl_to_hex("hsl(221, 83, 53)"))
print(hsl_to_hex((221,83,53)))  # #2463EB
print(hsl_to_hex([0,0,0]))

# Test with 0 and 360 degrees for hue
print("\n", "--" * 5, " Test with 360 & 0 hue values ", "--"*5)
print("360: ", hsl_to_hex("hsl(360, 50, 50)"))
print("360: ", hsl_to_hex((360, 50,50)))
print("0: ", hsl_to_hex("hsl(0, 50, 50)"))
print("0: ", hsl_to_hex((0, 50,50)))


# HSL to RGB decimal format
print("--" * 5, " HSL to RGB (string), error values ", "--"*5)
# Test using error values
print(hsl_to_rgb("hsl(299, 83, 53)"))
print(hsl_to_rgb((221,83,53, 0)))
print(hsl_to_rgb(0,0))
print(hsl_to_rgb((0,0, "AA")))

# Test with valid values
print("\n", "--" * 5, " HSL to RGB (string), valid values ", "--"*5)
print(hsl_to_rgb("hsl(221, 83, 53)"))
print(hsl_to_rgb((221,83,53)))  # #2463EB
print(hsl_to_rgb([221,83,53]))

print("\n", "--" * 5, " HSL to RGB (tuple)", "--"*5)
print(hsl_to_rgb([221,83,53], to_string=False))



# In[18]:


def rgb_to_hsl(rgb_value, to_string=True) -> str | tuple:
    '''
    Converts a R,G,B format color code to HSL (hue, sautration, lightness) format.

    Accepts either of 2 value formats (handled automatically):
    1. Standard CSS style RGB color format, ex: "rgb( 36, 99, 235)" string
    2. Enumerable data structure such as a list, tuple, or dictionary values. Ex: (221, 83, 53) or
    [221, 83, 53] etc. Valid values are 0-255 each.
    
    Returns: 
    (default): CSS style string format, ex: "hsl(221, 83%, 53%)"
    (to_string = False): (H,S,L) color code format with values ranges (0-360, 0-100, 0-100), values only.
    
    NOTE: color rgb_value is validated in the called function, not here.
    '''
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


# In[19]:


print(rgb_to_hsl("rgb(36, 99, 235"))
print(rgb_to_hsl((36,99,235)))
print(rgb_to_hsl((36,99,235), to_string=False))



# In[20]:


def rgb_to_hex(rgb_value, to_tuple=False) -> str | tuple:
    '''
    Converts an RGB format color code to HEX RGB color code. Accepts both a CSS string format "rgb(36, 99, 235)" or
    RGB tuple format, ex: (36, 99, 235).

    Validates data length and value range (0-255) for the passed RGB value.
    
    Returns:
    (default): Hexadecimal RGB in string format, with "#" symbol. Ex: "#2463EB"
    (to_tuple=True): hex values (as strings) in a tuple, ex: ("24", "63", "EB")
    '''
    # Extract integer values from string if a string is passed
    if isinstance(rgb_value, str):
        rgb_list = list(rgb_value.lower().strip("rgb(,)").split(","))
        rgb_temp = tuple([int(val) for val in rgb_list])
    else:
        rgb_temp = rgb_value

    # validate data length & values; return early if errors are present
    errors = color_code_error_handler(rgb_temp, "rgb")
    if errors: return errors

    
    # if not len(rgb_temp) == 3:
    #     raise ValueError(f"RGB value passed must contain 3 elements only: ->{rgb_value}")
    # for val in rgb_temp:
    #     if val < 0 or val > 255:
    #         raise ValueError(f"Color values must be between 0-255: {rgb_value} is invalid")
    
    # Convert to hexadecimal
    rgb_hex = ()
    for val in rgb_temp:
        rgb_hex += (format(val, '02X'),) # use format() instead of hex() to avoid '0x' hex prefix

    # Return as hex or  string, as needed
    if to_tuple == True:
        return rgb_hex
    else:
        return f"#{rgb_hex[0]}{rgb_hex[1]}{rgb_hex[2]}"
    


# In[21]:


print("from tuple: ", rgb_to_hex((36,99,235)))
print("from string: ", rgb_to_hex("rgb(36,39,235)"))
# Return tuple format
print("from tuple, return tuple: ", rgb_to_hex((36,99,235), to_tuple=True))
# Invalid values passed
# print(rgb_to_hex((36,99,235, 60)))
# # print(rgb_to_hex("rgb(36,39,256)"))


# In[22]:


def hsv_to_hex(hsv_value, to_string=True) -> str | tuple:
    '''
    Converts a color value in HSV (hue, saturation, value) color vectorspace format to a standard 
    RGB hexidecimal or RGB integer format.
   
    Accepts either of two types:
    1. CSS string format hsv color code, ex: "hsv(221, 85, 92)"
    2. An enumerable data structure such as a list, tuple, or dictionary values. Valid data values:
    Hue 0-360, sat. 0-100, value 0-100)
    
    Returns 1 of 2 types:
    (Default): Hexadecimal RGB color code in cSS style format, ex: "#2463EB"
    (to_string=False): Tuple containing RGB hex values as strings, ex: ("24", "63", "EB")
    '''
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


# In[23]:


#
print("--" * 5, " hsv to HEX ", "--"*5)
print(hsv_to_hex("hsv(221, 85%, 92%)"))
print(hsv_to_hex((221,85,92)))  # #2463EB
print(hsv_to_hex((0,0,0)))

# Test with 0 and 360 degrees for hue
print("--" * 5, " Test with 360 & 0 hue values ", "--"*5)
print("360: ", hsv_to_hex("hsv(360, 50%, 50%)"))
print("360: ", hsv_to_hex((360, 50,50)))
print("0: ", hsv_to_hex("hsv(0, 50%, 50%)"))
print("0: ", hsv_to_hex((0, 50,50)))


# In[24]:


def hsv_to_rgb(hsv_value, to_string=True) -> str | tuple:
    '''
    Converts a color value in HSV (hue, saturation, value) color vectorspace format to a standard 
    RGB integer format.
   
    Accepts either of two types:
    1. CSS string format hsv color code, ex: "hsv(221, 85, 92)"
    2. An enumerable data structure such as a list, tuple, or dictionary values. Valid data values:
    Hue 0-360, sat. 0-100, value 0-100)
    
    Returns 1 of 2 types:
    (Default): RGB color code in cSS style format, ex: "rgb(36, 99, 235)"
    (to_string=False): Tuple containing RGB hex values as strings, ex: (36, 99, 235)
    '''
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
    


# In[25]:


print("--" * 5, " hsv to HEX ", "--"*5)
print(hsv_to_rgb("hsv(221, 85%, 92%)"))
print(hsv_to_rgb((221,85,92), to_string=False))
print(hsv_to_rgb((0,0,0)))

# Test with 0 and 360 degrees for hue
print("--" * 5, " Test with 360 & 0 hue values ", "--"*5)
print("360: ", hsv_to_rgb("hsv(360, 50%, 50%)"))
print("360: ", hsv_to_rgb((360, 50,50)))
print("0: ", hsv_to_rgb("hsv(0, 50%, 50%)"))
print("0: ", hsv_to_rgb((0, 50,50)))


# In[26]:


def hsl_to_hsv(hsl_value, to_string=True) -> str | tuple:
    '''
    Converts a color value in HSL (hue, saturation, lightness) color to HSV (hue, saturation, value).
   
    Accepts either of 2 value formats:
    1. Standard CSS style HSL color format, ex: "hsl(221, 83%, 53%)" string
    2. Enumerable data structure such as a list, tuple, or dictionary values. Valid data values:
    Hue 0-360, sat. 0-100, lightness 0-100) 
    
    Returns one of 3 options:
    1. (Default, to_string=False): CSS style HSV color code string, ex: "hsv(221, 85%, 92%)".
    2. Tuple of integer values: ex: (221, 85, 92)
    '''
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

    


# In[27]:


# HSL to HSV (string)
# Invalid value test:
print("--"*5, "Invalid value test", "--"*5)
print(hsl_to_hsv("hsl(360, 120%, 50%)"))
# 
print("-- valid values test--")
print(hsl_to_hsv("hsl(221, 83%, 53%)"))
print(hsl_to_hsv("hsl(360, 50%, 50%)"))
print(hsl_to_hsv("hsl(0,0,0)"))

# HSL to HSV (tuple)
# Invalid length test:
print("--"*5, "Invalid length test", "--"*5)
print(hsl_to_hsv("hsl(360, 120%, 50%, 50%)", to_string=False))
print("-- valid values test--")
print(hsl_to_hsv("hsl(221, 83%, 53%)", to_string=False))
print(hsl_to_hsv("hsl(360, 50%, 50%)", to_string=False))
print(hsl_to_hsv("hsl(0,0,0)", to_string=False))


# In[28]:


def hsv_to_hsl(hsv_value, to_string=True) -> str | tuple:
    '''
    Converts a color value in HSV (hue, saturation, value) color to HSL (hue, saturation, lightness).
   
    Accepts either of 2 value formats:
    1. Standard CSS style HSV color format, ex: "hsV(221, 85%, 92%)" string
    2. Enumerable data structure such as a list, tuple, or dictionary values. Valid data values:
    Hue 0-360, sat. 0-100, value 0-100) 
    
    Returns one of 3 options:
    1. (Default, to_string=False): CSS style HSL color code string, ex: "hsl(221, 83%, 53%)".
    2. Tuple of integer values: ex: (221, 83, 53)
    '''
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


# In[29]:


# HSV to HSL (string)
# Check for invalid values
# print(hsv_to_hsl("hsv(221, 110%, 92%"))

print(hsv_to_hsl("hsv(221, 85%, 92%)"))
print(hsv_to_hsl("hsv(360, 50%, 50%)"))


# HSV to HSL (tuple)
# Check for invalid length
# print(hsv_to_hsl((221,85,92,0), to_string=False) )

print(hsv_to_hsl((221,85,92), to_string=False) )
print(hsv_to_hsl((0,50,50), to_string=False) )


# In[30]:


def color_swap_hex(color_val, order) -> str:
    '''
    Swaps color values in order to generate a new color.
    Accepts: 
    1. String hexadecimal RGB color, ex: "#AABBCC", 2. R/G/B swap order string, defined as:
    { red/green: "r_to_g" or "g_to_r", green/blue: "g_to_b", "b_to_g", red/blue: "r_to_b", "b_to_r")
    
    Returns:
    Hexadecimal string, ex: "#BBAACC" with '#' if one was passed originally.
    '''
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


# In[31]:


# R-G
print("--"*5, "Test: 1) bad value, 2) length, 3) bad swap order", "--"*5)
print(color_swap_hex("#ZZBBCC", "r_to_g"))
print(color_swap_hex("AABBCCF", "g_to_r"))
print(color_swap_hex("#AABBCC", "r_to_r"))

#
print("Test valid values")
print(color_swap_hex("#AABBCC", "r_to_g"))
print(color_swap_hex("AABBCC", "g_to_r"))

# G-B
print(color_swap_hex("#AABBCC", "g_to_b"))
print(color_swap_hex("AABBCC", "b_to_g"))

# B-R
print(color_swap_hex("#AABBCC", "r_to_b"))
print(color_swap_hex("AABBCC", "b_to_r"))


# In[32]:


def color_swap_rgb(color_val, order, to_string=True) -> str | tuple:
    '''
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
    '''
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


# In[33]:


# R to G
print(color_swap_rgb("rgb(36,99,235)", "r_to_g"))
print(color_swap_rgb((36,99,235), "r_to_g"))
print(color_swap_rgb((36,99,235), "r_to_g", to_string=False))

# G to B
print(color_swap_rgb("rgb(36,99,235)", "g_to_b"))
print(color_swap_rgb((36,99,235), "g_to_b"))
print(color_swap_rgb((36,99,235), "g_to_b", to_string=False))

# R to B
print(color_swap_rgb("rgb(36,99,235)", "r_to_b"))
print(color_swap_rgb((36,99,235), "r_to_b"))
print(color_swap_rgb((36,99,235), "r_to_b", to_string=False))

# rgb(74,98,161) varieties:
print(color_swap_rgb("rgb(74,98,161)", "r_to_g"))
print(color_swap_rgb("rgb(74,98,161)", "g_to_b"))
print(color_swap_rgb("rgb(74,98,161)", "r_to_b"))



# In[34]:


def adjust_lightness_rgb(color_val, percent=10, mode="lighten", to_string=True) -> str | tuple:
    '''
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
    '''
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


# In[35]:


# #2463EB = rgb(36, 99, 235)
print("--"*5, "# Adjust lightness - ligthen, default 10%","--"*5)
print("rgb(36, 99, 235) -> ", adjust_lightness_rgb("rgb(36, 99, 235)"))
print("rgb(36, 99, 235) -> ", adjust_lightness_rgb("rgb(36, 99, 235)", to_string=False))
print("rgb(36, 99, 235) -> ", adjust_lightness_rgb((36, 99, 235)))
print("rgb(25, 0, 255) -> ", adjust_lightness_rgb((25, 0, 255)))
print()
# Lighten with custom value
print("--"*5, "# Adjust lightness - ligthen, custom val.", "--"*5)
print("rgb(36, 99, 235) 23% -> ", adjust_lightness_rgb("rgb(36, 99, 235)", percent=23))
print()
# Adjust lightness - darken
print("--"*5, "# Adjust lightness - darken","--"*5)
print("rgb(36, 99, 235) -> ", adjust_lightness_rgb("rgb(36, 99, 235)", mode="darken"))
print("rgb(36, 99, 235) -> ", adjust_lightness_rgb("rgb(36, 99, 235)", mode="darken", to_string=False))
print("rgb(36, 99, 235) -> ", adjust_lightness_rgb((36, 99, 235), mode="darken"))
print("rgb(25, 0, 200) -> ", adjust_lightness_rgb((25, 0, 235), mode="darken"))
print()
# Darken with custom value
print("--"*5, "# Adjust lightness - darken, custom val.", "--"*5)      
print("rgb(36, 99, 235) 23% -> ", adjust_lightness_rgb("rgb(36, 99, 235)", mode="darken", percent=23))


# In[36]:


def adjust_lightness_hex(color_val, percent=10, mode="lighten", to_string=True) -> str | tuple:
    '''
    Function to lighten or darken colors passed.
    
    Accepts: 
    A. CSS style string format hexadecimal RGB color code, ex: "#2463EB" or "#ABF", "AABBCC" etc.
    
    B. lighten & darken values as an integer representing the percentage, i.e., 10 = 10%, etc.
    
    C. Mode option: "lighten" or "darken" to indicate which to perform
    D. Return string true/false option
    
    Returns:
    (default): CSS style hex. RGB string with color values swapped, ex: "#2463EB"
    (to_string=False): tuple format with hex values a string, ex: ("24", "63", "EB")
    '''

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


# In[37]:


# #2463EB = rgb(36, 99, 235)
print("--"*5, "Test default (percent=10, mode='lighten')", "--"*5)
print("#2463EB -> ", adjust_lightness_hex("#2463EB"))
print("#2463EB -> ", adjust_lightness_hex("#2463EB", to_string=False))
print("#2463EB -> ", adjust_lightness_hex("2463EB"))
print("#abc -> ", adjust_lightness_hex("abc"))
print("#1600FF -> ", adjust_lightness_hex("#1600FF"))
print()
# Lighten with custom value
print("--"*5, "Test default (percent=custom, mode='lighten')", "--"*5)
print("#2463EB 23% -> ", adjust_lightness_hex("#2463EB", percent=23))
print()
# Adjust lightness - darken
print("--"*5, "Test default (percent=10, mode='darken')", "--"*5)
print("#2463EB -> ", adjust_lightness_hex("#2463EB", mode="darken"))
print("#2463EB -> ", adjust_lightness_hex("#2463EB", mode="darken", to_string=False))
print("#2463EB -> ", adjust_lightness_hex("2463EB", mode="darken"))
print("#abc -> ", adjust_lightness_hex("abc", mode="darken"))
print("#1600FF -> ", adjust_lightness_hex("#1600FF", mode="darken"))
print()
# Lighten with custom value
print("--"*5, "Test default (percent=custom, mode='darken')", "--"*5)
print("#2463EB 23% -> ", adjust_lightness_hex("#2463EB", mode="darken", percent=23))


# In[38]:


# Open the color names file and loads as a dictionary object for reference use
import json

def load_dict_from_json(filename, dict_name="") -> dict:
    '''
    Given a filename, reads the file and returns the single/main data dictionary contained within, if a 
    name is supplied. Else, all available are returned.
    
    Returns an error object of JSON is not valid or file not found.
    '''
    
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return { "error": f"File '{filename}' not found." }
    except json.JSONDecodeError as e:
        return { "error": f"Invalid JSON format in '{filename}': {e}" }

    if dict_name:
        return data[dict_name]
    else:
        return data


# In[39]:


COLOR_NAMES = load_dict_from_json("color_names.json")
print(COLOR_NAMES)


# In[40]:


color_val = "#2463EB"
name_val = "aliceblue"

print("Number of named colors: ", len(COLOR_NAMES))

if name_val in COLOR_NAMES.keys():
    print("Found name!")
    color_val = COLOR_NAMES[name_val]["hex"]
    print("color_val: ", color_val)


# In[41]:


def named_color_to_value(color_name, color_name_dict, code_format="hex") -> str:
    '''
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
    '''
    # Validate the color names/values dictionary is loaded/passed
    errors = color_code_error_handler(color_name, "name")
    if errors: return errors
        
    value = color_name_dict[color_name]["hex"] if code_format == "hex" else color_name_dict[color_name]["rgb"]

    return value


    


# In[42]:


print(named_color_to_value("rebeccapurple", COLOR_NAMES))
print(named_color_to_value("rebeccapurple", COLOR_NAMES, code_format="rgb"))


# In[43]:


# def color_test(color_val):
#     print("val: ", color_val,  "Type: ", type(color_val))
#     return color_val.group(3)

# def get_match_group(match_obj, num):
#     return match_obj.group(num)


# In[44]:


def process_lines_with_regex(color_function, regex_expr, target_filename, source_filename, whitelist=None, blacklist=None):
    '''
    Processes a file, substituting the target color codes based on the color mode and the RegEx expression
    used to match terms. The reesult is saved in the desired target filename.
    A report (stats) object is returned along with errors, if any.
    
    Accepts:
    - color_function: color function to be used for color code conversion (must match the color mode).
    - regex_expr: regrex string or pre-compiled term used for matchin syntax.
    - target_filename: File to be created/overwritten for saving the results. Existing file of the same name will be over
      written.
    - source_filename: Original file from which lines are scanned for matches & substitutions made. Will not be modified!
    '''
    
    report = { "lines": 1, "changes": 0, "skipped": 0, "error_stats": {} } # Tracks changes made and error messages/details
    
    with open(source_filename, "r+") as file:    
        lines = file.readlines()
        # Subsitutes hex values, if present
        newlines = []
        
        # RGB option (default) - match ':  #aabbcc;' pattern and replace
        for line in lines:
            temp_line = line
            match_list = list(re.finditer(regex_expr, line))
            
            # Process the matched color values found; if an error dict. is returned, add it to the error report
            # data object and skip that matched string term in the match list
            processed_list = []
            for i, m in enumerate(match_list):
                result = color_function(m.group(2))  # Call color function w/ matched string's value
                start, end = m.span()
                
                if isinstance(result, dict):
                    # Increment error count, aka "skipped", and skip that match string as
                    # errors were found when calling the color function
                    report["skipped"] += 1  
                    # Add current line number to the current error messages
                    result["error"] = [e + f", line {report["lines"]}" for e in result["error"] ]
                    # Add error messages to the reporting data object; key = the "skipped" integer value
                    report["error_stats"] |= { report["skipped"]: result["error"] }
                else:
                    # Increment change count and rebuild the updated string: 
                    # New line = line BEFORE match + match group(1) + updated match string + trailing match group (3)
                    # + remaining riginal line group (3).
                    
                    # Modify the current line and abide by whitelist or blacklists if they exist
                    if whitelist is None and blacklist is None:  # (default is None, change all matched terms)
                        report["changes"] += 1  
                        temp_line = temp_line[:start] + m.group(1) + result + m.group(3) + temp_line[end:]
                    elif whitelist is not None:
                        if m.group(2).upper() in whitelist: # Change the line ONLY if the term is in the whitelist
                            report["changes"] += 1  
                            temp_line = temp_line[:start] + m.group(1) + result + m.group(3) + temp_line[end:]
                        else:
                            pass
                    elif blacklist is not None: # Skip modifying the line for the given word if found in blacklist
                        if m.group(2).upper() in blacklist:
                            pass
                        else:
                            report["changes"] += 1  
                            temp_line = temp_line[:start] + m.group(1) + result + m.group(3) + temp_line[end:]

            # Build the new file list (updated lines) & update
            newlines.append(temp_line)
            report["lines"] += 1
            
        # Write the updated content to a new file w/ the same original filename. Overwrites an existing file!
        with open(target_filename, "wt") as file:
            for line in newlines:
                file.write(line)

        return report


# In[45]:


def report_stats(data_object, mode):
    '''
    Reports a summary of data changes made & errors via the print output
    '''
    print("==" * 12, f"MATCH REPORT FOR MODE {mode}", "==" * 12)
    print(json.dumps(data_object, indent=4, sort_keys=False))
    print("--"*12)
    print(f"{data_object["changes"]} replacements made out of {data_object["lines"]} lines. {data_object["skipped"]} invalid terms skipped.")     
    print("==" * 24)


# In[46]:


def write_log_file(filename_path, data_object, color_mode, write_mode="a"):
    '''
    Saves matching status & error data to a log file.
    Accepts: 
    - filename_path: file name & path for log file created/appended.
    - data_object: dict containing status data and errors. Must contain keys: "changes", "lines", "skipped."
    - color_mode: current mode of operation, i.e., hex_to_rgb, etc.
    - write_mode: (default standard append/create new) allows changing the file write access mode
    '''
    with open(filename_path, write_mode, newline="\n", encoding="utf-8") as file:
        # Write each dict structure which contains matcing data as well as any errors found.
        title_string = f"{'•••' * 3} STATUS FOR OPERATION {color_mode} {'•••' * 3}"
        file.write(title_string + "\n")
        json.dump(data_object, file, indent=2)
        file.write("\n\n")
        file.write(f'{data_object["changes"]} replacement(s) made out of {data_object["lines"]} lines. ')
        file.write(f'{data_object["skipped"]} invalid terms skipped.')
        file.write("\n")
        file.write(f"{'•' * len(title_string)}\n")
        file.write("\n")


# In[49]:


# ================ REGEX EXPRESSIONS FOR TERM MATCHING ==========
REGEX_HEX = re.compile(r"(:\s*)(#[a-zA-Z0-9]{3,8})(;)")
REGEX_RGB = re.compile(r"(?i)(:\s*)(rgb\((?:\s*[0-9]+,)+(?:\s*[0-9])+\))(;)") # Note: uses case flag 'i'
REGEX_HSL = re.compile(r"(?i)(:\s*)(hsl\((?:\s*[0-9]+,)+(?:\s*[0-9])+\))(;)") # Note: uses case flag 'i'
REGEX_HSV = re.compile(r"(?i)(:\s*)(hsv\((?:\s*[0-9]+),(?:\s*[0-9]+%,?)+\))(;)") # Note: uses case flag 'i'
REGEX_NAME = re.compile(r"(?i)(:\s*)([a-zA-Z]{3,})(;)") # Uses case-insensitive flag
# ===============================================================

def file_color_processor(orig_filename, file_name_path, logfile_name_path, options, white_filename="", black_filename="") -> dict:
    '''
    Uses a top level function to read, write, and manipulate files while using color functions
    based on the user JSON options received.

    Returns a report object (dict) with data counts for all files processed + change counts.
    '''
    # report = { "lines": 0, "changes": 0, "skipped": 0, "error_stats": {} } # Tracks changes made and error values
    # linecount = report["lines"] # Alias variable
    reports = {}
    
    # As the name color function is a special case, additional parameters are used when calling. To preserve passing
    # a function to process_lines_with_regex(), bind the required arguments prior to passing the function.
    named_color_to_hex = lambda color_name: named_color_to_value(color_name, color_name_dict=COLOR_NAMES, \
                                                                 code_format="hex")
    named_color_to_rgb = lambda color_name: named_color_to_value(color_name, color_name_dict=COLOR_NAMES, \
                                                                 code_format="rgb")
    

    # Check for an existing log file. If true, delete it as a new one will be created & appended to.
    if os.path.isfile(logfile_name_path):
        os.remove(logfile_name_path)
        print(f"Previous file {logfile_name_path} found and deleted. Starting new log file.")
    else:
        print(f"Previous {logfile_name_path} not found; no action taken.")
        
    # Check for a whitelist or blacklist file. If found, validate JSON format. Loads the 
    # Default is no lists, so set them to None initially
    whitelist = None  # Ensures they'll be ignored in line processing if nothing was passed / or invalid files passed
    blacklist = None
    
    if white_filename:
        result = load_dict_from_json(white_filename)
        # If errors are found, add to the parent status dict (reports)
        if "error" in result:
            reports |= { "whitelist": { "lines": 0, "changes": 0, "skipped": 0, "error_stats": {result} } }
        else:
            # Save a success user message in the stats for the whitelist report
            reports |= { "whitelist": { "lines": 0, "changes": 0, "skipped": 0, "error_stats": \
                                        f"Whitelist in {white_filename} loaded ok." } }
            # Convert dictionary to a list; ensure all strings are upper case before passing to ensure matches work
            whitelist = [val.upper() for val in result.get("whitelist") ]
                                      
    elif black_filename:
        result = load_dict_from_json(black_filename)
        # If errors are found, add to the parent status dict (reports)
        if "error" in result:
            reports |= { "blacklist": { "lines": 0, "changes": 0, "skipped": 0, "error_stats": {result} } }  
        else:
            # Save a success user message in the stats for the whitelist report
            reports |= { "blacklist": { "lines": 0, "changes": 0, "skipped": 0, "error_stats": \
                                        f"Blacklist in {black_filename} loaded ok." }  }
            # Convert dictionary to a list; ensure all strings are lower case before passing
            blacklist = [val.upper() for val in result.get("blacklist") ]
    
    # -----------------------------------
    # Hex to RGB conversion
    if options["hex_rgb"] == True:
        report = process_lines_with_regex(hex_to_rgb, REGEX_HEX, orig_filename, file_name_path, whitelist, blacklist)
        reports |= { "hex_rgb": report }
            
    if options["hex_hsl"] == True:
        report = process_lines_with_regex(hex_to_hsl, REGEX_HEX, orig_filename, file_name_path, whitelist, blacklist)
        reports |= { "hex_hsl": report }        

    
    # -----------------------------------    
    if options["rgb_hsl"] == True:
        report = process_lines_with_regex(rgb_to_hsl, REGEX_RGB, orig_filename, file_name_path, whitelist, blacklist)
        reports |= { "rgb_hsl": report }        
            
    if options["rgb_hex"] == True:
        report = process_lines_with_regex(rgb_to_hex, REGEX_RGB, orig_filename, file_name_path, whitelist, blacklist)
        reports |= { "rgb_hex": report }            

    
    # -----------------------------------    
    if options["hsl_hex"] == True:
        report = process_lines_with_regex(hsl_to_hex, REGEX_HSL, orig_filename, file_name_path, whitelist, blacklist)
        reports |= { "hsl_hex": report }            

    if options["hsl_rgb"] == True:
        report = process_lines_with_regex(hsl_to_rgb, REGEX_HSL, orig_filename, file_name_path, whitelist, blacklist)
        reports |= { "hsl_rgb": report }                  

    if options["hsl_hsv"] == True:
        report = process_lines_with_regex(hsl_to_hsv, REGEX_HSL, orig_filename, file_name_path, whitelist, blacklist)
        reports |= { "hsl_hsv": report }                  

    
    # -----------------------------------    
    if options["hsv_hsl"] == True:
        report = process_lines_with_regex(hsv_to_hsl, REGEX_HSV, orig_filename, file_name_path, whitelist, blacklist)
        reports |= { "hsv_hsl": report }          
        
    if options["hsv_hex"] == True:
        report = process_lines_with_regex(hsv_to_hex, REGEX_HSV, orig_filename, file_name_path, whitelist, blacklist)
        reports |= { "hsv_hex": report }          

    if options["hsv_rgb"] == True:
        report = process_lines_with_regex(hsv_to_rgb, REGEX_HSV, orig_filename, file_name_path, whitelist, blacklist)
        reports |= { "hsv_rgb": report }   
        

    # -----------------------------------
    # Convert a CSS color name to a value code - requires the color reference dict to be passed
    if options["name_hex"] == True:
        report = process_lines_with_regex(named_color_to_hex, REGEX_NAME, orig_filename, \
                                          file_name_path, whitelist, blacklist)
        reports |= { "name_hex": report }        
        
    if options["name_rgb"] == True:
        report = process_lines_with_regex(named_color_to_rgb, REGEX_NAME, orig_filename, \
                                          file_name_path, whitelist, blacklist)
        reports |= { "name_rgb": report }          

    
    # -----------------------------------
    if options["colorswap_hex"]["active"] == True:
        # Bind 2nd argument to the color function to work with passing the function to the line process function
        color_swap_hex_order = lambda color_val: color_swap_hex(color_val, order=options["colorswap_hex"]["order"])
        
        report = process_lines_with_regex(color_swap_hex_order, REGEX_HEX, orig_filename, \
                                          file_name_path, whitelist, blacklist)
        reports |= { "colorswap_hex": report }              

    if options["colorswap_rgb"]["active"] == True:
        # Bind 2nd argument to the color function to work with passing the function to the line process function
        color_swap_rgb_order = lambda color_val: color_swap_rgb(color_val, order=options["colorswap_rgb"]["order"])
        
        report = process_lines_with_regex(color_swap_rgb_order, REGEX_RGB, orig_filename, \
                                          file_name_path, whitelist, blacklist)
        reports |= { "colorswap_rgb": report }        


    # -----------------------------------    
    if options["lightdark_hex"]["active"] == True:
        # Function: adjust_lightness_rgb(color_val, percent=10, mode="lighten", to_string=True)
        
        # Bind arguments to 2 & 3 to the color function to work with passing the function. Arg. 4 is default value.
        adjust_lightness_hex_color_val = lambda color_val: \
                                    adjust_lightness_hex(color_val, percent=options["lightdark_hex"]["percent"], \
                                     mode=options["lightdark_hex"]["mode"])
        
        report = process_lines_with_regex(adjust_lightness_hex_color_val, REGEX_HEX, orig_filename, \
                                          file_name_path, whitelist, blacklist)
        reports |= { f"lightdark_hex ({options["lightdark_hex"]["mode"]})": report }        

    if options["lightdark_rgb"]["active"] == True:
        # Function: adjust_lightness_rgb(color_val, percent=10, mode="lighten", to_string=True)
        
        # Bind arguments to 2 & 3 to the color function to work with passing the function. Arg. 4 is default value.
        adjust_lightness_rgb_color_val = lambda color_val: \
                                    adjust_lightness_rgb(color_val, percent=options["lightdark_rgb"]["percent"], \
                                     mode=options["lightdark_rgb"]["mode"])
        
        report = process_lines_with_regex(adjust_lightness_rgb_color_val, REGEX_RGB, orig_filename, \
                                          file_name_path, whitelist, blacklist)
        reports |= { f"lightdark_rgb ({options["lightdark_rgb"]["mode"]})": report }        

    
    # -----------------------------------        
    # Save match status reports to a log file
    # function: write_log_file(filename_path, data_object, color_mode, write_mode="a"):
    for rep_key, rep_val in reports.items():
        write_log_file(logfile_name_path, data_object=rep_val, color_mode=rep_key)


# In[50]:


# Test hex to rgb
file_color_processor("test_modified.txt", "test.txt", "match_log.txt", black_filename="blacklist.json", \
                     options = { "hex_rgb": True, "hex_hsl": False, "rgb_hsl": False, \
                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                    "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                     "hsv_rgb": False, "name_hex": False, "name_rgb": False, \
                      "colorswap_hex": { "active": False, "order": "r_to_g" }, \
                      "colorswap_rgb": { "active": False, "order": "r_to_g" }, \
                    "lightdark_hex": { "active": False, "mode": "darken", "percent": 10 }, \
                    "lightdark_rgb": { "active": False, "mode": "lighten", "percent": 10 } } )                     


# In[78]:


# Test hex to hsl
file_color_processor("test_modified.txt", "test.txt", "match_log.txt", { "hex_rgb": False, "hex_hsl": True, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                      "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False} )


# In[79]:


# Test rgb to hsl
file_color_processor("test_modified.txt", "test.txt", "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": True, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                      "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False} )


# In[81]:


# Test rgb to hex
file_color_processor("test_modified.txt", "test.txt", "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": True,  "hsl_hex": False, "hsl_rgb": False, \
                                                      "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False} )


# In[82]:


# Test hsl to hex
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": True, "hsl_rgb": False, \
                                                      "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False} )


# In[84]:


# Test hsl to rgb
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": True, \
                                                      "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False} )


# In[86]:


# Test hsl to hsv
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                      "hsl_hsv": True, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False} )


# In[87]:


# Test hsv to hsl
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                      "hsl_hsv": False, "hsv_hsl": True, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False} )


# In[88]:


# Test hsv to hex
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                      "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": True, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False} )


# In[90]:


# Test hsv to rgb
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                      "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": True, "name_hex": False, "name_rgb": False} )


# In[91]:


# Test name to hex
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                      "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": True, "name_rgb": False} )


# In[92]:


# Test name to rgb
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                      "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": True} )


# In[87]:


# Test color swap function (hex)
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                     "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False, \
                                                      "colorswap_hex": { "active": True, "order": "r_to_g" }, \
                                                      "colorswap_rgb": { "active": False, "order": "r_to_g" }, \
                                            "lightdark_hex": { "active": False, "mode": "lighten", "percent": 10 }, \
                                            "lightdark_rgb": { "active": False, "mode": "lighten", "percent": 10 } } )                                                                         


# In[88]:


# Test color swap function (rgb)
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                     "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False, \
                                                      "colorswap_hex": { "active": False, "order": "r_to_g" }, \
                                                      "colorswap_rgb": { "active": True, "order": "r_to_g" }, \
                                            "lightdark_hex": { "active": False, "mode": "lighten", "percent": 10 }, \
                                            "lightdark_rgb": { "active": False, "mode": "lighten", "percent": 10 } } )


# In[89]:


# Test adjust lightness (hex)
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                     "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False, \
                                                      "colorswap_hex": { "active": False, "order": "r_to_g" }, \
                                                      "colorswap_rgb": { "active": False, "order": "r_to_g" }, \
                                            "lightdark_hex": { "active": True, "mode": "darken", "percent": 10 }, \
                                            "lightdark_rgb": { "active": False, "mode": "lighten", "percent": 10 } } )


# In[94]:


# Test adjust lightness (rgb)
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", { "hex_rgb": False, "hex_hsl": False, "rgb_hsl": False, \
                                                       "rgb_hex": False, "hsl_hex": False, "hsl_rgb": False, \
                                                     "hsl_hsv": False, "hsv_hsl": False, "hsv_hex": False, \
                                                      "hsv_rgb": False, "name_hex": False, "name_rgb": False, \
                                                      "colorswap_hex": { "active": False, "order": "r_to_g" }, \
                                                      "colorswap_rgb": { "active": False, "order": "r_to_g" }, \
                                            "lightdark_hex": { "active": False, "mode": "darken", "percent": 10 }, \
                                            "lightdark_rgb": { "active": True, "mode": "lighten", "percent": 10 } } )


# In[162]:


# Run ALL tests!
file_color_processor("test_modified.txt", "test.txt",  "match_log.txt", black_filename="blacklist.json", options={ "hex_rgb": True, "hex_hsl": True, "rgb_hsl": True, \
                                                       "rgb_hex": True, "hsl_hex": True, "hsl_rgb": True, \
                                                     "hsl_hsv": True, "hsv_hsl": True, "hsv_hex": True, \
                                                      "hsv_rgb": True, "name_hex": True, "name_rgb": True, \
                                                      "colorswap_hex": { "active": True, "order": "r_to_g" }, \
                                                      "colorswap_rgb": { "active": True, "order": "r_to_g" }, \
                                            "lightdark_hex": { "active": True, "mode": "darken", "percent": 10 }, \
                                            "lightdark_rgb": { "active": True, "mode": "lighten", "percent": 10 } } )


# In[ ]:





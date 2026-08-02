"""
Top-level module for file color code processing using RegEx for term matching within user-supplied
text content files. This file contains the file_color_processor() (parent) and
process_lines_with_regex() (child function).

Also handles errors found matching and reports the results as a series of status objects, saved
to a specified log file.

The "options" data object is loaded as a dictionary from JSON as supplied via the user interface/API,
if present.
"""

import re
import os
from color_functions import *
from .utils.file_functions import load_dict_from_json, write_log_file


# ================ REGEX EXPRESSIONS FOR TERM MATCHING ==========
# These are used for term (string) matching in process_lines_with_regex()
REGEX_HEX = re.compile(r"(:\s*)(#[a-zA-Z0-9]{3,8})(;)")
REGEX_RGB = re.compile(r"(?i)(:\s*)(rgb\((?:\s*[0-9]+,)+(?:\s*[0-9])+\))(;)") # Note: uses case flag 'i'
REGEX_HSL = re.compile(r"(?i)(:\s*)(hsl\((?:\s*[0-9]+,)+(?:\s*[0-9])+\))(;)") # Note: uses case flag 'i'
REGEX_HSV = re.compile(r"(?i)(:\s*)(hsv\((?:\s*[0-9]+),(?:\s*[0-9]+%,?)+\))(;)") # Note: uses case flag 'i'
REGEX_NAME = re.compile(r"(?i)(:\s*)([a-zA-Z]{3,})(;)") # Uses case-insensitive flag
# ===============================================================


# Top level function for processing a file & using matched values to call color functions as specified
def file_color_processor(target_filename, source_filename, options, logfile_name_path="", white_filename="", black_filename="") -> dict:
    '''
    Top level function to read, write, and manipulate files while using color functions based on the user JSON 
    options received.

    Accepts:
    - target_filename: name & path (string) for the output file; typically the file received via an API request.
    - source_filename: Same as above, but the file while will be processed & output in the name/path <target_filename>
    - options: dict object structure containing color code functionality options. See "dev_notes.md" for the
    - logfile_name_path: (optional) Specifies name/path for log file to be written, if present.
      example. Must contain all key/value pairs, even if not used.
    - white_filename: (optional) color code whitelist filename & path. If present, will be loaded as a list and
      passed to process_lines_with_regex(). Whitelist = ONLY these color codes (strings) will be modified if a match
      is found in the source file.
    - black_filename: (optional) The inverse of above - process_lines_with_regex() will match/modify all color values
      EXCEPT those in the blacklist.
      
    
    Outputs: 
    - (optional) Logfile containing report objects (dicts) with data counts all changes made or skipped and any errors.
      One status report object is written to the log file for each color function used.
    
    Note: 
    • Both whitelist *and* blacklist cannot both be used; if both are passed to the function, whitelist file
    takes precedence and the blacklist is ignored.
    • If a whitelist or blacklist is supplied, the status of reading the file & loading the data is reported to the
    logfile as well, if "logfile_name_path" is provided, before the report objects.
    '''
    # report = { "lines": 0, "changes": 0, "skipped": 0, "error_stats": {} } # Tracks changes made and error values
    # linecount = report["lines"] # Alias variable
    reports = {}
    
    # As the name color function is a special case, additional parameters are used when calling. To preserve passing
    # a function to process_lines_with_regex(), bind the required arguments prior to passing the function.
    named_color_to_hex = lambda color_name: named_color_to_value(color_name, color_name_dict=options, \
                                                                 code_format="hex")
    named_color_to_rgb = lambda color_name: named_color_to_value(color_name, color_name_dict=options, \
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
        report = process_lines_with_regex(hex_to_rgb, REGEX_HEX, target_filename, source_filename, whitelist, blacklist)
        reports |= { "hex_rgb": report }
            
    if options["hex_hsl"] == True:
        report = process_lines_with_regex(hex_to_hsl, REGEX_HEX, target_filename, source_filename, whitelist, blacklist)
        reports |= { "hex_hsl": report }        

    
    # -----------------------------------    
    if options["rgb_hsl"] == True:
        report = process_lines_with_regex(rgb_to_hsl, REGEX_RGB, target_filename, source_filename, whitelist, blacklist)
        reports |= { "rgb_hsl": report }        
            
    if options["rgb_hex"] == True:
        report = process_lines_with_regex(rgb_to_hex, REGEX_RGB, target_filename, source_filename, whitelist, blacklist)
        reports |= { "rgb_hex": report }            

    
    # -----------------------------------    
    if options["hsl_hex"] == True:
        report = process_lines_with_regex(hsl_to_hex, REGEX_HSL, target_filename, source_filename, whitelist, blacklist)
        reports |= { "hsl_hex": report }            

    if options["hsl_rgb"] == True:
        report = process_lines_with_regex(hsl_to_rgb, REGEX_HSL, target_filename, source_filename, whitelist, blacklist)
        reports |= { "hsl_rgb": report }                  

    if options["hsl_hsv"] == True:
        report = process_lines_with_regex(hsl_to_hsv, REGEX_HSL, target_filename, source_filename, whitelist, blacklist)
        reports |= { "hsl_hsv": report }                  

    
    # -----------------------------------    
    if options["hsv_hsl"] == True:
        report = process_lines_with_regex(hsv_to_hsl, REGEX_HSV, target_filename, source_filename, whitelist, blacklist)
        reports |= { "hsv_hsl": report }          
        
    if options["hsv_hex"] == True:
        report = process_lines_with_regex(hsv_to_hex, REGEX_HSV, target_filename, source_filename, whitelist, blacklist)
        reports |= { "hsv_hex": report }          

    if options["hsv_rgb"] == True:
        report = process_lines_with_regex(hsv_to_rgb, REGEX_HSV, target_filename, source_filename, whitelist, blacklist)
        reports |= { "hsv_rgb": report }   
        

    # -----------------------------------
    # Convert a CSS color name to a value code - requires the color reference dict to be passed
    if options["name_hex"] == True:
        report = process_lines_with_regex(named_color_to_hex, REGEX_NAME, target_filename, \
                                          source_filename, whitelist, blacklist)
        reports |= { "name_hex": report }        
        
    if options["name_rgb"] == True:
        report = process_lines_with_regex(named_color_to_rgb, REGEX_NAME, target_filename, \
                                          source_filename, whitelist, blacklist)
        reports |= { "name_rgb": report }          

    
    # -----------------------------------
    if options["colorswap_hex"]["active"] == True:
        # Bind 2nd argument to the color function to work with passing the function to the line process function
        color_swap_hex_order = lambda color_val: color_swap_hex(color_val, order=options["colorswap_hex"]["order"])
        
        report = process_lines_with_regex(color_swap_hex_order, REGEX_HEX, target_filename, \
                                          source_filename, whitelist, blacklist)
        reports |= { "colorswap_hex": report }              

    if options["colorswap_rgb"]["active"] == True:
        # Bind 2nd argument to the color function to work with passing the function to the line process function
        color_swap_rgb_order = lambda color_val: color_swap_rgb(color_val, order=options["colorswap_rgb"]["order"])
        
        report = process_lines_with_regex(color_swap_rgb_order, REGEX_RGB, target_filename, \
                                          source_filename, whitelist, blacklist)
        reports |= { "colorswap_rgb": report }        


    # -----------------------------------    
    if options["lightdark_hex"]["active"] == True:
        # Function: adjust_lightness_rgb(color_val, percent=10, mode="lighten", to_string=True)
        
        # Bind arguments to 2 & 3 to the color function to work with passing the function. Arg. 4 is default value.
        adjust_lightness_hex_color_val = lambda color_val: \
                                    adjust_lightness_hex(color_val, percent=options["lightdark_hex"]["percent"], \
                                     mode=options["lightdark_hex"]["mode"])
        
        report = process_lines_with_regex(adjust_lightness_hex_color_val, REGEX_HEX, target_filename, \
                                          source_filename, whitelist, blacklist)
        reports |= { f"lightdark_hex ({options["lightdark_hex"]["mode"]})": report }        

    if options["lightdark_rgb"]["active"] == True:
        # Function: adjust_lightness_rgb(color_val, percent=10, mode="lighten", to_string=True)
        
        # Bind arguments to 2 & 3 to the color function to work with passing the function. Arg. 4 is default value.
        adjust_lightness_rgb_color_val = lambda color_val: \
                                    adjust_lightness_rgb(color_val, percent=options["lightdark_rgb"]["percent"], \
                                     mode=options["lightdark_rgb"]["mode"])
        
        report = process_lines_with_regex(adjust_lightness_rgb_color_val, REGEX_RGB, target_filename, \
                                          source_filename, whitelist, blacklist)
        reports |= { f"lightdark_rgb ({options["lightdark_rgb"]["mode"]})": report }        

    
    # -----------------------------------        
    # Save match status reports to a log file
    # function: write_log_file(filename_path, data_object, color_mode, write_mode="a"):
    for rep_key, rep_val in reports.items():
        write_log_file(logfile_name_path, data_object=rep_val, color_mode=rep_key)


# Child function called by file_color_processing - process a specified file one line at a time when called by
# the file process, as specified by the options dictionary passed to that function
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

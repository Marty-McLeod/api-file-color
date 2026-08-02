import json

# Open the color names file and loads as a dictionary object for reference use
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


# Called for writing file processing data & errors to a log file
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
        title_string = f"{'---' * 3} STATUS FOR OPERATION {color_mode} {'---' * 3}"
        file.write(title_string + "\n")
        json.dump(data_object, file, indent=2)
        file.write("\n\n")
        file.write(f'{data_object["changes"]} replacement(s) made out of {data_object["lines"]} lines. ')
        file.write(f'{data_object["skipped"]} invalid terms skipped.')
        file.write("\n")
        file.write(f"{'-' * len(title_string)}\n")
        file.write("\n")
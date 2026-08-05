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
def write_log_file(logfile_namepath, data_object, source_filename="", style="", write_mode="a"):
    '''
    Saves matching status & error data to a log file.
    Accepts: 
    - filename_path: file name & path for log file created/appended.
    - data_object: dict containing status data and errors. Must contain keys: "changes", "lines", "skipped."
    - style: String indicating the type of text output format: JSON style (default) or a more user-friendly
      "text" format (Sentences only, not JSON objects).
    - write_mode: (default standard append/create new) allows changing the file write access mode
    '''
    with open(logfile_namepath, write_mode, newline="\n", encoding="utf-8") as file:
        # Start of logfile: name the current source file being logged
        title_string = f"{'===' * 3} Results for file '{source_filename}' {'===' * 3}"
        file.write(title_string + "\n\n")
        
        # Use a stylized output to the text file, as opposed to the default "dump" of the JSON status
        # report objects. This is a more user-friendly format.
        if style=='text':
            # Iterate of the nested record dicts (i.e., iterates over the dict keys/names) and 
            # access the nested data by reference/key/value pairs in each iterated item
            for record in data_object:
                # Summary of changes made or not made (skipped due to errors)
                summary_title = " "*10 + f" Summary ('{record}'): " + " "*10
                
                file.write("-"*len(summary_title) + "\n") # separating lines                
                file.write(f"Function/mode: '{record}'. Lines scanned: {data_object[record]["lines"]}\n")
                file.write("\nERROR REPORT:\n")
                # iterate over each record's keys & values for the error stats, write all errors in the value
                # (list of strings) out for each error number (key string)
                for k,v in data_object[record]["error_stats"].items():
                    # Output as <error num>: <error string, error string, ...>
                    file.write(f"{k:>2}: {'\n    '.join(v)}\n")
                    
                file.write("\n")

                file.write(summary_title)
                file.write("\n")
                file.write(f"{data_object[record]["changes"]} replacement(s) made out of"
                          f" {data_object[record]["lines"]} lines.\n")
                file.write(f"{data_object[record]["skipped"]} invalid terms skipped.\n")
                file.write("-"*len(summary_title) + "\n") # separating lines 
                file.write("\n\n")
        else: # Output each record object in JSON style format + a short summary of stats at the end
            for record in data_object:
                # Summary of changes made or not made (skipped due to errors)
                summary_title = "-"*10 + f" Summary ('{record}'): " + "-"*10
                file.write(summary_title)              
                file.write("\n")               
                json.dump(data_object[record], file, indent=2)

                file.write("\n\n")
                file.write(f"{data_object[record]["changes"]} replacement(s) made out of"
                          f" {data_object[record]["lines"]} lines.\n")
                file.write(f"{data_object[record]["skipped"]} invalid terms skipped.\n")
                file.write("-"*len(summary_title) + "\n") # separating lines 
                file.write("\n\n")
            
        file.write("\n")
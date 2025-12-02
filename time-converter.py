# Authors: Gannon Strand, Mei Miller
# Validating: Bryanna Rosales-Hernandez

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import time

current_line = None

def read_request():
    # time_date,current_zone,desired_zone
    # function returns a tuple if valid with (time_date,current_zone,desired_zone)
    global current_line
    try:
        with open("time-converter-requests.txt", "r+") as f:
            lines = f.readlines()
            for x, line in enumerate(lines):
                if not line.strip():
                    continue
                line_data = line.split(',')
                number_of_elements = len(line_data)
                if number_of_elements < 3:
                    continue
                else:
                    time_date = line_data[0].strip()
                    current_zone = line_data[1].strip()
                    desired_zone = line_data[2].strip()
                    check = check_valid(time_date, current_zone, desired_zone)
                    if check == False:
                        continue
                    else:
                        current_line = x
                        return check
    except FileNotFoundError:
        return


def check_valid(time_date, current_zone, desired_zone):
    try:
        time_date = datetime.fromisoformat(time_date)
        current_zone = ZoneInfo(current_zone)
        desired_zone = ZoneInfo(desired_zone)
    except (ValueError, ZoneInfoNotFoundError):
        return False
    return time_date, current_zone, desired_zone

def clear_command(current_command_line):
    with open("time-converter-requests.txt", "r+") as f:
        lines = f.readlines()
        if 0 <= current_command_line < len(lines):
            del lines[current_command_line]
        f.seek(0)
        f.writelines(lines)
        f.truncate()

def time_conversion(time_date, current_zone, desired_zone):
    # Function to deal with the actual converting of time, could return or call the output function directly.
    localized_time = time_date.replace(tzinfo=current_zone)
    converted_time = localized_time.astimezone(desired_zone)
    time_output(converted_time)

def time_output(output_time):
    # Function to write to the output file based on the time conversion.
    with open("time-converter-response.txt", "w+") as f:
        #Leaves in iso format for easy retrieval from main program
        print("Time outputted: " + str(output_time.isoformat()))
        f.write(output_time.isoformat())



while True:
    validity = read_request()
    if isinstance(validity, tuple):
        # Run other commands to convert time.
        time_date = validity[0]
        current_zone = validity[1]
        desired_zone = validity[2]
        time_conversion(time_date, current_zone, desired_zone)
        clear_command(current_line)
    #print("Listening for command...")
    time.sleep(1)
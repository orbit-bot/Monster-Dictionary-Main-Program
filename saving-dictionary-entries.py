# Authors: Gannon Strand, Thania Cisneros, Mei Miller

import time

def read_request():
    # function to read the dictionary entry entered into save-dict.txt
    try:
        with open("save-dict.txt", "r+") as f:
            lines = f.readlines()
            for x, line in enumerate(lines):
                if not line.strip():
                    continue
                dictionary_entry = line.strip()
                clear_line(x)
                return dictionary_entry
    except FileNotFoundError:
        return
    
def clear_line(current_line):
    # function to clear the current dictionary entry after reading it.
    with open("save-dict.txt", "r+") as f:
        lines = f.readlines()
        if 0 <= current_line < len(lines):
            del lines[current_line]
        f.seek(0)
        f.writelines(lines)
        f.truncate()
        
def get_next_id():
    # function returns the next unique integer ID based on the db file.
    try:
        with open("dictionary-db.txt", "r", encoding="utf-8") as db:
            lines = [ln.strip() for ln in db.readlines() if ln.strip()]
        if not lines:
            return 1
        last_line = lines[-1]
        first_part = last_line.split("|", 1)[0]
        return int(first_part) + 1
    except FileNotFoundError:
        # returns first entry if there's no DB yet
        return 1
    except (ValueError, IndexError):
        return 1

def process_entry(dictionary_entry):
    # function to process the entry and save it into dictionary-db.txt and it uses a unique number as a reference.
    entry_id = get_next_id()

    line_to_store = f"{entry_id}|{dictionary_entry}"

    # Append to the database file
    with open("dictionary-db.txt", "a", encoding="utf-8") as db:
        db.write(line_to_store + "\n")

    return entry_id

def output_handler(entry_id, dictionary_entry):
    # function to deal with the output (maybe that unique number if going with that implementation)
    print(f"Saved Entry ID #{entry_id}: '{dictionary_entry}'")


while True:
    check = read_request()
    if check != None:
        entry_id = process_entry(check)
        output_handler(entry_id, check)
        
    time.sleep(2)
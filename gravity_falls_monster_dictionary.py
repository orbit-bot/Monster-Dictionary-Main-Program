import time
from datetime import datetime, timezone

#Stores current session
current_user = ''

#main menu
#IH1: explain new + existing features
print("Welcome to the legendary and elusive Gravity Falls Monster Dictionary!")
print("This is a compilation of the most common monsters and cryptids in our town.")
print("You'll be able to browse different monster entries, as well as add/delete them.")

#Microservice 1:action,username,password
"""Microservice-oriented function definitions"""
def login_or_register_user(cmd_line):
    #action,username,password
    with open("main-program.txt", "a", encoding="utf-8") as f:
        f.write(cmd_line.strip() + "\n")

def check_login_result(username):
    """Check if login was successful for a given username"""
    print("[[Checking for successful login...]]\n")
    try:
        with open("auth-responses.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) >= 3:
                    status = parts[0] #"valid" or "invalid"
                    action = parts[1] #"login"
                    user = parts[2]   #username
                    
                    if action == "login" and user == username:
                        return status == "valid"
        return None  # Not found yet
    except FileNotFoundError:
        return None

def check_register_result(username):
    try:
        with open("auth-responses.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) >= 3:
                    status = parts[0]      # "valid" or "invalid"
                    action = parts[1]      # "register"
                    user = parts[2]        # username
                    
                    if action == "register" and user == username:
                        return status == "valid"
        return None  # Not found yet
    except FileNotFoundError:
        return None

#Microservice 3: user,action format
def action_log(username, action):
    print("[[Requesting action log]]\n")
    with open("uha-input.txt", "a") as f:
        f.write(username + "," + action)

def request_archive_erase():
    print("Requesting archive erase.\n")
    with open("uha-input.txt", "a") as f:
        f.write("erase")

def retrieve_archive():
    print("Retrieving actions...")
    with open("uha-output.txt", "r") as f:
        content = f.read().strip()
        if not content:
            print("\nNo data to show.\n")
            return
        print(content)

#Microservice 2: dictionary entry, newline format
def add_to_dictionary(entry):
    print("[[Requesting adding to dictionary]]\n")
    with open("save-dict.txt", "a") as f:
        f.write(entry + "\n")
        print("Entry added successfully!")

def retrieve_dictionary():
    with open("dictionary-db.txt", "r") as f:
        content = f.read().strip()
        if not content:
            print("\nDictionary is currently empty.\n")
            return
        print(content)

#Microservice 4: current datetime, current timezone, and desired timezone
def get_time():
    print("[[Requesting time...]]\n")
    current_datetime = datetime.now()
    with open("time-converter-requests.txt", "w") as in_file:
        in_file.write(f"{current_datetime.isoformat()},America/Los_Angeles,America/New_York\n")
    time.sleep(3)
    with open("time-converter-response.txt", "r") as out_file:
        content = out_file.read().strip()
    if not content:
        print("Error: Response file is empty.")
        return
    try:
        converted_time = datetime.fromisoformat(content)
        print(f"Oregon time (local): {current_datetime}")
        print(f"Washington D.C time: {converted_time}\n")
    except ValueError as e:
        print(f"Error: {e}")

"""main program related functions"""
def menu_choice_1():
    print("\nSearch by name allows you to look up a monster by name. Ensure your entry is lowercase, singular, and typed exactly.")
    name_search = input("Type in the monster name, or type 2 to go back: ")
    if (name_search == '2'):
        print("Going back to main menu...")
    else:
        try:
            with open("dictionary-db.txt", "r") as f:
                dict_line = []
                for line_number, line in enumerate(f, 1):
                    if name_search in line:
                        dict_line.append(line_number)
                        print(line.strip() + "\n")  #prints matching line
            
            if not dict_line:
                print("No such monster exists.")
        except FileNotFoundError:
            print("Dictionary file not found.")

def menu_choice_2():
    browse_choice = input("\nThis option will print all info currently in this dictionary.\nEnter 1 to continue and enter 2 to go back:")
    if (browse_choice == '2'):
        print("Going back to main menu...")
    elif(browse_choice == '1'):
        retrieve_dictionary()

def menu_choice_3():
    #IH2:Explain (to Users) the Costs of Using New and Existing Features
    print("\nIf you add an entry, it will permanently remain for archival purposes.")
    add_choice = input("Enter the monster name for the entry, or enter 2 to go back: ")
    if (add_choice == '2'):
        print("Going back to main menu...")
    else:
        entry_value = input("Enter the name & description of the monster: ")
        add_to_dictionary(entry_value)
        

"""
def menu_choice_4():
    delete_choice = input("Enter the monster name to permanently delete its entry or enter 2 to go back: ")
    if (delete_choice == '2'):
        print("Going back to main menu...")
    else:
        
        confirmation = input("Are you sure you want to remove this entry? This cannot be undone.\n1: Yes\n2: No\n")
        if (confirmation == '1'):
            if (monster_dictionary.get(delete_choice)):
                monster_dictionary.pop(delete_choice)
                print("Successfully deleted entry.")
            else:
                print("Invalid entry!")
"""

def menu_choice_4():
    archive_choice = input("Press 1 to view all logs, press 2 to delete all logs: ")
    if (archive_choice == '1'):
        retrieve_archive()
    elif (archive_choice == '2'):
        #IH8: Encourage Tinkerers to Tinker Mindfully
        confirmation = input("Are you sure? This will permanently delete the logs. Yes/No: ")
        if (confirmation.lower() == "yes"):
            request_archive_erase()

def menu_choice_5():
    print("Fetching time...\n")
    get_time()
    

while True:
    #IH6: Provide an Explicit Path through the Task
    login_option = input("\nEnter 1 to Log in, Enter 2 to Create an Account. Enter 3 to exit.\n")

    if (login_option == '1'):
        while True:
            username = input("Enter your username: ")
            password = input("Enter your password: ")

            login_or_register_user("login,"+ username + "," + password)
            print("Processing...")
            time.sleep(4)
            auth_response = check_login_result(username)

            if auth_response == True:
                print("Logged in successfully.")
                current_user = username
                action_log(current_user, "login")
                break
            elif auth_response == False:
                print("Incorrect credentials.")

    if (login_option == '2'):
        username = input("Enter your account's username: ")
        password = input("Enter your account's password: ")
        #users.update({username: password})
        login_or_register_user("register," + username + "," + password)
        print("Processing...")
        time.sleep(4)
        auth_response = check_register_result(username)

        if auth_response == True:
            print(f"You are now logged in as {username}.")
            current_user = username
            action_log(current_user, "register")
        elif auth_response == False:
            print("Registration failed.")

    if (login_option == '3'):
        break

    #IH7: provide ways of different approaches
    #IH5: make undo, backtracking available
    #IH4: make familiar features available (keeping the menu easily accessible)
    menu_choice = input("Enter 1: Search by Name\nEnter 2: Browse\nEnter 3: Add Entry\nEnter 4: Access/Remove Logs\nEnter 5: Get DC Time\nEnter 6: Back\n")
    while (menu_choice != '6'):
        #IH3: let users gather information
        
        #search by name
        if (menu_choice == '1'):
            menu_choice_1()

        #IH 6
        if (menu_choice == '2'):
            menu_choice_2()
            
        if (menu_choice == '3'):
            menu_choice_3()

        if (menu_choice == '4'):
            menu_choice_4()
        
        if (menu_choice == '5'):
            menu_choice_5()

        menu_choice = input("Enter 1: Search by Name\nEnter 2: Browse\nEnter 3: Add Entry\nEnter 4: Access/Remove Logs\nEnter 5: Get DC Time\nEnter 6: Back\n")




# Author: Thania Cisneros
# Debugging: Bryanna Rosales

# The program reads a command from main-program.txt and sends it to the right microservice by writing the following lines:
# Auth -> writres to user-action.txt and  notifications -> writes to notification-microservice.txt
# Then the program waits for Auth's answer in auth-reponses.txt and prints the results and adds them to demo_transcript.txt
# Deletes the processed lines from main-rpogram.txt so it doesn't run twice
# This repeats every 2 seconds. 

import time
import random
import os

# Files this main program uses
AUTH_IN   = "user-action.txt"                    # send commands to Auth
AUTH_OUT  = "auth-responses.txt"                 # read results from Auth
NOTIFY_IN = "notification-microservice.txt"      # send commands to Notifications
MAIN_IN   = "main-program.txt"                   # this file tells the main program what to do
TRANSCRIPT= "demo_transcript.txt"                # optional: where we print what happened
DATABASE   = "database.txt"               

def _ensure_files():
    # create empty files if they don't exist
    for p in [AUTH_IN, AUTH_OUT, NOTIFY_IN, MAIN_IN, TRANSCRIPT, DATABASE]:
        if not os.path.exists(p):
            open(p, "a", encoding="utf-8").close()

def _consume_line(all_lines, line_to_remove, f_handle):
    all_lines.remove(line_to_remove)
    f_handle.seek(0)
    f_handle.truncate()
    f_handle.writelines(all_lines)

def _say(*args):
    msg = " ".join(str(a) for a in args)
    print(msg)
    _append(TRANSCRIPT, msg)

def _append(path, text):
    with open(path, "a", encoding="utf-8") as f:
        f.write(text.strip() + "\n")

def user_exists(username):
    with open(DATABASE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "," not in line:
                continue  # skip malformed lines
            stored_user, _ = line.split(",", 1)
            if stored_user == username:
                return True
    return False

def send_register(username, password):
    if user_exists(username):
        return "username-already-exists"
    store_user(username, password)
    _append(AUTH_IN, f"credential-action,{username},{password}")
    return "registered"

def store_user(username, password):
    _append(DATABASE, f"{username},{password}")

def send_login(username, password):
    # request-credentials,username,password
    _append(AUTH_IN, f"request-credentials,{username},{password}")

def send_forgot(username):
    # forgot-password,username
    _append(AUTH_IN, f"forgot-password,{username}")

def wait_auth(action, username):
    timeout=5.0
    end = time.time() + timeout
    while time.time() < end:
        try:
            with open(AUTH_OUT, "r+", encoding="utf-8") as f:
                lines = f.readlines()
                for ln in lines:
                    ln = ln.strip()
                    if not ln:
                        continue
                    parts = [p.strip() for p in ln.split(",")]
                    if len(parts) >= 3:
                        status, act, uname = parts[0], parts[1], parts[2]
                        if act == action and uname == username:
                            lines = [l for l in lines if l.strip() != ln]
                            return ln
        except FileNotFoundError:
            with open("error-log.txt", "a") as f:
                f.write("user-authentication,File Not Found,3\n")
            pass
        time.sleep(0.1)
    return "timeout-waiting-for-auth"

def send_notification(email, when_iso=None):
    
    #   send-email,email,time   OR   send-email,email
    if when_iso:
        _append(NOTIFY_IN, f"send-email,{email},{when_iso}")
    else:
        _append(NOTIFY_IN, f"send-email,{email}")

def read_request():
    """
    Reads main-program.txt and performs one command per run. """
  
    try:
        with open(MAIN_IN, "r+", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if not line.strip():
                    continue
                data = [p.strip() for p in line.split(",")]
                cmd = data[0]

                # register
                if cmd == "register":
                    if len(data) < 3:
                        _say("bad-register-command")
                        _consume_line(lines, line, f)
                        return "bad-register-command"
                    user, pwd = data[1], data[2]
                    resp = send_register(user, pwd)
                    if resp == "username-already-exists":
                        _say(f"register -> username '{user}' already exists")
                        _consume_line(lines, line, f)
                        return resp
                    # still send to Auth for demo
                    verify(data[1], data[2], data[0])
                    resp_auth = wait_auth("register", user)
                    _say("register ->", resp_auth)
                    _consume_line(lines, line, f)
                    return resp_auth

                # login
                if cmd == "login":
                    if len(data) < 3:
                        _say("bad-login-command")
                        _consume_line(lines, line, f)
                        return "bad-login-command"
                    user, pwd = data[1], data[2]
                    send_login(user, pwd)
                    verify(data[1], data[2], data[0])
                    resp = wait_auth("login", user)
                    _say("login ->", resp)
                    _consume_line(lines, line, f)
                    return resp

                # forgot
                if cmd == "forgot":
                    if len(data) < 2:
                        _say("bad-forgot-command")
                        _consume_line(lines, line, f)
                        return "bad-forgot-command"
                    user = data[1]
                    new_password = data[2] if len(data) >= 3 else None
                    send_forgot(user)
                    verify(data[1], data[2], data[0])
                    resp = wait_auth("forgot", user)
                    if new_password and user_exists(user):
                        with open(DATABASE, "r+", encoding="utf-8") as db:
                            db_lines = db.readlines()
                            db.seek(0)
                            db.truncate()
                            for l in db_lines:   
                                if not l.strip():
                                    continue
                                stored_user, _ = l.strip().split(",", 1)
                                if stored_user == user:
                                    db.write(f"{user},{new_password}\n")
                                else:
                                    db.write(l)
                    _say("forgot ->", resp)
                    _consume_line(lines, line, f)
                    return resp

                # notify
                if cmd == "notify":
                    # notify,email[,time]
                    if len(data) < 2:
                        _say("bad-notify-command")
                        _consume_line(lines, line, f)
                        return "bad-notify-command"
                    if len(data) == 2:
                        email = data[1]
                        send_notification(email)
                        _say("notify -> queued", email)
                        _consume_line(lines, line, f)
                        return "notify-queued"
                    elif len(data) >= 3:
                        email, when_iso = data[1], data[2]
                        send_notification(email, when_iso=when_iso)
                        _say("notify -> queued", email, when_iso)
                        _consume_line(lines, line, f)
                        return "notify-queued"
                    else:
                        _consume_line(lines, line, f)
                        return "bad-notify-command"

                # Sleep 
                if cmd == "sleep":
                    try: 
                    # sleep,seconds
                        secs = float(data[1]) if len(data) >= 2 else 1.0
                    except ValueError:
                        _say("bad-sleep-command")
                        _consume_line(lines,line,f)
                        return "bad-sleep-command"
                    time.sleep(secs)
                    _say(f"slept {secs}s")
                    _consume_line(lines, line, f)
                    return f"slept-{secs}"

                # echo 
                if cmd == "echo":
                    msg = ",".join(data[1:]) if len(data) > 1 else ""
                    _say(msg)
                    _consume_line(lines, line, f)
                    return msg

            return "no-commands"
    except FileNotFoundError:
        with open("error-log.txt", "a") as f:
                f.write("user-authentication,File Not Found,3\n")
        return "no-main-program-file"

def verify(username, password, process):
    try:
        valid = False
        with open(DATABASE, "r") as f:
            lines = f.readlines()
            for line in lines:
                list = line.strip().split(',')
                if (process == 'forgot' and list[0] == username):
                    valid = True
                elif (list[0] == username and list[1] == password):
                    valid = True
        if (valid == False):
            with open(AUTH_OUT, "w") as f:
                f.write("invalid,"+process+','+username)
        if (valid == True):
            with open(AUTH_OUT, "w") as f:
                f.write("valid,"+process+','+username)
    except FileNotFoundError:
        with open("error-log.txt", "a") as f:
                f.write("user-authentication,File Not Found,3\n")
        pass


_ensure_files()
print(f"Main program watching {MAIN_IN}")
while True:
    result = read_request()
    #if result == "no-commands":
        #_say("no commands, sleeping...")
    time.sleep(2)
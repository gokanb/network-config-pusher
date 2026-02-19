# Importing libraries
import paramiko
import os.path
import time
import sys
import re

# Asking user input file path and name.
user_file = input("\n[+] Enter user file path and name (e.g. D:\MyApps\myfile.txt): ")

# Checking if the user file path is valid
if os.path.isfile(user_file):
    print("\n[+] Username/password file is valid :)\n")
else:
    print("\n[-] File {} does not exist :( Please check and try again. \n".format(user_file))
    sys.exit()

# Asking user input for commands file path and name.
cmd_file = input("\n[+] Enter commands file path and name (e.g. D:\MyApps\myfile.txt): ")

# Checking if the commands file path is valid
if os.path.isfile(cmd_file):
    print("\n[+] Command file is valid :)\n")
else:
    print("\n[-] File {} does not exist :( Please check and try again.\n".format(cmd_file))
    sys.exit()


# SSH connection function
def ssh_connection(ip):
    global user_file
    global cmd_file

    try:
        with open(user_file, 'r') as selected_user_file:
            first_line = selected_user_file.readline()        
            username = first_line.split(',')[0].strip()       # of using readlines()[0] twice with seek(0)
            password = first_line.split(',')[1].strip()       # Also replaced rstrip("\n") with strip() for safety

        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        session.connect(ip.strip(), username=username, password=password)

        connection = session.invoke_shell()
        connection.send("enable\n")
        connection.send("terminal length 0\n")
        time.sleep(1)
        connection.send("\n")
        connection.send("configure terminal\n")
        time.sleep(1)

        with open(cmd_file, 'r') as selected_cmd_file:
            for each_line in selected_cmd_file.readlines():
                connection.send(each_line.strip() + '\n')    
                time.sleep(2)                                 # sending extra whitespace/newlines

        router_output = connection.recv(65535)               

        if re.search(b"% Invalid input", router_output):
            print("* There was at least one IOS syntax error on device {} :(".format(ip))
        else:
            print("\n[+] DONE for device {} :)\n".format(ip))
            print(str(router_output) + "\n")

        session.close()

    except paramiko.AuthenticationException:
        print("* Invalid username or password :(\n* Please check the username/password file or the device configuration.")
        print("* Closing program... Bye!")            
    except Exception as e:                             
        print(f"* An unexpected error occurred: {e}")  # to catch other potential errors


# Example usage - call the function with a target IP
# ssh_connection("192.168.1.1")

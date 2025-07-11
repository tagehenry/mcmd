#!/bin/python3
# Author: Tage Henry <tage199819@gmail.com>
# Description: Multi-Command Remote Executor for running commands/scripts on multiple remote hosts via SSH.


import argparse
import paramiko
import datetime
import json
import getpass
import concurrent.futures

# ASCII art header for the script
mcmdart = """
                                 __
   ____ ___  _________ ___  ____/ /
  / __ `__ \/ ___/ __ `__ \/ __  /
 / / / / / / /__/ / / / / / /_/ /
/_/ /_/ /_/\___/_/ /_/ /_/\__,_/
===================================
   Multi-Command Remote Executor   
===================================
"""

#Function that handles the config file and loads the values from it
def config():
    #Opens the config file in read mode
    try:
        with open('config.json') as config_file:
            # Loads the config file as a JSON object
            config = json.load(config_file)
            #Grabs vaules of each key in the config file and assigns them to a variable, if there is no key found it will use the second argument as the default
            port = config.get('port', 22)
            username = config.get('username', 'username')
            password = config.get('password', 'password')
            defaultshowerrors = config.get('showerrorsdefault', True)
            command = config.get('command', 'command to run on remote device')
            commanddescription = config.get('commanddescription', 'mcmd')
            script_path = config.get('script_path', '/path/to/your/script.sh')
            threads = config.get('threads', 20)
            remote_script = f'nohup bash {script_path} > /dev/null 2>&1 &'
            return port, username, password, defaultshowerrors, command, commanddescription, script_path, remote_script, threads
    except FileNotFoundError:
        print("The file config.json was not found. Please copy config_default.json to config.json and edit it with your settings.")
        exit()
    except json.JSONDecodeError:
        print("Error decoding JSON from config.json")
        exit()

#Function to run the set command on the remote device, it will iterate through the iplist and run the command on each IP
def run_command(command, commanddescription, port, username, password, defaultshowerrors, output=False, error=False, log=False, threads=20):
    #Opens the IP list file in read mode (default)
    try:
        with open('iplist.txt') as file:
            ip_list = file.readlines()
    except FileNotFoundError:
        print("The file iplist.txt was not found")
        exit()
    if not ip_list:
        print("The file iplist.txt is empty")
        exit()

    if log:
        with open('mcmd.log', 'a') as logfile:
            logfile.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [INFO] Starting Multi-Command Remote Executor\n")

    def log_and_print(ip):
        if log:
            if commanddescription.startswith('Remote Script:'):
                logfile_msg = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [INFO] Running script '{commanddescription[14:]}' on {ip}"
            else:
                logfile_msg = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [INFO] Running {commanddescription} on {ip}"
            with open('mcmd.log', 'a') as logfile:
                logfile.write(logfile_msg + "\n")
        if commanddescription.startswith('Remote Script:'):
            print(f"Running script on IP: {ip}")
        else:
            print(f"Running {commanddescription} on IP: ", ip)

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for ip in ip_list:
            ip = ip.strip()
            log_and_print(ip)
            future = executor.submit(
                setup_ssh,
                ip, command, port, username, password, defaultshowerrors,
                output, error, log
            )
            futures.append(future)
        #Optionally, wait for all to complete and handle exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"A thread generated an exception: {exc}")

#Function to setup the SSH connection to the remote device and run the command it also handles logging and error handling
def setup_ssh(ip, command, port, username, password, defaultshowerrors, output=False, error=False, log=False):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port, username, password, timeout=10)
        stdin, stdout, stderr = client.exec_command(command)
        std_output = stdout.read().decode()
        std_error = stderr.read().decode()
        if std_output:
            if output:
                print(f"Output from {ip}:\n{std_output}")
            if log:
                with open('mcmd.log', 'a') as logfile:
                    logfile.write(f"{timestamp} [INFO] Output from {ip}: {std_output.strip()}\n")
        if std_error:
            if error or defaultshowerrors:
                print(f"Error from {ip}:\n{std_error}")
            if log:
                with open('mcmd.log', 'a') as logfile:
                    logfile.write(f"{timestamp} [ERROR] Error from {ip}: {std_error.strip()}\n")
    except paramiko.SSHException as e:
        print(f"Failed to connect to {ip}: {e}")
        if log:
            with open('mcmd.log', 'a') as logfile:
                logfile.write(f"{timestamp} [ERROR] Failed to connect to {ip}: {e}\n")
        return
    except Exception as e:
        print(f"An error occurred while connecting to {ip}: {e}")
        if log:
            with open('mcmd.log', 'a') as logfile:
                logfile.write(f"{timestamp} [ERROR] An error occurred while connecting to {ip}: {e}\n")
        return
    finally:
        client.close()

#Main function to handle the command line arguments (flags) and run the script
#It will also prompt for a password if the --unsecure or -u flag is not used and display the ASCII art at the start
def main():
    print(mcmdart)
    parser = argparse.ArgumentParser(description='Run a command on a list of IPs.')
    parser.add_argument('--unsecure', '-u', action='store_true', help='Will not ask for a password and will use the default password in the config file')
    parser.add_argument('--script', '-s', action='store_true', help='Runs a script that exists on the remote device')
    parser.add_argument('--verbose', '-v', action='store_true', help='Will display the output of the command in the console')
    parser.add_argument('-vv', action='store_true', help='Will show the output and errors of the command in the console')
    parser.add_argument('--log', '-l', action='store_true', help='Log all standard output to mcmd.log')
    args, unknown = parser.parse_known_args()
    #If there is an unsupported flag it will print the help message and exit
    if unknown:
        print(f"Unsupported flag(s): {' '.join(unknown)}")
        parser.print_help()
        exit(2)

    port, username, password, defaultshowerrors, command, commanddescription, script_path, remote_script, threads = config()

    if args.script:
        print("======= Remote Script Mode ========\n")
        commanddescription = f"Remote Script: {script_path}"

    if args.log:
        print("========= Logging Enabled =========\n")

    #Uses the default password from the config file if the --unsecure or -u flag is used otherwhise it will prompt for a password
    if args.unsecure:
        password_to_use = password
    else:
        password_input = getpass.getpass(prompt='Enter password for remote device(s): ')
        if not password_input:
            print("No password entered, using default password from config file")
            password_to_use = password
        else:
            password_to_use = password_input

    #If the --script or -s flag is used it will run the script on the remote device, if not it will run the command
    if args.script:
        if "/path/to/your/script.sh" in script_path:
            print("The default script path is being used, please edit the config.json file and change it to your own script path")
            exit()
        if args.verbose:
            run_command(remote_script, commanddescription, port, username, password_to_use, defaultshowerrors, output=True, log=args.log, threads=threads)
        elif args.vv:
            run_command(remote_script, commanddescription, port, username, password_to_use, defaultshowerrors, output=True, error=True, log=args.log, threads=threads)
        else:
            run_command(remote_script, commanddescription, port, username, password_to_use, defaultshowerrors, log=args.log, threads=threads)

    #If the --verbose or -v flag is used it will display the output of the command in the console
    elif args.verbose or args.vv:
        if "command to run on remote device" in command:
            print("The default command is being used, please edit the config.json file and change it to your own command")
            exit()
        print(f"Max Threads: {threads}")
        if args.verbose:
            run_command(command, commanddescription, port, username, password_to_use, defaultshowerrors, output=True, log=args.log, threads=threads)
        elif args.vv:
            run_command(command, commanddescription, port, username, password_to_use, defaultshowerrors, output=True, error=True, log=args.log, threads=threads)

    #If no flags are used it will just run the command on the remote device
    else:
        if "command to run on remote device" in command:
            print("The default command is being used, please edit the config.json file and change it to your own command")
            exit()
        run_command(command, commanddescription, port, username, password_to_use, defaultshowerrors, log=args.log, threads=threads)

if __name__ == "__main__":
    main()
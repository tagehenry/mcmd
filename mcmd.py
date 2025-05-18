#!/bin/python3
import argparse
import paramiko
import datetime

#Make sure to add the relevant port and credentials
port = 22
username = 'username'
password = 'password'

#This variable can be set to True or False. It will determine if standard errors from the command being ran will be displayed by default
defaultshowerrors = True

#These two variables below are used for when the -s or --script flag is used
script_path = '/path/to/your/script.sh'  # Absolute path to the script you want to run
remote_script = f'nohup bash {script_path} > /dev/null 2>&1 &'

command = """
command to run on remote device
"""

#This can be changed to be the command or description of the command being ran, by default it is set to "mcmd"
commanddescription = "mcmd"

def run_command(command, output=False, error=False, log=False):
    #Opens the IP list file in read mode (default)
    try:
        with open('iplist.txt') as file:
            ip_list = file.readlines()

    except FileNotFoundError:
        print("The file iplist.txt was not found")
        exit()

    # Write header to log if logging is enabled
    if log:
        with open('output.log', 'a') as logfile:
            logfile.write(f"\n=== Running {commanddescription} at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    # Itterates throught the list of IPs
    for ip in ip_list:
        ip = ip.strip()
        print(f"Running {commanddescription} on IP: ", ip)
        setup_ssh(ip, output=output, error=error, log=log)


def setup_ssh(ip, output=False, error=False, log=False):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port, username, password, timeout=10)
        stdin, stdout, stderr = client.exec_command(command)
        std_output = stdout.read().decode()
        std_error = stderr.read().decode()
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if std_output:
            if output:
                print(f"Output from {ip}:\n{std_output}")
            if log:
                with open('output.log', 'a') as logfile:
                    logfile.write(f"[{timestamp}] Output from {ip}:\n{std_output}\n")
        if std_error:
            if error or defaultshowerrors:
                print(f"Error from {ip}:\n{std_error}")
            if log:
                with open('output.log', 'a') as logfile:
                    logfile.write(f"[{timestamp}] Error from {ip}:\n{std_error}\n")
    except paramiko.SSHException as e:
        print(f"Failed to connect to {ip}: {e}")
        if log:
            with open('output.log', 'a') as logfile:
                logfile.write(f"[{timestamp}] Failed to connect to {ip}: {e}\n")
        return
    except Exception as e:
        print(f"An error occurred while connecting to {ip}: {e}")
        if log:
            with open('output.log', 'a') as logfile:
                logfile.write(f"[{timestamp}] An error occurred while connecting to {ip}: {e}\n")
        return
    finally:
        client.close()
def main():
    #Instantiates the ArgumentParser class and sets the description
    parser = argparse.ArgumentParser(description='Run a command on a list of IPs.')

    #Adds an optional flag option to the script named --script or -s
    parser.add_argument('--script', '-s', action='store_true', help='Runs an existing script on the remote device')

    #Adds another optional flag option to display the standard output from the command being ran
    parser.add_argument('--verbose', '-v', action='store_true', help='Runs an existing script on the remote device')

    #Adds another optional flag option to display the standard error and standard output from the command being ran
    parser.add_argument('-vv', action='store_true', help='Runs an existing script on the remote device')

    #Adds another optional flag option to log the standard output from the command being ran
    parser.add_argument('--log', '-l', action='store_true', help='Log all standard output to output.log')
    
    args = parser.parse_args()

    if args.script:
        if "/path/to/your/script.sh" in script_path:
            print("The default script path is being used, please change it to your own script")
            exit()
        if args.verbose:
            run_command(remote_script, output=True, log=args.log)
        elif args.vv:
            run_command(remote_script, output=True, error=True, log=args.log)
        else:
            run_command(remote_script, log=args.log)

        if "command to run on remote device" in command:
            print("The default command is being used, please change it to your own command")
            exit()
        run_command(command, log=args.log)
    
    elif args.verbose or args.vv:
        if args.verbose:
            run_command(command, output=True, log=args.log)
        elif args.vv:
            run_command(command, output=True, error=True, log=args.log)
            
    else:
        if "command to run on remote device" in command:
            print("The default command is being used, please change it to your own command")
            exit()
        run_command(command, log=args.log)

if __name__ == "__main__":
    main()
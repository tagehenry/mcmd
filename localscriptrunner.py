#!/bin/python3

import os
import paramiko
import getpass
import datetime

username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")


def local_script_ssh_uploader(script, remote_name, username, password, remote_ip, output=False, error=False, log=False, logfile=None):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=remote_ip, username=username, password=password)
        if log and logfile:
            logfile.write(f"{timestamp} [INFO] Uploading script as {remote_name} to {remote_ip}\n")
        if output:
            print(f"[{remote_ip}] [INFO] Uploading script as {remote_name}...")
        #Saves the local script on the remote device using cat
        stdin, stdout, stderr = ssh.exec_command(f"cat > {remote_name}")
        stdin.write(script)
        stdin.channel.shutdown_write()
        upload_err = stderr.read().decode()
        if upload_err:
            if error:
                print(f"[{remote_ip}] [ERROR] Upload error: {upload_err}")
            if log and logfile:
                logfile.write(f"{timestamp} [ERROR] Upload error: {upload_err}\n")
        stdout.channel.recv_exit_status()
        # Make script executable and run it on remote device. I was having issues getting stdout from echos so I added 'get_pty=True' which simulates a real terminal and is able to capture echos.
        stdin, stdout, stderr = ssh.exec_command(f"sudo chmod +x {remote_name} && {remote_name}", get_pty=True)
        if output:
            print(f"[{remote_ip}] [INFO] Executing {remote_name} on {remote_ip}...")
        if log and logfile:
            logfile.write(f"{timestamp} [INFO] Executing {remote_name} on {remote_ip}\n")
        print(f"[{remote_ip}] [INFO] Output from script:")
        #Prints standard output in real-time
        for line in iter(stdout.readline, ""):
            if output:
                print(f"[{remote_ip}] [SCRIPT] {line}", end="")
            if log and logfile:
                logfile.write(f"{timestamp} [SCRIPT] {line}")
        #Captures the exit status of the script execution (to check if it ran successfully)
        script_exit_status = stdout.channel.recv_exit_status()
        if script_exit_status != 0:
            if log and logfile:
                logfile.write(f"{timestamp} [ERROR] An error occurred when running {remote_name}.  Exit status: {script_exit_status}\n")
            if error:
                print(f"[{remote_ip}] [ERROR] An error occurred when running {remote_name}.  Exit status: {script_exit_status}")
        else:
            if log and logfile:
                logfile.write(f"{timestamp} [INFO] Script exit status: {script_exit_status}\n")
            if output:
                print(f"[{remote_ip}] [INFO] {remote_name} has finished executing successfully.")

        #Runs the rest of the commands to remove the script from the remote device. I chose to seperate these from the previous commands in order to capture the scripts exit status.
        stdin, stdout, stderr = ssh.exec_command(f"sleep 2 && sudo rm {remote_name}")
        for line in iter(stdout.readline, ""):
            if output:
                print(line, end="")
            if log and logfile:
                logfile.write(line)
        err = stderr.read().decode()
        if err:
            if error:
                print(f"[{remote_ip}] [ERROR] An error occurred while removing {remote_name}. Error: {err}")
            if log and logfile:
                 logfile.write(f"{timestamp} [ERROR] An error occurred while removing {remote_name}. Error: {err}\n")

        # Captures exit status of the remove script command
        cleanup_exit_status = stdout.channel.recv_exit_status()
        if cleanup_exit_status != 0:
            if error:
                print(f"[{remote_ip}] [ERROR] An error occurred while removing {remote_name}. Exit status: {cleanup_exit_status}")
            if log and logfile:
                logfile.write(f"{timestamp} [ERROR] An error occurred while removing {remote_name}. Exit status: {cleanup_exit_status}\n")
        else:
            if log and logfile:
                logfile.write(f"{timestamp} [INFO] {remote_name} was removed successfully. Exit status: {cleanup_exit_status}\n")
            if output:
                print(f"[{remote_ip}] [INFO] {remote_name} has successfully been removed from {remote_ip}")
    except Exception as e:
        print(f"[ERROR] {e}")
        if log and logfile:
            logfile.write(f"{timestamp} [ERROR] Exception: {e}\n")
    finally:
        ssh.close()


def local_script_handler(username, password, log=False, output=False, error=False):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #Grabs the path to the scripts directory
    scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
    #Creates a list of all files in the scripts directory
    files = [f for f in os.listdir(scripts_dir) if os.path.isfile(os.path.join(scripts_dir, f))]
    if output:
        print(f"[INFO] Detected scripts that will run on remote device:\n{files}")
    #Opens the IP list file in read mode (default)
    try:
        with open('iplist.txt') as file:
            ip_list = file.readlines()

    except FileNotFoundError:
        print("[WARNING] The file iplist.txt was not found")
        exit()
    if not ip_list:
        print("[WARNING] The file iplist.txt is empty")
        exit()
    logfile = None
    if log:
        logfile = open('mcmd.log', 'a')
        logfile.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [INFO] Starting Multi-Command Remote Executor\n")
    if not files:
        print(f"[WARNING] No scripts found in '{scripts_dir}'. Exiting..")
        if log and logfile:
            logfile.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [ERROR] No scripts found in '{scripts_dir}'. Exiting..\n")
            logfile.close()
        exit(1)
    #Check if all scripts are empty
    all_empty = True
    for filename in files:
        script_path = os.path.join(scripts_dir, filename)
        try:
            with open(script_path) as file:
                script = file.read()
            if script.strip():
                all_empty = False
                break
        except Exception as e:
            continue
    if all_empty:
        print(f"[WARNING] All scripts in '{scripts_dir}' are empty. Exiting..")
        if log and logfile:
            logfile.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [ERROR] All scripts in '{scripts_dir}' are empty. Exiting..\n")
            logfile.close()
        exit(1)
    #Iterates through the list of IPs
    for ip in ip_list:
        ip = ip.strip()
        for filename in files:
            script_path = os.path.join(scripts_dir, filename)
            try:
                with open(script_path) as file:
                    script = file.read()
                if not script.strip():
                    print(f"[WARNING] Script '{filename}' is empty. Skipping..")
                    if log and logfile:
                        logfile.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [ERROR] Script '{filename}' is empty. Skipping..\n")
                    continue
                remote_name = f"/tmp/mcmd_{filename}"
                if log and logfile:
                    logfile.write(f"{timestamp} === Executing {filename} on {ip} ===\n")
                if output:
                    print(f"=== Executing {filename} on {ip} ===")
                local_script_ssh_uploader(script, remote_name, username, password, ip, output=output, error=True, log=log, logfile=logfile)
            except Exception as e:
                print(f"[ERROR] Failed to process '{filename}': {e}")
                if log and logfile:
                    logfile.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [ERROR] Failed to process '{filename}': {e}\n")
    if log and logfile:
        logfile.close()

local_script_handler(username, password, log=True, output=True, error=True)
#!/bin/python3

import os
import paramiko
import getpass

username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")
remote_ip = input("Enter the remote IP address: ")

#Grabs the path to the scripts directory 
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

print(scripts_dir)

#Creates a list of all files in the scripts directory
files = [f for f in os.listdir(scripts_dir) if os.path.isfile(os.path.join(scripts_dir, f))]
print(files)

def local_script_ssh_uploader(script, remote_name, username, password, remote_ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=remote_ip, username=username, password=password)
        print(f"[INFO] Uploading script as {remote_name}...")
        # Upload script using 'cat'
        stdin, stdout, stderr = ssh.exec_command(f"cat > {remote_name}")
        stdin.write(script)
        stdin.channel.shutdown_write()
        upload_err = stderr.read().decode()
        if upload_err:
            #Write to log there is an error
            pass
        stdout.channel.recv_exit_status()
        # Make script executable and run it. I was having issues getting stdout from echos so I added 'get_pty=True' which simulates a real terminal and is able to capture echos.
        stdin, stdout, stderr = ssh.exec_command(f"sudo chmod +x {remote_name} && {remote_name}", get_pty=True)
        print(f"[INFO] Executing {remote_name} on remote host...")
        print("STDOUT:")
        # Read STDOUT in real time
        for line in iter(stdout.readline, ""):
            print(line, end="")  # already includes newline
        #Captures the exit status of the script execution (to check if it ran successfully)
        script_exit_status = stdout.channel.recv_exit_status()
        print("Exit Status:", script_exit_status)

        #Runs the rest of the commands to remove the script from the remote device. I chose to seperate these from the previous commands in order to capture the scripts exit status.
        stdin, stdout, stderr = ssh.exec_command(f"sleep 2 && sudo rm {remote_name}")

        # Read STDOUT in real time
        for line in iter(stdout.readline, ""):
            print(line, end="")  # already includes newline

        # Read STDERR
        err = stderr.read().decode()
        if err:
            print("STDERR:")
            print(err)

        # Wait for command to complete
        cleanup_exit_status = stdout.channel.recv_exit_status()
        print("Exit Status:", cleanup_exit_status)
        #If statement if vv flag is used
            #print("STDERR:", stderr.read().decode())
    except Exception as e:
        pass
        #if statement if vv flag is used
            #print(f"[ERROR] {e}")
    finally:
        ssh.close()

for filename in files:
    #Grab the full path to the file location
    script_path = os.path.join(scripts_dir, filename)
    with open(script_path) as file:
        script = file.read()
    remote_name = f"/tmp/mcmd_{filename}"
    local_script_ssh_uploader(script, remote_name, username, password, remote_ip)
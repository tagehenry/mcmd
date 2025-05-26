#!/bin/python3

import os
import paramiko

#Grabs the path to the scripts directory 
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

print(scripts_dir)

#Creates a list of all files in the scripts directory
files = [f for f in os.listdir(scripts_dir) if os.path.isfile(os.path.join(scripts_dir, f))]
print(files)

def local_script_ssh_uploader(script, remote_name):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect("remote_host", username="username", password="password")
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
        #Run script
        #if statement if args v or vv flags are used
            #print(f"[INFO] Executing {remote_name} on remote host...")
        stdin, stdout, stderr = ssh.exec_command(f"sudo chmod +x {remote_name} && {remote_name} && sleep 2 && sudo rm {remote_name}")
        #If statement if args v or vv flags are used
            #print("STDOUT:", stdout.read().decode())
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
    local_script_ssh_uploader(script, remote_name)
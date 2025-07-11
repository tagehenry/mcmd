# MCMD - Multi-Command Remote Executor
```
                                 __
   ____ ___  _________ ___  ____/ /
  / __ `__ \/ ___/ __ `__ \/ __  /
 / / / / / / /__/ / / / / / /_/ /
/_/ /_/ /_/\___/_/ /_/ /_/\__,_/
===================================
   Multi-Command Remote Executor   
===================================
```
MCMD is a Python script for running commands or scripts on multiple remote hosts via SSH. It is designed for flexibility, security, and ease of use, supporting both interactive and non-interactive password entry, logging, and robust argument parsing.

## Requirements

- Python 3.x
- paramiko

## Installation

```bash
pip install paramiko
```

## Features

- **Configurable via JSON**: All connection and command details are stored in `config.json` for easy editing and separation from code.
- **Threaded Execution**: Run commands or scripts on multiple hosts concurrently. The number of parallel SSH connections is controlled by the `threads` value in `config.json` for faster execution on large IP lists.
- **Secure Password Handling**: By default, the script prompts for the SSH password at runtime. Optionally, you can use the `--unsecure` flag to use the password from the config file (not recommended for production).
- **Argument Parsing with Error Handling**: Uses argparse to handle command-line arguments. If unsupported flags are used, the script displays a clear error message and help text.
- **Run Scripts or Commands**: Use the `--script` flag to run a script on remote hosts, or run a command as specified in the config.
- **Verbose and Error Output**: Use `--verbose` to display command output, and `-vv` to display both output and errors.
- **Logging**: Use `--log` to save all output and errors to `mcmd.log`.
- **IP List Management**: Reads target IPs from `iplist.txt`. Warns if the file is missing or empty.
- **Default Value Warnings**: Warns if you are using default values for script path or command, prompting you to update your config.

## Usage

```bash
python3 mcmd.py [OPTIONS]
```

### Options

- `--unsecure`, `-u`   : Use the password from `config.json` instead of prompting (not recommended for production)
- `--script`, `-s`     : Run the script specified in the config on remote hosts
- `--verbose`, `-v`    : Display command output in the console
- `-vv`                : Display both output and errors in the console
- `--log`, `-l`        : Log all output and errors to `mcmd.log`

If you use an unsupported flag, the script will display a message and show the help text.

## IP List Example

iplist.txt should contain one IP address per line, e.g.:
```
192.168.1.10
192.168.1.11
10.0.0.5
```

## Configuration

Copy `config_default.json` to `config.json` before first use:

```bash
cp config_default.json config.json
```

Edit `config.json` to set your connection and command details. Example:

```
{
    "username": "youruser",
    "password": "yourpassword",
    "port": 22,
    "showerrorsdefault": true,
    "script_path": "/path/to/your/script.sh",
    "command": "ls -l",
    "commanddescription": "List directory contents",
    "threads": 20
}
```


**Note:**
- The `threads` field controls how many SSH connections are made in parallel. Increase for faster execution, decrease if you experience connection issues or want to limit resource usage.
- The `password` field is only used when the `-u` or `--unsecure` flag is provided. For best security, do not store real passwords in `config.json` unless required for testing.

## Security Notes
- **Do not store real passwords in `config.json` unless using `--unsecure` for testing.**
- For best security, use SSH keys or enter passwords interactively.

## Example

```bash
python3 mcmd.py --script --verbose --log
```
Runs the script on all IPs in `iplist.txt`, prints output, and logs results.

## Troubleshooting
- If you see a message about default values, update your `config.json`.
- If you use an unsupported flag, you'll see a clear error and the help text.
- Make sure `iplist.txt` exists and contains one IP per line.

## Author
Tage Henry (tage199819@gmail.com)

## TO DO
- Add a feature/flag that allows a script saved locally to be executed on the remote device.
- In addition to the local script execution feature, add a dependency installer bash script that will run first for Python scripts with missing libraries on the remote device.
- Improve logging when -s or --script is used

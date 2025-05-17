# Mass Command

# mcmd.py

A Python script to run a shell command or script on multiple remote devices via SSH, using a list of IP addresses. Supports logging, verbose output, and error display customization.

## Features
- Run a custom shell command or script on a list of IPs (from `iplist.txt`)
- SSH authentication (username/password)
- Optional logging of all output to `output.log`
- Verbose and very verbose output modes
- Configurable error display
- Timestamped log entries

## Usage

1. **Prepare your IP list:**
   - Place all target IP addresses (one per line) in a file named `iplist.txt` in the same directory as the script.

2. **Set credentials and command:**
   - Edit the script to set the correct SSH `username`, `password`, and `port` if needed.
   - Set the `command` variable to the shell command you want to run.
   - Optionally, set `commanddescription` for log readability.

3. **Run the script:**
   ```bash
   python3 runcommandinmass.py [options]
   ```

### Options
- `-s`, `--script`   : Run a specified script on the remote device (set `script_path` in the script)
- `-v`, `--verbose`  : Print standard output from the command
- `-vv`              : Print both standard output and standard error
- `-l`, `--log`      : Log all output to `output.log`

### Example
```bash
python3 runcommandinmass.py -v -l
```
This will print standard output to the console and log all output to `output.log`.

## Configuration
- **defaultshowerrors**: Set to `True` or `False` in the script to control whether errors are shown by default.
- **script_path**: Set the absolute path to your script if using the `--script` flag.

## Log File
- All log entries are timestamped and grouped by command batch for easy parsing.

## Requirements
- Python 3
- `paramiko` library (install with `pip install paramiko`)


*Created for mass remote command execution and troubleshooting.*
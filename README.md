# ParaDecoder
## Requirements
### Python Version
- 3
### Libraries
- logging
- argparse
- pathlib
- subprocess
- time
- sys
## Dscription
ParaDecoder creates command lines by combining lists and executing the commands in parallel threads. The initial task was to test openssl decryption. Other taks/applications are possible. The Files have to contain one argument per line, e.g. ciphers or passwords. 
## Usage
$ python paradecoder.py [-h] [-b BRAKE] [-l LOGFILE] [-t THREADS] [-v] COMMAND
### COMMAND:
Command to execute, give replacement files in {}
### -h, --help
Show this help message and exit
### -b BRAKE, --brake BRAKE
Exit criteria:
- 0 = exit code is 0 (default, in Version 0.1 this is the only method)
### -l LOGFILE, --logfile LOGFILE
Set logfile
### -t THREADS, --threads THREADS
Number of threads (default: 1)              
### -v, --verbose
Set loglevel debug
## Example
```
$ python paradecoder.py -t 4 -v 'openssl {ciphers.txt} -d -pbkdf2 -in sample.enc -k {pw_list.txt}'
```
with files:
### ciphers.txt
```
aes-128-cbc
aes-128-ecb
aes-192-cbc
aes-192-ecb
aes-256-cbc
aes-256-ecb
```
### pw_list.txt
```
123456
verysafe
test
justwrong
```
### More Examples
```
$ python paradecoder.py -v -t 8 './matrixtest.sh {list_a.txt} {list_b.txt} {list_c.txt}'
$ python paradecoder.py -v './dummy.sh {nopw_list.txt}'
```
## Project Page
https://github.com/markusthilo/ParaDecoder

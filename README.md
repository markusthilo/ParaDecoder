# ParaDecoder

## Requirements

### Version
Python 3
### Libraries
logging
argparse
pathlib
subprocess
time
sys

## Dscription
ParaDecoder creates command lines by combining lists and executing the commands in parallel threads. The initial task was to test openssl decryption. Other taks/applications are possible. The Files have to contain one argument per line, e.g. ciphers or passwords. 

## Usage

$ python paradecoder.py [-h] [-b STRING] [-l FILE] [-t INTEGER] [-v] STRING

positional arguments:
  STRING                Command to execute, give replacement files in {}

options:
  -h, --help            show this help message and exit
  -b STRING, --brake STRING
                        Exit on: 0 = exit code is 0 (default, v0.1: the only method)
  -l FILE, --logfile FILE
                        Set logfile
  -t INTEGER, --threads INTEGER
                        Number of threads (default: 1)
  -v, --verbose         Set loglevel debug

## Example
$ python paradecoder.py -t 4 -v 'openssl {ciphers.txt} -d -pbkdf2 -in sample.enc -k {pw_list.txt}'

with files:
### ciphers.txt
es-128-cbc
aes-128-ecb
aes-192-cbc
aes-192-ecb
aes-256-cbc
aes-256-ecb

### pw_list.txt
123456
verysafe
test
justwrong

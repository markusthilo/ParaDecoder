#!/bin/bash
echo "Process $1 x $2 x $3: sleeping for 3 seconds..."
sleep 3
echo "End of Bash Script, returning exit code 1"
echo "This is send to STDERR" >&2
exit 1

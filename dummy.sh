#!/bin/bash
if [ "$1" = 'test' ]
then
    echo "Matching password: $1"
    exit 0
fi
echo "Wrong password: $1" >&2
exit 1

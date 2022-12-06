#!/bin/bash
if [ "$1" = 'test' ]
then
    echo MATCH!
    exit 0
fi
exit 1

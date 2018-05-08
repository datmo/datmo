#!/bin/bash -e

exit_success () {
    echo "Passed Formatting Test"
    exit 0
}

yapf -d -r datmo > diff.txt

if [ -s diff.txt ]
then
    cat diff.txt
    echo ""
    echo "Failing Formatting Test"
    echo "Please run yapf over the datmo module"
    echo "pip install yapf==0.20.0"
    echo "yapf -i -r datmo"
    exit 1
fi

yapf -d setup.py > diff.txt

if [ -s diff.txt ]
then
    cat diff.txt
    echo ""
    echo "Failing Formatting Test"
    echo "Please run yapf over the setup.py file"
    echo "pip install yapf==0.20.0"
    echo "yapf -i setup.py"
    exit 1
else
    exit_success
fi
exit 1
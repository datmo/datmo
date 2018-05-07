#!/usr/bin/env bash

# This script will create a datmo-enabled repository in the current directory
# run the initial script to create a snapshot and will list out the snapshots
# by calling the `datmo snapshot ls` command

# Create a datmo-enabled repo
datmo init --name="iris data with sklearn models" --description="use iris data along with sklearn models"

# Run the script to create a snapshot
python snapshot_create_iris_sklearn.py

# Run the datmo command to list all snapshots
datmo snapshot ls
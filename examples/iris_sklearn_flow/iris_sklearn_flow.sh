#!/usr/bin/env bash

# This script will make the iris_sklean_flow directory into a datmo-enabled one `iris_sklearn`
# run the initial script to create a snapshot and will list out the snapshots
# by calling the `datmo snapshot ls` command

# Create a datmo-enabled repo
datmo init --name="iris data flow with sklearn models" --description="use iris data along with sklearn models to run tasks to compare models and create snapshots"

# Run the script to create a snapshot
python task_compare.py

# Run the datmo command to list all snapshots
datmo snapshot ls
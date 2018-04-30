#!/usr/bin/env bash

# This script will create a datmo-enabled repository called `iris_sklearn`
# run the initial script to create a snapshot and will list out the snapshots
# by calling the `datmo snapshot ls` command

# Create directory for the datmo-enabled repo to live
mkdir iris_sklearn

cd iris_sklearn

# Create a datmo-enabled repo
datmo init --name="iris data with sklearn models" --description="use iris data along with sklearn models"

# Copy the relevant scripts into the repo
cp ../iris_sklearn.py .
cp ../iris_sklearn.ipynb .

# Run the script to create a snapshot
python iris_sklearn.py

# Run the datmo command to list all snapshots
datmo snapshot ls


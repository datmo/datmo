#!/usr/bin/env bash

# This script will show the multiple different ways to setup your environment using Datmo

## SCENARIO A: Starting from an uninitialized Datmo Project
# Step 1: Initialize the datmo repository with
$ datmo init
# Step 2: Answer the following prompts for project name and description
# Step 3: When asked if you want to set up an environment, say yes
# Step 4: Type the number corresponding to the environment you want to use from the list


## SCENARIO B: Adding an environment to an existing Datmo Project
# Step 1: begin environment setup with
$ datmo environment setup
# Step 2: Type the number corresponding to the environment you want to use from the list


## SCENARIO C: Adding your own environment to be logged in your Datmo Project
# Step 1: begin environment setup with
$ datmo environment setup
# Step 2: Choose the option corresponding to bringing your own environment
# Step 3: Type the directory containing your environment files in the prompt (Dockerfile, requirements.txt, etc)
#!/usr/bin/env bash

# This script demonstrates how to rerun a task you've run previously within this project.

# Step 0: Have a previously run task with:
$ datmo run <your-cmd-here>
# or
$ datmo <workspace> # ex: notebook, rstudio, etc

# Step 1: Find the previous run ID from the run table:
$ datmo run ls

# Step 2: Re-run using the following command:
$ datmo rerun <run-id>


# NOTE:
# For workspace tasks:
# This will re-initialize a workspace at the resulting state of the workspace from last run.
#
# For command/script tasks:
# This will execute the same task on the initial state from the referenced run.
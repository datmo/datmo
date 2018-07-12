# CLI Flow Examples

In order to run the examples, make sure that you have datmo properly installed with the latest 
stable or development version. You can install it with the following command:
```
$ pip install datmo
```

## Using the Examples
### CLI
1. Navigate to desired project folder or create a new one 

        $ mkdir MY_DATMO_PROJECT
        $ cd MY_DATMO_PROJECT

2. Copy/save example files within project folder

        $ cp /path/to/SCRIPT_NAME.sh .
        $ cp /path/to/SCRIPT_NAME.py .

3. Follow the instructions for a given example in the table below

### Examples

| feature  | filename(s) | Instructions |
| ------------- |:-------------:| :-----|
| Create Snapshot | `snapshot_create_iris_sklearn.py`, <br> `snapshot_create_iris_sklearn.sh` | (1) Read `snapshot_create_iris_sklearn.py` <br> (2) Run the command `bash snapshot_create_iris_sklearn.sh` or run all of the commands one-by-one |
| Create Environment | `environment_setup.sh` | (1) Read `environment_setup.sh` <br> (2) Follow one of the scenarios listed in the file |
| Start a Workspace | `workspace_setup.sh` | (1) Read `workspace_setup.sh` <br> (2) For Jupyter notebook: `$ datmo notebook` or <br> RStudio: `$ datmo rstudio` |
| Re-run a Task | `task-rerun.sh` | (1) Read `task-rerun.sh` <br> (2) `$ datmo rerun <run-id>` |
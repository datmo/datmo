# Python script examples

In order to run the examples, make sure that you have datmo properly installed with the latest 
stable or development version. You can install it with the following command:
```
$ pip install datmo
```

## Using the Examples
### Python
1. Navigate to desired project folder or create a new one 

        $ mkdir MY_DATMO_PROJECT
        $ cd MY_DATMO_PROJECT
        
2. Initialize the datmo project

        $ datmo init

3. Copy/save example files within project folder (if directory, copy the contents of the directory)

        $ cp /path/to/SCRIPT_NAME.py .
        $ cp /path/to/DIRECTORY/* .
        
4. Run 

        $ python SCRIPT_NAME.py


### Examples

| feature  | filename(s) | Instructions |
| ------------- |:-------------:| -----|
| Create Snapshot | `snapshot_create_iris_sklearn.py`| (1) blah blah blah blah (2) blah blah blah blah |
| Run standard task | `/task_run_iris_sklearn/`: `basic_task.py`,`train_model_1.py`| (1) blah blah blah blah (2) blah blah blah blah |
| Run containerized tasks | `/task_run_iris_sklearn/:` `task_compare.py`, `train_model_1.py`, `train_model_2.py1` | (1) blah blah blah blah (2) blah blah blah blah |
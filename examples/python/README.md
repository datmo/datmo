# CLI + Python Flow Examples

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
        
   If the filename for the example is a directory then you can run the following
   
        $ cp /path/to/DIRECTORY/* .
        
4. Follow the instructions for a given example in the table below


### Examples

| feature  | filename(s) | Instructions |
| ------------- |:-------------:| -----|
| Create Snapshot | `snapshot_create_iris_sklearn.py`| (1) Run `$ python snapshot_create_iris_sklearn.py` <br> (2) See snapshots created with `$ datmo snapshot ls` |


<!-- Task run currently deprecated. Commenting out until they are eventually replaced with `run` and `rerun`.
| Run a single task | `/task_run_iris_sklearn_basic/`: `basic_task.py`,`train_model_1.py`| (1) Read `'train_model_1.py` <br> (2) Run `$ python basic_task.py` <br> (3) See task results with `$ datmo task ls`|
| Run multiple tasks and compare | `/task_run_iris_sklearn_compare/:` `task_compare.py`, `train_model_1.py`, `train_model_2.py` | (1) Read `train_model_1.py` and `train_model_2.py` <br> (2) Run `$ python task_compare.py` <br> (3) See task results with `$ datmo task ls` <br> (4) See snapshots created with `$ datmo snapshot ls`|
-->
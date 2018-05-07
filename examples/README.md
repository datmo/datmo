# Examples

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

3. Open the `SCRIPT_NAME.sh` file in a text editor and run the commands individually, or run

        $ bash SCRIPT_NAME.sh

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

### Jupyter Notebook
1. Navigate to desired project folder or create a new one 

        $ mkdir MY_DATMO_PROJECT
        $ cd MY_DATMO_PROJECT
        
2. Initialize the datmo project

        $ datmo init

3. Copy/save example files within project folder (if directory, copy the contents of the directory)

        $ cp /path/to/SCRIPT_NAME.ipynb .
        $ cp /path/to/DIRECTORY/* .
        
4. Run 

        $ jupyter notebook SCRIPT_NAME.ipynb

5. Run cells in order


## Examples
#### Creating a Snapshot
* CLI
	* TBD
* Python
	* [Snapshot create with sklearn iris classifier](https://github.com/datmo/datmo/blob/master/examples/python/snapshot_create_iris_sklearn.py)
* Jupyter notebook
	* [Snapshot create with sklearn iris classifier directory](https://github.com/datmo/datmo/blob/master/examples/jupyter_notebook/snapshot_create_iris_sklearn/)
	    * [Snapshot create with sklearn iris classifier notebook](https://github.com/datmo/datmo/blob/master/examples/jupyter_notebook/snapshot_create_iris_sklearn/snapshot_create_iris_sklearn.ipynb)

#### Running a containerized task (with option to create Snapshot)
* CLI
	* Run a training script (any language) (Coming soon)
	* Run an inference script (any language) (Coming soon)
* Python
    * [Task run example with sklearn iris classifier directory](https://github.com/datmo/datmo/blob/master/examples/python/task_run_iris_sklearn)
	    * [Train a basic sklearn iris classifier](https://github.com/datmo/datmo/blob/master/examples/python/task_run_iris_sklearn/basic_task.py)
	    * [Run multiple tasks and snapshot the best result](https://github.com/datmo/datmo/blob/master/examples/python/task_run_iris_sklearn/task_compare.py)
    * Perform inference on saved model (iris sklearn) (Coming soon)
* Jupyter notebook
    * TBD


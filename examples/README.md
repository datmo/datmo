# Examples

In order to run the examples, make sure that you have datmo properly installed with the latest 
stable or development version.

## Using the Examples
### CLI
1. `$ pip install datmo` or `$ git clone https://github.com/datmo/datmo`
2. Navigate to desired project folder
3. Copy/save example files within project folder
4. Open the `SCRIPT_NAME.sh` file in a text editor and run the commands individually, or run `$ bash SCRIPT_NAME.sh`

### Python
1. `$ pip install datmo`
2. Navigate to desired project folder
3. `$ datmo init`
4. Copy/save example files within project folder
5. Run `python SCRIPT_NAME.py`

### Jupyter Notebook
1. `$ pip install datmo`
2. Navigate to desired project folder
3. `$ datmo init`
4. Copy/save files within project folder
5. Run `jupyter notebook`, navigate to `.ipynb` file
6. Run cells in order


## Examples
#### Creating a Snapshot
* CLI
	* TBD
* Python
	* [sklearn iris classifier](/examples/python/snapshot_create_iris_sklearn.py)
* Jupyter notebook
	* [sklearn iris classifier](/examples/jupyter_notebook/snapshot_create_iris_sklearn.ipynb)

#### Running a containerized task (with option to create Snapshot)
* CLI
	* Run a training script (any language) (Coming soon)
	* Run an inference script (any language) (Coming soon)
* Python
	* [Train a basic sklearn iris classifier](/examples/python/task_run_iris_sklearn/basic_task.py)
	* [Run multiple tasks and snapshot the best result](/examples/python/task_run_iris_sklearn/basic_task.py)
    * Perform inference on saved model (iris sklearn) (Coming soon)
* Jupyter notebook
    * TBD


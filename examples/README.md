# Examples

In order to run the examples, make sure that you have datmo properly installed with the latest 
stable or development version. You can install it with the following command:

```
$ pip install datmo
```

## Using the Examples
### CLI (Standalone)
The datmo CLI can work entirely as a standalone tool. It can also be used in conjunction with our language-specific SDKs to enhance the experience of the user and enable more granular control over model management during runtime.

See [CLI flow examples](/examples/cli) for instructions.

### Python
We offer a fully supported Python SDK, that works in conjunction with the CLI.

See [CLI + Python flow examples](/examples/python) for instructions

### Jupyter Notebook (IPython)
For Python kernels, the Python SDK is compatible with Jupyter notebooks. 
For running a containerized notebook environment, the user can do this with the CLI.

See [CLI + Jupyter Notebook flow examples](/examples/jupyter_notebook) for instructions

### R (beta)
Users can call the CLI natively using the `system2()` command in R, allowing for granular control over snapshot creation.
In the future, these system calls will be replaced with a more intuitive SDK.

See [R flow examples](/examples/R) for instructions

## Examples
Listed below are actions you might want to take with Datmo. For each
we have listed if there are any example for each type of flow. You can 
navigate to the specific flow folder to find the exact instructions for
each example. 

#### Creating a Snapshot 
* [CLI flow](/examples/cli/)
    * snapshot_create_iris_sklearn
* [CLI + Python flow](/examples/python)
    * snapshot_create_iris_sklearn
* [CLI + Jupyter Notebook flow](/examples/jupyter_notebook)
    * snapshot_create_iris_sklearn
* [CLI + R flow](/examples/R)
    * snapshot_create_iris_caret

#### Running a containerized task
* [CLI + Python flow](/examples/python)
    * task_run_iris_sklearn_basic
    * task_run_iris_sklearn_compare

#### Re-run a previous task
Rerun a single task (command/script or workspace) [CLI](/examples/cli/)
    * task_rerun

#### Environment setup
* Setting up a project environment [(CLI)](/examples/cli/environment_setup.sh)
    * From fresh repository
    * From existing datmo project
    * Bringing your own
* Initializing a workspace [(CLI)](/examples/cli/workspace_setup.sh)
    * opening a Jupyter notebook
    * open RStudio
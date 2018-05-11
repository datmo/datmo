import datmo
"""
WHAT IT DOES: 
	Instantiates new task objects, and runs tasks inside of local container.
	As this is run within a datmo project with python dependencies, the
	environment will automatically be generated from the file dependencies.

INSTRUCTIONS
	1. Instantiate your current folder as a Datmo project with:
	$ datmo init --name="Iris sklearn model comparison" --description="create sklearn models for iris data using tasks, and compare their results with snapshots"
    
	2. Run this script to create a snapshot
	$ python task_compare.py

	3. Run this datmo command to list all snapshots in this Datmo project:
	$ datmo snapshot ls
"""

task_1 = datmo.task.run(command="python train_model_1.py")
task_2 = datmo.task.run(command="python train_model_2.py")

# create a single snapshot from the task id directly, depending on which model was more accurate
if task_1.results['test accuracy'] > task_2.results['test accuracy']:
    print("found test accuracy of model 1 to be best")
    print("creating a snapshot with model 1")
    snapshot = datmo.snapshot.create(
        message="my great snapshot", task_id=task_1.id)
else:
    print("found test accuracy of model 2 to be best")
    print("creating a snapshot with model 2")
    snapshot = datmo.snapshot.create(
        message="my great snapshot", task_id=task_2.id)

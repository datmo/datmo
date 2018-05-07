import datmo

"""
WHAT IT DOES: 
    Instantiates a new task object, and runs the task inside of local container.
    As this is run within a datmo project with python dependencies, the
    environment will automatically be generated from the file dependencies.

INSTRUCTIONS
    1. Instantiate your current folder as a Datmo project with:
    $ datmo init --name="basic iris model" --description="run an iris sklearn training script as a task"

    2. Run this script to create a snapshot
    $ python task_compare.py

    3. Run this datmo command to view the snapshot:
    $ datmo snapshot ls
"""

task = datmo.task.run(command="python train_model_1.py")

print(task.files())
print(task.results)

# create a snapshot from the task id directly
snapshot = datmo.snapshot.create_from_task(message="my great snapshot", task_id=task.id)

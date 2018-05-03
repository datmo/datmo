import datmo

# instantiate a new task object, and run task inside of local container
# as this is run within a datmo project with python dependencies, the
# environment will automatically be generated from the file dependencies
task = datmo.task.run(command="python train_model_1.py")

print(task.files())
print(task.results)

# create a snapshot from the task id directly, create from task that is best
snapshot = datmo.snapshot.create_from_task(
    message="my great snapshot", task_id=task.id)

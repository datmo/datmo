import datmo

# instantiate a new task object, and run task inside of local container
# as this is run within a datmo project with python dependencies, the
# environment will automatically be generated from the file dependencies
task_1 = datmo.task.run(command="python train_model_1.py")

task_2 = datmo.task.run(command="python train_model_2.py")

# create a snapshot from the task id directly, create from the best task
if task_1.results['test accuracy'] > task_2.results['test accuracy']:
    print("creating a snapshot with model 1")
    snapshot = datmo.snapshot.create_from_task(message="my great snapshot",
                                               task_id=task_1.id)
else:
    print("creating a snapshot with model 2")
    snapshot = datmo.snapshot.create_from_task(message="my great snapshot",
                                               task_id=task_2.id)



# Examples

In order to run the examples, make sure that you have datmo properly installed with the latest 
stable or development version.

## Bash Scripts

Bash scripts are meant to show you an entire flow for creating a datmo project, running a particular command
and seeing the output. These scripts result in new repositories that will contain the project in question. 
You can run them with the following command -- example given is for the iris sklearn example

```
$ bash iris-sklearn.sh
```

Once the scripts are finished they will have created a project folder which you can navigate to and 
run datmo commands in to see how it works. 

## Python Scripts

Datmo python scripts that `import datmo` must be run within a Datmo-enabled repository. Enabling datmo is as simple as
running a `datmo init` within an existing directory. The directory can already have your model code or can 
be completely empty. 

Python scripts that do not include `import datmo` are meant to be like any other script you are already running. 
They can be run completely separately and do not need to run within a datmo-enabled repository, but they can be 
called and referenced in scripts that run datmo tasks. 

In order to run any of the scripts present in this `examples/` directory, you can do the following: 
1) copy over the script to an empty repo or an existing repo
2) run the following within the destination directory `datmo init` to ensure it is a datmo-enabled repo
3) run the script: `python SCRIPT.py` or if it is a Jupyter Notebook `jupyter notebook` and run the cells

For any of the directories present within the `examples/` directory, they require more than just the script. 
In this case you can do the following:
1) copy the entire directory to an empty repo or an existing repo
2) run the following within the destination directory `datmo init` to ensure it is a datmo-enabled repo
3) navigate to within the directory in the repo 
4) run the script: `python SCRIPT.py` or if it is a Jupyter Notebook `jupyter notebook` and run the cells

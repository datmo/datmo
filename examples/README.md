# Examples

Datmo scripts that `import datmo` must be run within a Datmo-enabled repository. Enabling datmo is as simple as
running a `datmo init` within an existing directory. The directory can already have your model code or can 
be completely empty. 

Scripts that do not include `import datmo` are meant to be like any other script you are already running. 
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

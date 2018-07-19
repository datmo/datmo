# CLI + R examples

In order to run the examples, make sure that you have datmo properly installed with the latest 
stable or development version. You can install it with the following command:
```
$ pip install datmo
```
*Note: Datmo installation is currently only officially supported through pip, Python's package manager. If you don't already have it installed, [you can find it here.](https://pip.pypa.io/en/stable/installing/)*

## Using the Examples
### R
1. Navigate to desired project folder or create a new one 

        $ mkdir MY_DATMO_PROJECT
        $ cd MY_DATMO_PROJECT
        
2. Initialize the datmo project (skip this step if using an example with .Rmd)

        $ datmo init

3. Copy/save example files within project folder (if directory, copy the contents of the directory)

        $ cp /path/to/SCRIPT_NAME.R .
        
   If it is an Rmd notebook, you can run the following
   
        $ cp /path/to/NOTEBOOK_NAME.Rmd .
        
   If the filename for the example is a directory then you can run the following
   
        $ cp /path/to/DIRECTORY/* .
        
4. Open RStudio from the terminal (allows $PATH to find Datmo in MacOS)

        $ open -a RStudio
    
5. Change your current working directory within RStudio to the root directory of your project. 

This can be done either through the GUI, or with the following R Console command.

        `> setwd("~/path/of/projectfolder")`

NOTE: You may find that some of the libraries requested in the script are not present, you can use 
the RStudio GUI to install those packages if you run into any errors running the lines of code
in the example.   

### Examples

| feature  | filename(s) | Instructions |
| ------------- |:-------------:| -----|
| Create Snapshot | `snapshot_create_iris_caret.R`| (1) Open and run `snapshot_create_iris_caret.R` in RStudio <br> (2) See snapshot created with `$ datmo snapshot ls` |
| Create Snapshot Notebook | `snapshot_create_notebook.Rmd`| (1) Open and run `snapshot_create_notebook.Rmd` in RStudio <br> (2) See snapshot created with `$ datmo snapshot ls` |
| Open a new RStudio workspace | N/A | (1) `$ datmo environment setup`, choose an image that contains RStudio <br> (2) Run `$ datmo rstudio` |
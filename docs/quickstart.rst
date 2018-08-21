Quickstart
===================================

Hello World
-----------------

Setup:

    - docker (installed and running before starting) 
        Instructions for `Ubuntu <https://docs.docker.com/install/linux/docker-ce/ubuntu/#uninstall-old-versions>`_, `MacOS <https://docs.docker.com/docker-for-mac/install/#install-and-run-docker-for-mac>`_, `Windows <https://docs.docker.com/docker-for-windows/install/>`_

    - datmo 
        install with ``$ pip install datmo``


Steps:

1. Clone this github `project <https://github.com/datmo/hello-world.git>`_.

``$ git clone https://github.com/datmo/hello-world.git``

2. Move into the project, initialize it, and setup the environment using the datmo CLI,
::
   $ cd hello-world
   $ # Initialize the project using datmo
   $ datmo init
   $ # Set the name and description for the project
   $ # Enter `y` to setup the environment
   $ # Select `cpu`, `data-analytics`, `py27` based on the questions being asked   

3. Now, run and view your first experiment using the following commands,
::
   $ datmo run 'python script.py'
   $ # check for your first run using ls command
   $ datmo ls

4. Now let's change the environment and script for a new run,
   
To edit the environment,

``$ vi datmo_environment/Dockerfile``

Add the following line into this `Dockerfile`
::
   RUN pip install catboost

To edit the script,

``$ vi script.py``

Uncomment the following lines in the script,
::
   # import catboost
   # print catboost.__version__


5. Now that we have updated the environment and script, let's run another experiment,
::
   $ datmo run 'python script.py'
   $ # check for your first run using ls command
   $ datmo ls

6. With two test being tracked, we can now rerun any of the previous run with reprocibility,
::
   $ # Select the earlier run-id to rerun the first experiment
   $ datmo rerun < run-id >

Now, in this hello-world example, you have run two experiments, both which are tracked, and have 
rerun one of these tracked experiments.


--------

Spinning up a TensorFlow Jupyter Notebook
--------------------------------------------

0. Install Docker on your system

Find the proper version for your operating system and install Docker from `this page <https://docs.docker.com/install/#supported-platforms>`_. Check that Docker is installed and running before moving forward.

1. Install datmo using pip:

``$ pip install datmo``

2. Navigate to a new folder for your project and run:

``$ datmo init``

3. Create a name and description. When prompted to setup an environment, respond with the following answers:
    - Would you like to set up an environment? : ``y``
    - Please select one of the above enviornment type (e.g. 1 or gpu): ``cpu``
    - Please select one of the above environments (e.g. 1 or data-analytics): ``keras-tensorflow``
    - Please select one of the above environment language (e.g. py27): ``py27``

4. Open a jupyter notebook automatically with:

``$ datmo notebook``

Congrats, you now have a functional jupyter notebook with TensorFlow! 


--------

Testing it out:

1. Navigate to the notebook by typing the following into your browser:

``localhost:8888/?token=UNIQUE_TOKEN_FROM_TERMINAL``

2. Click 

``New --> Notebook: Python2``

3. In the first cell, paste in and run:

.. code::
    
    import tensorflow as tf

4. In the second cell paste and run:

.. code:: python
    
    # Define a constant
    hello = tf.constant('Hello, TensorFlow!')

    # Start tf session
    sess = tf.Session()

    # Run the op
    print(sess.run(hello))


If your output is ``Hello, TensorFlow!``, you're good to go! 
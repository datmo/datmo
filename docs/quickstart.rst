Quickstart
===================================

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

Testing it out
------------------------

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
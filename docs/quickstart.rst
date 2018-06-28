Quickstart
===================================

Spinning up a TensorFlow Jupyter Notebook
--------------------------------------------

1. Install datmo using pip:

``$ pip install datmo``

2. Navigate to a new folder for your project and run:

``$ datmo init``

3. Create a name and description. When prompted for a desired environment, type:

``tensorflow:cpu``

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
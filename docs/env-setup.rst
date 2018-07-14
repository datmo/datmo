Setting Up Your Environment
===================================

In Datmo, there are three ways to setup an environment:

1. :ref:`using-default`
2. :ref:`adding-to-default`
3. :ref:`bring-your-own`

-----

.. _using-default:

Using a Default Environment
--------------------------------

Default Datmo environments are maintained by the Datmo team and are guaranteed to work out of the box. We've provided many of the most popular environments for data science and AI, including:

- kaggle
- keras/tensorflow
- mxnet 
- pytorch 
- caffe2
- base R and Python

You can setup a Datmo default environment either by saying yes when prompted at time of project initialization with ``$ datmo init``,
or at any point in time by selecting a provided environment from ``$ datmo environment setup``.

.. _adding-to-default:

Adding to a Default Environment
------------------------------------

There are instances where you may want to add additional components to your environment. A common example would be installing additional language-level packages that weren't included in the default environment.

1. To do this, first setup your default environment in one of two ways:
    - If you haven't yet initialized a project, use ``$ datmo init``
    - Otherwise, use ``$ datmo environment setup``

2. Once you've followed the prompts and selected the default environment to setup, you can find the environment file at:
    ``PROJECT-DIR/datmo_environment/Dockerfile``

3. **Open the Dockerfile in a text/code editor**

4. **Add the respective environment setup commands inside the Dockerfile:**
   
     .. note::
        
        Docker has specific rules for writing command line arguments in Dockerfiles. For more details, see the RUN section of the official `Docker documentation <https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#run>`_. 

     For example, to add pandas using the pip package manager, you would add the following line to the Dockerfile:
     ``RUN pip install pandas``


     If you have a list of python packages you'd like to install, like a `requirements.txt` file, you can do that by appending the following to the end of your Dockerfile:
     ``RUN pip install -r requirements.txt``

.. _bring-your-own:

Bringing your own environment
---------------------------------
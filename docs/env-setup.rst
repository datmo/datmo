Setting Up Your Environment
===================================

In Datmo, there are three ways to setup an environment:

1. :ref:`using-default`
2. :ref:`adding-to-default`
3. :ref:`bring-your-own`

-----

.. _using-default:

Using a Default Environment
------------------------------

Default Datmo environments are maintained by the Datmo team and are guaranteed to work out of the box. We've provided many of the most popular environments for data science and AI, including:

- data-analytics (general data science/computational programming)
- kaggle
- keras/tensorflow
- mxnet 
- pytorch 
- caffe2
- base R and Python

You can setup a Datmo default environment either by saying yes when prompted at time of project initialization with ``$ datmo init``,
or at any point in time by selecting a provided environment from ``$ datmo environment setup``.

-----

.. _adding-to-default:

Adding to a Default Environment
----------------------------------

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

     **Adding individual packages/libraries** 

     to add pandas using the pip package manager, you would add the following line to the Dockerfile:
     ``RUN pip install pandas``


     **Adding packages froma build/package list**

     If you have a list of python packages you'd like to install, like a `requirements.txt` file, you can do so by appending the following to the end of your Dockerfile:

     .. code-block:: none
         
         COPY requirements.txt /tmp/requirements.txt
         RUN pip install -r /tmp/requirements.txt

-----

.. _bring-your-own:

Bringing Your Own Environment
---------------------------------

There are two ways to write your own enviornment: with or without a Datmo base image.

Datmo base images aim to efficiently serve as a foundation for environments, including an operating system, necessary system level drivers, as well as a programming language, package, and workspaces. Datmo base images are tested and reliable, but the user has the option to bring their own as well if they would prefer.

**A) With a datmo base image:**

We have created public base images for all permutations of the following:
    - Languages: Python 2.7, Python 3.5, R
    - System Drivers: CPU, GPU (nvidia)


The datmo team maintains these images and ensures they will serve as a stable base for building environments on top of. To use one of them, you'll need to call one of them using ``FROM`` at the top of the Dockerfile.

**1. Open a blank text file, and save it with the name** ``Dockerfile`` **in the** ``/datmo_environment`` **directory**

**2. Designate a base image**

At the top of your Dockerfile, you will need a line of the following format:

    ``FROM datmo/python-base:z``

    .. note::
        
        The tag ``z`` is dependent on the language and system permutation (``py27``, ``py35``, ``r`` and ``cpu``, ``gpu``)


    Examples of valid dockerfile names would be as follows (list is not exhaustive):
        i. datmo/python-base:py35-cpu
        ii. datmo/python-base:py35-gpu
        iii. datmo/python-base:py27-cpu
        iv. datmo/python-base:py27-gpu

    To see the full list of officially supported Python environment versions, check out the `Dockerhub page here <https://hub.docker.com/r/datmo/python-base/tags/>`_.

**3. Designate installation of system level packages**

All base datmo environments utilize Ubuntu, so the ``apt-get`` package tool will be used to install any necessary system dependencies. 

In your Dockerfile, enumerate all system level packages with the following:

    ``RUN apt-get install <package-name>``

    .. note ::
        
        For installing multiple system packages consecutively, read more about Docker's suggested syntax `here <https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#run>`_.


**4. Designate installation of language level packages**

Most languages leverage some sort of package management tool. For example, Python utilizes pip, and is included in all python base datmo images.

To utilize your package manager to install packages through the Dockerfile, use the following line:

    ``RUN pip install <python-package-name>``

    .. note ::
        
        For installing multiple language-level packages, follow the same guidelines listed above in the step 3 note.

-----

**B) Without a datmo base image:**
 
**1. Open a blank text file, and save it with the name** ``Dockerfile`` **in the** ``/datmo_environment`` **directory**

**2. Designate a base image**

At the top of your Dockerfile, you will need a line of the following format:

    ``FROM x/y:z``

    Where each variable represents the following Dockerhub information:
        - x: user/organization account name
        - y: Dockerfile name
        - z: Dockerfile version

    An example would be the following: 
        ``FROM kaggle/python:latest``

**3. Designate installation of system level packages**

Based on which operating system the base image utilizes, you will likely have a different package manager for installing system level utilities. Examples include ``apt-get`` for Ubuntu, ``yum`` for CentOS/Fedora, or ``apk`` on Alpine, and more.

In your Dockerfile, enumerate all system level package installations using your respective package manager with the following:

    ``RUN apt-get install <package-name>``

    .. note ::
        
        For installing multiple system packages consecutively, read more about Docker's suggested syntax `here <https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#run>`_.


**4. Designate installation of language level packages**

Most languages leverage some sort of package management tool. For example, Python utilizes pip, which may need to be installed as a system level resource first.

To utilize your language-level package manager to install packages through the Dockerfile, use the following line:

    ``RUN pip install <python-package-name>``

    .. note ::
        
        For installing multiple language-level packages, follow the same guidelines listed above in the step 3 note.


**5. Getting datmo workspaces to work with your custom environment**

By running a fully custom environment image, you will need to add code snippets to your Dockerfile in order for some of datmo's aliases to work. Please make sure you have installed ``pip`` and ``apt-get`` during step 3.

**Jupyter Notebook** via ``$ datmo notebook``
    
    i. Add the following code snippet to your Dockerfile

    .. code-block:: none

     # Jupyter
     RUN pip --no-cache-dir install \
             ipykernel \
             jupyter \
             && \
         python -m ipykernel.kernelspec
     
     # Set up our notebook config.
     COPY jupyter_notebook_config_py2.py /root/.jupyter/
     RUN mv /root/.jupyter/jupyter_notebook_config_py2.py /root/.jupyter/jupyter_notebook_config.py
     
     # Jupyter has issues with being run directly:
     #   https://github.com/ipython/ipython/issues/7062
     # We just add a little wrapper script.
     
     COPY run_jupyter.sh /
     RUN chmod +x /run_jupyter.sh
     
     # IPython
     EXPOSE 8888


    ii. Download the 3 patchfiles from `here <https://github.com/datmo/docker-files/tree/master/workspace-patches>`_ and move them into your ``datmo_environment`` folder along with your Dockerfile.

**JupyterLab** via ``$ datmo jupyterlab``
    
    i. Add the following code snippet to your Dockerfile

    .. code-block:: none

      # Jupyter
         RUN pip --no-cache-dir install \
                 ipykernel \
                 jupyter \
                 && \
             python -m ipykernel.kernelspec
         
         # Set up our notebook config.
         COPY jupyter_notebook_config_py2.py /root/.jupyter/
         RUN mv /root/.jupyter/jupyter_notebook_config_py2.py /root/.jupyter/jupyter_notebook_config.py
         
         # Jupyter has issues with being run directly:
         #   https://github.com/ipython/ipython/issues/7062
         # We just add a little wrapper script.
         
         COPY run_jupyter.sh /
         RUN chmod +x /run_jupyter.sh
         
         # Jupyter lab
         RUN pip install jupyterlab==0.32.1
         
         # IPython
         EXPOSE 8888



    ii. Download the 3 patchfiles from `here <https://github.com/datmo/docker-files/tree/master/workspace-patches>`_ and move them into your ``datmo_environment`` folder along with your Dockerfile.

**RStudio** via ``$ datmo rstudio``
    
    i. Add the following code snippet to your Dockerfile

    .. code-block:: none

         # Rstudio
         ENV DEBIAN_FRONTEND noninteractive
         ENV CRAN_URL https://cloud.r-project.org/
         
         RUN set -e \
               && ln -sf /bin/bash /bin/sh
         
         RUN set -e \
               && apt-get -y update \
               && apt-get -y dist-upgrade \
               && apt-get -y install apt-transport-https gdebi-core libapparmor1 libcurl4-openssl-dev \
                                     libssl-dev libxml2-dev pandoc r-base \
               && apt-get -y autoremove \
               && apt-get clean
         
         RUN set -e \
               && R -e "\
               update.packages(ask = FALSE, repos = '${CRAN_URL}'); \
               pkgs <- c('dbplyr', 'devtools', 'docopt', 'doParallel', 'foreach', 'gridExtra', 'rmarkdown', 'tidyverse'); \
               install.packages(pkgs = pkgs, dependencies = TRUE, repos = '${CRAN_URL}'); \
               sapply(pkgs, require, character.only = TRUE);"
         
         RUN set -e \
               && curl -sS https://s3.amazonaws.com/rstudio-server/current.ver \
                 | xargs -I {} curl -sS http://download2.rstudio.org/rstudio-server-{}-amd64.deb -o /tmp/rstudio.deb \
               && gdebi -n /tmp/rstudio.deb \
               && rm -rf /tmp/rstudio.deb
         
         RUN set -e \
               && useradd -m -d /home rstudio \
               && echo rstudio:rstudio \
                 | chpasswd
         
         # expose for rstudio
         EXPOSE 8787



    ii. Download the 3 patchfiles from `here <https://github.com/datmo/docker-files/tree/master/workspace-patches>`_ and move them into your ``datmo_environment`` folder along with your Dockerfile.

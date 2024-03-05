# colibrisuce



## What it is

Colibri-suce delivers the juice for the COLIBRI project. It proposes a prove-of-concept implementation to demonstrate how
we imagine a future simulation environment that can serve to implement future building regulation codes, but also 
become a tool of choice for project work which, due to its intuitive design, will quickly become so popular that it 
will replace most existing tools, unify the building modelling approach and bring peace to the world.   

Design goals are (in order)
- intuitive: it should be possible to learn how to use and extend the system by just looking at it. We want the user experience to be so joyfull that we do not have to convince people to use the system - they will beg for it. Contributions will flow in from all over the world.
- modular: it must be possible to add a new phenomenon without any knowledge about the already existing ones - just copy a single file containinng a simple model in the language of your choice and add your formulae  
- open: it should be able to use most existing models implemented for tools like MATLAB, TRN-suce, Modellica, ...  
- automatic testing: test cases that make it unbreakable even by very motivated idiots

## Installation

### Python
We use Python 3.10 and a couple of packages. A good way to create an environment is to use conda.

### Conda

Install `Anaconda distribution <https://www.anaconda.com/distribution/>`_ or `Miniconda3 distribution <https://docs.conda.io/en/latest/miniconda.html>`_. The path to miniconda installation will be added to Windows environmental variables. The `*` represents a number corresponding to the version of miniconda installed. Restarting the computer is necessary to take into account the new paths.


### Creating the conda environment

Open a command line tool in the dimosim root folder, enter the ``ci`` folder, and then run:

    conda env create -f environment.yml

Activate the environment you just created like this:

    conda activate colibrisuce

For more information on conda environments, please visit https://conda.io/docs/using/envs.html.


### PyCharm

Pycharms is the IDE used for development, the community version is free. 
It can be downloaded here `Pycharm <https://www.jetbrains.com/fr-fr/pycharm/download/#section=windows>`_


## FAQ

### It is written in Python, will it be slow?
In the first version, yes. Optimization will be done at a late stage of the project and in such a way that 'normal' users do not realize it has been optimized. 
We favor clarity over speed. We avoid making it weired to squeeze out the last millisecond.

### Why does it have such a weired name?
Never mind, it is only temporary. Colibri is a project at CSTB aiming at defining a framework for the French Building code. 
The French word 'suce' means 'to suck' and is pronounced like 'sys' in systems like TRN-SYS.


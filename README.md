# colibrisuce



## What it is

Colibri-suce delivers the juce for the COLIBRI project. It proposes a prove-of-concept implementation to demonstrate how
we imagine a future simulation environment that can serve to implement future building regulation codes, but also 
become a tool of choice for project work which, due to its intuitive design, will quickly become so popular that it 
will replace most existing tools, unify the building modelling appraoch and bring peace to the world.   

Design goals are (in order)
- intuitive: it should be possible to learn how to use and extend the system by just looking at it. We want the user experience to be so joyfull that we do not have to convince people to use the system - they will beg for it. Contributions will flow in from all over the world.
- modular: it must be possible to add a new phenomenon without any knowledge about the already existing ones - just copy a single file containinng a simple model in the language of your choice and add your formulae  
- open: it should be able to use most existing models implemented for tools like MATLAB, TRN-suce, Modellica, ...  
- automatic testing: test cases that make it unbreakable ever by very motivated idiots

## FAQ

### It is written in Python, will it be slow?
In the first version, yes. Optimization will be done at a late stage of the project and in such a way that 'normal' users do not realize it has been optimized. 
We favor clarity over speed. We avoid making it weired to squeeze out the last millisecond.

### Why does it have such a weired name?
Never mind, it is only temporary. Colibri is a project at CSTB aiming at defining a framework for the French Building code. 
The French word 'suce' means 'to suck' and is pronounced like 'sys' in systems like TRN-SYS.


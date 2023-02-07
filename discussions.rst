
===========
Discussions
===========

Maybe we should put the discussions in issues...

Structure
=========

OOP (Oriented Object Programming) or functions or both (structure/models with OOP and computations with functions)?
Check performance and scale (e.g., object "wall", etc.)? Can we have as many objects as we would like?
How can we create a model (solar thermal combisystem) from others (pipe, pump, storage tank, etc.)?

Model
=====

Should we keep @abc.abstractmethod (on each function)?
- pros: show options to users / give opportunities
- cons: do not hide "complexity" / add code

Variable
========

Find another name for "linked_to" in variable.py (line 48)? Options:
    - expands
    - indexes

Models
======

The SimpleBuilding model (line 68) should use an interface (e.g., hasattr(climate_date)) rather than depends on the model's type/class (Weather) for flexibility

.. code-block::

    weather = self.project.get_models('Weather')[0]
    weather.climate_data['temperature']

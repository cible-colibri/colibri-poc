
Conda
-----

Conda est un système de gestion de paquets qui peut être installé via :

- `Distribution Anaconda <https://www.anaconda.com/distribution/>`_ ;
- `Distribution Miniconda3 <https://docs.conda.io/en/latest/miniconda.html>`_.

Après avoir installé le gestionnaire de paquets, il est possible de créer un
environnement. Ouvrez une console de commande dans le dossier racine de
colibri, puis exécutez :

.. code-block:: bash

    conda create -n colibri-env

Il est possible d'activer l'environnement que vous venez de créer comme ceci :

.. code-block:: bash

    conda activate colibri-env

Installer ``colibri`` pour l'utiliser :

.. code-block:: bash

    pip install colibri

ou pour développer (toujours à la racine de colibri) :

.. code-block:: bash

    pip install -e .

Pour plus d'informations sur les environnements conda, veuillez visiter :
`cond envs <https://conda.io/docs/using/envs.html>`_.

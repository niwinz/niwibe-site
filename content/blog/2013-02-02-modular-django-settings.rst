Vuelta de tuerca a los settings de django
#########################################

:tags: django

Django, por defecto viene con un unico archivo de configuración: ``settings.py`` y  para empezar 
no esta mal. De hecho, considero que el sistema de settings de django muy bueno y muy comodo. 

El problema es que el "template" de un proyecto no esta preparado para cubrir a casos complejos, con 
multiples entornos (preproducción, producción, etc). Otro problema es como evitar de una manera comoda
no meter configuracion especifica/personalizada de cada usuario en el control de versiones.


settings_local.py
=================

La primera iteración, y posiblementa la mas extendida, es crear un fichero ``settings_local.py`` al
mismo nivel que el ``settings.py`` y que ese se encargue de importarlo si existiese.

Algo así como esto:

.. code-block:: python

    # settings.py
    # [...]
    try:
        from .settings_local import *
    except ImportError:
        pass



En un principio, esta solución soluciona los problemas planteados. Evita que las configuracion especifica
del usuario  no vaya al repo. Pero tiene un problema fundamental, no puedes extender o sobreescribir 
certos atributos.

Settings como package
=====================

Despues de varias iteraciones, buscando una organización flexible y modular de settings. He 
llegado a la solucion que expondre con un ejemplo. A diferencia de lo anterior, en settings en este
caso pasa a ser un package de python, es decir un directorio.

Esta es la estructura:

.. code-block:: console

    ./fooproject/settings/__init__.py
    ./fooproject/settings/common.py
    ./fooproject/settings/development.py
    ./fooproject/settings/production.py
    ./fooproject/settings/local.py.example


Este seria el contenido de ``__init__.py``:

.. code-block:: python
    # -*- coding: utf-8 -*-

    from __future__ import absolute_import, print_function
    import os, sys

    try:
        from .local import *
    except ImportError:
        print(u"«local.py» file does not exist.")
        print(u"Go to settings directory and copy «local.py.example» to «local.py»")
        sys.exit(-1)


- ``common.py`` contendría el contenido de ``settings.py`` estandar. 
- ``development.py`` heredaría todo lo del ``common.py`` pero haria las modificaciones especifica para el entorno de desarrollo.
- ``production.py`` tendria lo mismo que ``development.py`` pero para el entorno de producción.


Aqui los ejemplos del resto de ficheros:

.. code-block:: python

    # development.py
    from .common import *
    DEBUG = True


.. code-block:: python

    # production.py
    from .common import *
    DEBUG = False

.. code-block:: python
    
    # local.py.example
    from .development import *


Con este sistema, por defecto obligamos al usuario crear un archivo **local.py** (que a su vez deberia
estar ignorado en el repo).

    DATABASES['default']['NAME'] = 'somepersonaldbname'
    DATABASES['default']['HOST'] = '192.168.1.4'


Y arrancariamos django así:


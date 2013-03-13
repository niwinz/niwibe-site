Vuelta de tuerca a los settings de django
#########################################

:tags: django


Django, por defecto viene con un unico archivo de configuración: ``settings.py`` y  para empezar
no esta mal. De hecho, considero que el sistema de settings de django es muy bueno y muy comodo.

Pero podemos detectar los siguientes problemas:

* El "template" de un proyecto no esta preparado para cubrir casos complejos, con multiples entornos (preproducción, producción, etc).
* Como evitar de una manera comoda no meter configuración especifica/personalizada de cada usuario en el control de versiones.
* Como evitar duplicacion de estructuras de configuración y poder modificar configuracion y no solo sobreescribir.


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


En un principio, esta iteracion da solucion a uno de los problemas planteados: evita que las configuración especifica
del usuario  no vaya al repo. Pero tiene un problema fundamental, solo puedes sobreescribir configuración, pero no
puedes hacer modificaciones pequeñas y parciales.

Settings como package
=====================

Despues de varias iteraciones, buscando una organización flexible y modular de settings. He
llegado a la solución que expondre con un ejemplo. A diferencia de lo anterior, en settings en este
caso pasa a ser un package de python, es decir un directorio.

Esta es la estructura:

.. code-block:: console

    ./fooproject/settings/__init__.py
    ./fooproject/settings/common.py
    ./fooproject/settings/development.py
    ./fooproject/settings/production.py
    ./fooproject/settings/local.py.example

**Nota:** Todos estos ficheros deberian estar gestionados por el control de versiones y solo y unicamente **local.py**
debe ser ignorado, debido a que ahi es donde se colocaria la configuración personalizada de cada developer.

Este sería el contenido de ``__init__.py``:

.. code-block:: python
    # -*- coding: utf-8 -*-

    from __future__ import absolute_import
    import os, sys

    try:
        from .local import *
    except ImportError:
        pass


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


Con este sistema, le damos la opcion al usuario de no tener que pasar el parametro --settings a todos
los comandos de **manage.py** creando el fichero **local.py**. Con este fichero creado, y con lo que
hemos puesto en el fichero **__init__.py** django podra cargar los settings.

Si dado el caso en mi entorno preciso otros parametros de conexion a la base de datos, solo tendria que
modificar mi local.py y añadirle lo siguiente:

.. code-block:: python

    DATABASES['default']['NAME'] = 'somepersonaldbname'
    DATABASES['default']['HOST'] = '192.168.1.4'

Y estando con seguridad de que estos cambios nunca llegaran al repo por algun descuido y que solo estoy
modificando una pequeña parte sin replicar toda la estructura de la configuración.

Esto realmente es muy util para entornos de desarrollo. Luego, en produccion, no es algo incomodo
pasar como parametro el settings que se va a usar, por lo que existe dos opciones, crear **local.py**
o especificar el modulo de settings a usar mediante el parametro **--settings**.

Con este sistema tenemos una manera flexible de tener settings locales fuera del repositorio y un sistema
modular con "herencia" de settings, evitando la duplicación de los mismos.

Ejemplo:

.. code-block:: console

    $ gunicorn_django --settings="projectname.settings.production" -w 3

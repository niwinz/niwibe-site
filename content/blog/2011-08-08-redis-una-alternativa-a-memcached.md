Title: Redis, una alternativa a memcached.
Tags: python, redis, django

Este articulo esta basado completamente en <http://trespams.com/2011/08/04/redis-vs-memcached/>.

Sabemos bien, que hoy en día memcached es casi un estándar en plataformas web, pero no hace mucho ha salido un competidor, y no precisamente con pocas ganas de pelear. En este caso, estamos hablando de redis.

Redis, es una base de datos orientada a clave valor, con soporte de distintos tipos de datos, que a igual que memcached puede ofrecer un rendimiento espectacular, sirviendo de backend para cache, ademas de darnos otras mil posibilidades.

Pequeña lista de ventajas que aporta redis:

* posibilidad de ver que claves tenemos almacenadas.
* puede ser una base de datos persistente.
* no esta limitado a la memoria, posibilidad de uso de disco.
* replicación master-slave muy simple de configurar.
* distintas bases de datos, con control separado.

Sabiendo esto y habiendo leído las pruebas de rendimiento del post original, las ventajas son mas que evidentes. Y una de las mas importantes es la persistencia y la granularidad con bases de datos. Ya que de esta manera podemos limpiar una base de datos sin interferir en otra, o una caída no hará que la cache tenga que regenerarse 100% gracias a la persistencia eventual.

### A Redis cache backend for django ###

Esta es el modulo/backend para django, que permite de una manera simple utilizar el sistema de cache de django con redis como backend.

Ademas, a la versión original, he agregado nueva funcionalidad, como por ejemplo poder elegir que protocolo usar para la serialización (véase [**pickle**][1]) como también una app de django para ver el estado de los servidores de cache de redis, teniendo información como la memoria, cpu, uptime, numero de keys, etc...

<https://github.com/niwibe/django-redis>

[1]: http://docs.python.org/library/pickle.html

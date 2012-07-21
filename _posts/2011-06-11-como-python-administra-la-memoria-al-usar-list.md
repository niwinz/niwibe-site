---
layout: post.html
title: Como python administra la memoria al usar list()
tags: [python]
---

En python, tenemos varios contenedores de variables, y en este caso hablaremos de tuplas y listas. Y aveces nos surgen las dudas de como administra python la memoria a la hora de conversión de una tupla a una lista. O mejor dicho, que cuando convertimos de una tupla a una lista, los objetos que los contienen también son instancias nuevas?

Con unos ejemplos claros veré de presentar varias situaciones de conversión y vemos lo que hace python en realidad.

En python existe una función que permite saber el identificador actual del objeto ( **id(obj)** ) y es el que voy a usar para identificar si los objetos son instancias nuevas o no.

En primer caso vemos una tupla y sus identificadores:

~~~ { python }
>>> var = ('hola', 'mundo')
>>> id(var), [id(x) for x in var]
(17316752, [17381008, 17381056])
~~~


Ahora convertimos este objeto tupla **var** a una lista y observamos que nos muestra la salida:

~~~ { python }
>>> varlist = list(var)
>>> id(varlist), [id(x) for x in varlist]
(17344920, [17381008, 17381056])
~~~

Vemos que el objeto contenedor cambia, pero los objetos que estaban dentro simplemente se han utilizado sin realizar ninguna copia. Y esto como creo que ya es mas que obvio pasa con cualquier tipo de objeto, sea string o sea cualquiera que hayamos definido nosotros.

---
layout: post.html
title: Tipado estatico en python.
tags: [python]
---

Hoy me encontré con una curiosidad! Y una vez vista la idea sabia que se podría hacer, pero no se me había ocurrido la necesidad de hacerlo.

Se trata de implementar una especie de tipado estático o control de tipos para una clase, y eso es gracias a los descriptores de las nuevas clases de python, las que derivan de __object__.

El articulo original es de [Crysol][1], que por cierto, recomendó seguir este blog por que suele publicar cosas bastante interesantes.

[1]: http://crysol.org/es/node/1500

El ejemplo que presentan es:

~~~ { python }
class TypedAttr(object):
    def __init__(self, name, cls):
        self.name = name
        self.cls = cls

    def __get__(self, obj, objtype):
        if (obj is None):
            raise AttributeError()

        try:
            return obj.__dict__[self.name]
        except KeyError:
            raise AttributeError

    def __set__(self, obj, val):
        if not isinstance(val, self.cls):
            raise TypeError("'%s' given but '%s' expected" % \
              (val.__class__.__name__, self.cls.__name__))

        obj.__dict__[self.name] = val
~~~


¿Y que es lo que hace esta clase? Lo que realmente hace es implementar el los métodos <code>__get__</code>
y <code>__set__</code> y cada uno de ellos recibe 2 argumentos.

En caso del <code>__set__</code> el primer parámetro **obj** es el objeto al que esta asociado, y el segundo es el valor que quiere asignarle. Y en el caso de <code>__get__</code> nos pasa el objeto al que esta asociado y la clase de la que se instancia.

Gracias a esto podemos por así decirlo recuperar información interna guardada en el objeto anfitrión que contendría este atributo para controlar el tipo de dato.

No creo que esta explicación quede algo clara, pero creo que con un ejemplo con los mensajes de debug descomentados podríamos ver que es lo que realmente pasa. Este es el script de ejemplo que he usado:

~~~ { python }
class A(object):
    a = TypedAttr("__a", str)

A1 = A()
A1.a = "hola"

print A1.a
A1.a = 1
~~~


Y esta es la salida de debug que nos pinta en la terminal:

~~~ { python }
debug2 <__main__.A object at 0x1373650> hola
debug <__main__.A object at 0x1373650> <class '__main__.A'>
hola
debug2 <__main__.A object at 0x1373650> 1
Traceback (most recent call last):
  File "test2.py", line 32, in <module>
    A1.a = 1
  File "test2.py", line 19, in __set__
    raise TypeError("'%s' given but '%s' expected" % (val.__class__.__name__, self.cls.__name__))
TypeError: 'int' given but 'str' expected
~~~

Vemos que cuando intentamos asignar un entero, nos salta un error diciendo que solo podemos asignar strings.

Este articulo es una mera copia del articulo de crysol con alguna que otra palabra mía por medio. Todos los méritos se lo lleva el autor original del articulo enlazado en la parte superior.

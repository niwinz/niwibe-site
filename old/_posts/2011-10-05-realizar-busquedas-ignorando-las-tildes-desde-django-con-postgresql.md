---
layout: post.html
title: Realizar búsquedas ignorando las tildes desde Django con PostgreSQL
tags: [python, django, postgresql]
---

En muchas ocasiones, necesitamos realizar búsquedas por palabras pero sin tener en cuenta las tildes. Y en este caso usando PostgreSQL 9.1, tenemos la extensión **unaccent** que nos permite dejar sin tildes una palabra o un conjunto de palabras.

Otra de las ventajas de utilizar PostgreSQL, es por que nos permite crear indices a expresiones o funciones.

Como primer paso creamos el indice en el campo que vamos a usar para las búsquedas e instalamos la extensión:

~~~ { sql }
CREATE EXTENSION unaccent;
ALTER FUNCTION unaccent(text) IMMUTABLE;
CREATE INDEX person_name_idx0 ON person USING btree (unaccent(name));
~~~

Una vez tenemos la base de datos preparada para realizar consultas, aqui un ejemplo de como realizar una busqueda ignorando las tildes:

~~~ { python }
>>> Person.objects.extra(where=["unaccent(name) = %s"], params=["Andrei"])
[<Person: 1>]
~~~

---
layout: post.html
title: First y Last postgresql aggregates y como usarlos en django.
tags: [postgresql, django]
---

Muchas veces nos encontramos en la situacion, cuando necesitamos sacar una lista ordenada de ultimos elementos (heterogeneos) agrupado por una "foreign key", y no sere de menos. Investigando y probando sobre el ORM de Django, a ver si se podria hacer algo, y ya perdidas todas la esperanzas me he topado con [este articulo.](http://www.postgresonline.com/journal/archives/68-More-Aggregate-Fun-Whos-on-First-and-Whos-on-Last.html)

Como dice, MS access tiene un particular conjunto de Aggregates, llamadas First y Last, que nos permiten secar primero o el último elemento de una consulta. Como sabemos que Access no es perfecto, veremos de crear nuestro mundo perfecto en PostgreSQL (traducción literal).

### Definicion de funciones y aggregates: ###

~~~ { sql }
CREATE OR REPLACE FUNCTION first_element_state(anyarray, anyelement)
    RETURNS anyarray AS
$$
    SELECT CASE WHEN array_upper($1,1) IS NULL THEN array_append($1,$2) ELSE $1 END;
$$
LANGUAGE 'sql' IMMUTABLE;

CREATE OR REPLACE FUNCTION first_element(anyarray)
    RETURNS anyelement AS
$$
    SELECT ($1)[1] ;
$$
LANGUAGE 'sql' IMMUTABLE;

CREATE OR REPLACE FUNCTION last_element(anyelement, anyelement)
    RETURNS anyelement AS
$$
    SELECT $2;
$$
LANGUAGE 'sql' IMMUTABLE;

CREATE AGGREGATE first(anyelement) (
    SFUNC=first_element_state,
    STYPE=anyarray,
    FINALFUNC=first_element
);

CREATE AGGREGATE last(anyelement) (
    SFUNC=last_element,
    STYPE=anyelement
);
~~~

### Aplicando a la practica: ###

Ahora suponemos que tenemos Item's u que cada uno pertenece a un Design, ahora queremos sacar el último item insertado por cada Design.

Este seria un ejemplo de sql:

~~~ { sql }

SELECT first(id) as id FROM (SELECT * FROM items WHERE code LIKE 'XXX%' ORDER BY created_date DESC)
as foo GROUP BY design_id;
~~~


Y usarlo en django es tan simple como:

~~~ { python }
Item.object.raw("SELECT first(id) as id FROM (SELECT * FROM items ORDER BY created_date DESC) as foo GROUP BY design_id")
~~~



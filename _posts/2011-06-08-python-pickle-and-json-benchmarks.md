---
layout: post.html
title: Python pickle and json benchmarks
tags: [python]
---

Leyendo twitter un día de estos me encontré con un twit (valga la redundancia) con un par de enlaces sobre la diferencia de rendimiento que había entre diferentes versiones de python en la serialización con json y pickle y distintas implementaciones.

Pero me picó la curiosidad de realizar pruebas propias, esta vez sobre python3 (3.2) y comparar los resultados con python2 (2.7).

Primero pense que la version 2 de python sería la que tendría el mejor rendimiento, sobretodo después de algunas menciones de que python3 era posiblemente más lento que 2 debido al uso de unicode, pero los resultados me sorprendieron bastante.

Un apunte de ultima hora, y es que he notado que en python2 las cadenas unicode (u"foo") son bastante mas rapidas de serializar que las cadenas estandar (str).

Los resultados de las pruebas para python3:

    JSON benchamark...
    RESULT => 7.364138126373291
    PICKLE benchmark...
    RESULT => 2.680925130844116

Los resultados de las pruebas para python2:

    JSON benchamark...
    RESULT => 8.85393881798
    PICKLE benchmark...
    RESULT => 8.89091897011
    SPECIAL JSON benchmark (str)...
    RESULT => 8.9193341732
    SPECIAL PICKLE benchmark (str)...
    RESULT => 41.0080709457


El script usado para realizar las pruebas es valido tanto para python3 como para python2. Puede descargarlo [desde aquí.][1].

[1]: http://www.niwi.be/media/webfiles/2011/04/05/testpy3.py

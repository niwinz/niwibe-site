Title: XZ vs World
Tags: sys

XZ es un formato de fichero de compresión sin perdida que utiliza un algoritmo casi idéntico de lzma2. A pesar de que ya muchas distribuciones lo usan como formato por defecto para comprimir los paquetes de aplicaciones, las personas somos muy de costumbres y nos cuesta cambiar. Sobre todo cuando estamos tan acostumbrados a los míticos gzip y bzip2.

Pero creo que les esta llegando la hora de jubilación. XZ es una alternativa real. Ademas de que ya es parte de la mayoría de distribuciones linux, freebsd y netbsd.

Aqui van mis rudimentarias pruebas al comprimir el directorio del trunk de django. Hay que tener en cuenta, y es que xz tiene un nivel mas de compresión a deferencia de gzip y bzip2.


*Gzip* con nivel 1 de compresión

    [niwi@vaio.niwi.be][~/compress]% time gzip -1 django.tar
    gzip -1 django.tar  0.52s user 0.02s system 99% cpu 0.540 total
    [niwi@vaio.niwi.be][~]% du -sh django.tar.gz
    6.1M    django.tar.gz
    [niwi@vaio.niwi.be][~/compress]% time gunzip django.tar.gz
    gunzip django.tar.gz  0.20s user 0.05s system 97% cpu 0.255 total

*Gzip* con nivel 6 de compresión

    [niwi@vaio.niwi.be][~/compress]% time gzip -6 django.tar
    gzip -6 django.tar  1.12s user 0.02s system 99% cpu 1.149 total
    [niwi@vaio.niwi.be][~/compress]% du -sh django.tar.gz
    5.0M    django.tar.gz
    [niwi@vaio.niwi.be][~/compress]% time gunzip django.tar.gz
    gunzip django.tar.gz  0.19s user 0.04s system 96% cpu 0.238 total

*Gzip* con nivel máximo de compresión

    [niwi@vaio.niwi.be][~/compress]% time gzip -9 django.tar
    gzip -9 django.tar  3.17s user 0.02s system 98% cpu 3.223 total
    [niwi@vaio.niwi.be][~/compress]% du -sh django.tar.gz
    4.9M    django.tar.gz
    [niwi@vaio.niwi.be][~/compress]% time gunzip django.tar.gz
    gunzip django.tar.gz  0.20s user 0.03s system 99% cpu 0.226 total

*Bzip2* con nuvel 1 de compresión

    [niwi@vaio.niwi.be][~/compress]% time bzip2 -z1 django.tar
    bzip2 -z1 django.tar  3.44s user 0.02s system 97% cpu 3.535 total
    [niwi@vaio.niwi.be][~/compress]% du -sh django.tar.bz2
    4.4M    django.tar.bz2
    [niwi@vaio.niwi.be][~/compress]% time bzip2 -d django.tar.bz2
    bzip2 -d django.tar.bz2  0.84s user 0.02s system 99% cpu 0.867 total


*Bzip2* con nivel 6 de compresión

    [niwi@vaio.niwi.be][~/compress]% time bzip2 -z6 django.tar
    bzip2 -z6 django.tar  4.04s user 0.04s system 99% cpu 4.108 total
    [niwi@vaio.niwi.be][~/compress]% du -sh django.tar.bz2
    3.2M    django.tar.bz2
    [niwi@vaio.niwi.be][~/compress]% time bzip2 -d django.tar.bz2
    bzip2 -d django.tar.bz2  1.03s user 0.05s system 98% cpu 1.088 total

*Bzip2* con nivel máximo de compresión

    [niwi@vaio.niwi.be][~/compress]% time bzip2 -z9 django.tar
    bzip2 -z9 django.tar  4.45s user 0.03s system 99% cpu 4.528 total
    [niwi@vaio.niwi.be][~/compress]% du -sh django.tar.bz2
    3.0M    django.tar.bz2
    [niwi@vaio.niwi.be][~/compress]% time bzip2 -d django.tar.bz2
    bzip2 -d django.tar.bz2  1.31s user 0.03s system 98% cpu 1.369 total

*XZ* con nivel 0 de compresión

    [niwi@vaio.niwi.be][~/compress]% time xz -z0 django.tar
    xz -z0 django.tar  1.48s user 0.03s system 95% cpu 1.584 total
    [niwi@vaio.niwi.be][~/compress]% du -sh django.tar.xz
    3.5M    django.tar.xz
    [niwi@vaio.niwi.be][~/compress]% time xz -d django.tar.xz
    xz -d django.tar.xz  0.42s user 0.02s system 97% cpu 0.456 total

*XZ* con nivel 6 de compresión

    [niwi@vaio.niwi.be][~/compress]% time xz -z6 django.tar
    xz -z6 django.tar  13.42s user 0.15s system 99% cpu 13.645 total
    [niwi@vaio.niwi.be][~/compress]% du -sh django.tar.xz
    2.4M    django.tar.xz
    [niwi@vaio.niwi.be][~/compress]% time xz -d django.tar.xz
    xz -d django.tar.xz  0.28s user 0.05s system 99% cpu 0.336 total

*XZ* con nivel máximo de compresión

    [niwi@vaio.niwi.be][~/compress]% time xz -z9 django.tar
    xz -z9 django.tar  14.26s user 0.28s system 99% cpu 14.643 total
    [niwi@vaio.niwi.be][~/compress]% du -sh django.tar.xz
    2.3M    django.tar.xz
    [niwi@vaio.niwi.be][~/compress]% time xz -d django.tar.xz
    xz -d django.tar.xz  0.29s user 0.05s system 97% cpu 0.351 total


Vemos que gzip efectivamente es el mas rápido, pero desde luego es un claro perdedor a la hora de comparar su capacidad para comprimir. Luego nos encontramos con Bzip2, que no hasta hace mucho, era el mas usado por la tasa de compresión es bastante mejor que la de gzip. Pero si lo comparamos con XZ, vemos que con el nivel mínimo de compresión llega a comprimir casi igual que bzip2 con nivel 6 y mucho mas eficiente en cuestión de tiempo.

Esta claro que cuanto mas le subimos el nivel de compresión, mas sube el consumo de tiempo. Si comparamos bzip2 y xz en el máximo nivel de compresión, vemos que xz es bastante mas lento. Pero si hasta ahora nos conformabamos con la tasa de compresion de bzip2, ahora podemos tener la misma tasa en mucho menos tiempo, y cuando necesitemos el máximo nivel de compresion, sacrificamos tiempo.


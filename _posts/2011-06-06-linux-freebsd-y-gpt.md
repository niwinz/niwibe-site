---
layout: post.html
title: Linux, FreeBSD y GPT
tags: [freebsd, linux, gpt]
---

Tabla de partición GUID (GPT) es un estándar para la colocación de la tabla de particiones
en un disco duro físico. Es parte del estándar Extensible Firmware Interface (EFI) propuesto por Intel para reemplazar la vieja BIOS del PC, heredada del IBM PC original. La
GPT sustituye al Master Boot Record (MBR) usado con la BIOS.

Puede leer mas en el [articulo de Wikipedia](wikipedia)

[wikipedia]: http://es.wikipedia.org/wiki/Tabla_de_partición_GUID

Ventajas y desventajas.
-----------------------

Actualmente cada vez mas, tenemos discos de tamaños mas elevados, y cada ves se hace mas
uso de sistemas de ficheros como zfs o agrupando varios discos en un solo volumen,  y esto
hace mas propenso a que vayamos a necesitar particiones con mas de 2TB. Cosa que con el
particionamiento antiguo no se puede debido a su limitación a 32 bits.

GPT esta hecho para sistemas 64bits, pero igual puede usarse para sistemas con 32 bits de
la misma manera.

Ademas del tamaño de partición, también a veces necesitamos mas particiones de las que nos
puede permitir el antiguo sistema de particionamiento. En este caso, el numero máximo por
defecto en GPT son 128, pero puede ser modificado en caso de que sea realmente necesario.

Otro punto a favor, es que en sistemas como freebsd, gpt permite el uso de zfs para todo
el sistema y con posibilidad de arrancar. Freebsd lo soporta completamente ademas de
tenerlo todo integrado en el Framework GEOM.

En linux a diferencia, aparte de la aplicación «GNU Parted», las demás aplicaciones no
soportan GPT, y en algunas distribuciones ni siquiera esta compilado el soporte del kernel.

Por no hablar que muchas distribuciones, incluyen grub de primer generación, el cual sin
parches adicionales no es capaz de arrancar de una partición GPT.

El uso de GPT es mas recomendado en sistemas que funcionan como servidores para que puedan
escalar en el tema de almacenamiento sin ninguna dificultad y contratiempo.


FreeBSD y GPT
-------------

Como he dicho antes, GPT esta perfectamente integrado dentro de GEOM, por lo que crear un
esquema de particionamiento de este tipo es muy simple.

Supongamos que el disco con el que trabajamos, es «ad4»:

    gpart create -s GPT ad4
    gpart add -b 34 -s 128 -t freebsd-boot ad4
    gpart add -b 162 -s 5242880 -t freebsd-swap ad4
    gpart add -b 5243042 -s 125829120 -t freebsd-ufs ad4


Esto asigna 3 particiones:  la primera es para el código de arranque de GPT y es de un
tamaño de 64K, la segunda es para swap y es de un tamaño de 2.5GB y la ultima es para «/»
y tiene un tamaño de 60GB.

Una vez creadas las particiones podemos crear el sistema de ficheros y asignar un label:

    newfs -U /dev/ad4p3
    glabel create raiz ad4p3

Ahora si queremos que el sistema arranque deberíamos ejecutar el siguiente comando:

    gpart bootcode -b /boot/pmbr -p /boot/gptboot -i 1 ad4


Instalación de freebsd sobre GPT
--------------------------------

Supongamos que estamos usando la imagen de freebsd-9-current sobre un pendrive. Arrancamos
y nos dirigimos a modo «Fixit» y le indicamos que sea desde USB.

Montamos «/dev/label/raiz» a «/mnt» y nos dirigimos a «/dist/9.0-CURRENT-201004/base». Realizamos la instalación con el comando:

    DESTDIR=/mnt sh install.sh

Una vez realizada la instalación del sistema base, nos dirigimos a «/dist/9.0-CURRENT-201004/kernel» y con el comando que viene a continuación, realizamos la instalación del kernel:

    DESTDIR=/mnt sh install.sh GENERIC

Una vez instalado, cambiamos al directorio /mnt/boot y re-nombramos GENERIC por «kernel».
Ahora ya podrá arrancar un sistema base sobre GPT, y no olvídense de crear los siguientes
archivos: «/mnt/etc/fstab» y «/mnt/etc/rc.conf».


GPT y ZFS sobre FreeBSD
-----------------------

Para empezar son los mismos pasos que para usarlo con UFS, con unas pequeñas variaciones
que mostrare a continuación:

En vez de ejecutar «gpart add -b 5243042 -s 125829120 -t freebsd-ufs ad4» ejecutamos:

    gpart add -b 5243042 -s 125829120 -t freebsd-zfs ad4

Y el para que pueda arrancar desde zfs:

    gpart bootcode -b /boot/pmbr -p /boot/gptzfsboot -i 1 ad4

Ahora, procedemos con la configuración de zfs, añadiendo las siguientes lineas a
«/mnt/boot/loader.conf»:

    zfs_load="YES"
    vfs.root.mountfrom="zfs:data"

También necesitamos añadir lo siguiente a «/mnt/etc/rc.conf»:

    zfs_enable="YES"

A partir de aquí puede proceder la instalación estándar explicada anteriormente con la
única diferencia de usar: DESTDIR=/data/

Ahora por ultimo, especificamos que zfs monte las particiones de manera "antigua":

    zfs set mountpoint=legacy data
    zpool set bootfs=data data


GPT sobre linux
---------------

A diferencia de freebsd, en linux necesitamos que kernel tenga compilado el soporte de
gpt, en caso contrario deberíamos re compilar el kernel o no podremos usar esta
característica. Como mencione antes, tampoco tenemos muchas herramientas para trabajar con
gpt aparte de «gnu parted», que por suerte si se encuentra en el cdrom de «Archlinux».

Una manera basica de crear la misma estructura que con freebsd usando parted:

    parted /dev/sda
    mklabel gpt
    mkpart primary 0 2.5G
    mkpart primary 2.5G 62.5G
    quit

Otra gran diferencia de freebsd es que en linux se ve que no contamos con nigun sistema
para arrancar que sea decente, ya que si nos ponemos a mirar grub legacy, incluido en
muchas distribuciones linux, no tiene soporte para GPT. Grub2 que se ve que es una
reescritura de grub para mejorar y con todo lo aprendido de grub, no se sabe si tiene
soporte debido a que esta completamente indocumentado. Por no hablar del soporte de xfs,
que no lo hay en grub legacy y en grub2 esta "experimental".

Lilo, que esta desmantenido desde el 2007, a diferencia de grub, no tiene esas carencias,
y es el unico que es capaz de arrancar el computador de este sistema de particionamiento.
Lastima que fue desmantenido.

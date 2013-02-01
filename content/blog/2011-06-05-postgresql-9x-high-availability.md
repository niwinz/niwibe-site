Title: PostgreSQL 9.x & High Availability
Tags: postgresql

En PostgreSQL 9.x se introducen varias características que nos permiten usar los registros de archivos wal para realizar replicación «master-slave», lo que a su vez nos da la posibilidad de tener un cluster de alta disponibilidad «activo-pasivo». Es decir, un servidor maestro y otro/s que están a la espera con replicación activada. En caso de que el servidor principal falle, puede activarse automáticamente uno de los muchos servidores «standby». También cabe mencionar que los servidores de espera pueden ser usados como nodos de acceso de solo lectura, es decir, en modo «hot_standby».

El funcionamiento se basa en que el servidor principal esta funcionando y ofreciendo su servicio y funcionando siempre con «continuous archiving mode», que quiere decir que continuamente registrará los archivos «Wal»

> *Véase*: [documentación oficial](http://www.postgresql.org/docs/9.0/static/continuous-archiving.html)

No es necesario ningún cambio en las tabas ni las bases de datos y tampoco requiere mucha mano de obra por parte del administrador, comparando-lo con otros sistemas de clusterización. De igual manera, no sobrecarga de manera excesiva el servidor principal, por lo que el rendimiento no se vería casi afectado.

PostgreSQL implementa dos maneras de transferir los logs binarios («Wal»), mediante sistema de ficheros, o en streaming. Los archivos «Wal» por norma general ocupan unos 16MB por lo que si esta trabajando en red de área local, no creo que un traspaso de estos ficheros sea una carga excesiva. Pero también se debe saber que el tamaño y la regularidad de creación de estos ficheros se puede re-configurar.

Siempre debe tener en cuenta, que los logs binarios se crean después de cada commit hace que los datos tengan un pequeño retraso, y en una fallida catastrófica siempre cabe que no se haya guardado el ultimo commit. Esto ultimo siempre puede ser compensado con algún sistema de replicación,mirroring o algún sistema raid. Zfs es una de las mejores soluciones para este tipo de clusters.

En el tema del rendimiento de recuperación, es bastante aceptable en muchos ámbitos, ya que no es una tarea complicada pasar del modo de recuperación a modo operativo. Tambien se puede decir que no es del todo un sistema de clusterización si no que un sistema de recuperación por fallas catastróficas. En cambio, con streaming se puede conseguir una tasa de sincronización muchísimo mas elevada, lo que si que puede llamarte clusterización de alta disponibilidad. Consiste en base de lo mismo, solo que los logs se pasan directamente por tcp sin espera de creación de ficheros.

¿Que debo saber?
----------------

El servidor principal y los «esclavos» que estan en modo recuperacion deberian tener caracteristicas similares o iguales, hablando de hardware como de software. Ademas, es obligatorio que se usen versiones identicas del servidor PostgreSQL, por no decir la arquitectura del procesador. No puedes tener el servidor principal con «x86_64» y los esclavos en «x86».
«Standby servers» o servidores esclavos de recuperación.

Los servidores de recuperación o esclavos, funcionan continuamente en modo «recovery», es decir, a la espera de nuevos logs «Wal». Tal como lo he comentado mas arriba, puede hacerse a través de sistema de ficheros, o por streaming vía tcp/ip.

El procedimiento teórico del funcionamiento de un servidor esclavo en modo recuperación se basa en pocos pasos: al iniciarse empieza restaurando todos los wall del directorio del backup o archivo, con el comando especificado en la variable «restore_command», cuando este falle, y intentas restaurar todo lo disponible en su directorio local «pg_xlog». Si es te falla, y esta configurada la opción de replicación por streaming, intenta conectarse y obtener todos los datos que sean necesarios. En caso de que no este configurada esta opción, vuelve a empezar con el primer paso. Es una cadena que solo se termina al apagar el servidor o que sea creado un archivo indicador que el servidor tenga que pasar de modo recuperacion a modo activo.

### Replicación basada en sistema de ficheros en red. ###

Tal como lo he comentado anteriormente, la replicación basada en sistema de ficheros compartido tiene un pequeño retraso, ya que siendo que hasta que no se llene el archivo «wal» y no se archive, ese no sera transferido a los esclavos, siendo este el principal problema.

El concepto es muy simple, para que un servidor pueda acceder al directorio de los «wal» archivados, ese debe ser compartido por nfs o cualquier otro sistema de ficheros en red. Consulte la documentación de la distribución o sistema operativo, para realizar esta parte.

Tambien tenemos que modificar ciertas cosas en «postgresql.conf» añadiendo/modificando los siguientes contenidos que explicare mas adelante:

    archive_mode = on
    archive_command = 'cp -i %p /mnt/xlog_archive/%f < /dev/null'
    archive_timeout = 0
    hot_standby = on
    wal_level = hot_standby

En primer lugar, activamos el proceso que archiva los «wal» en ves de reutilizarlos y asigna un comando, el cual se encarga de copiar el archivo «wal» lleno a otro directorio, que por norma general deberia ser un disco aparte, asi evitaremos dentro de lo que cabe cierta perdida de rendimiento que se pierde.

Con «hot_standby» activado, nos permitirá acceder en modo de solo lectura a un servidor esclavo y «wal_level» indica el nivel de datos que se guardara en los archivos «wal», por defecto esta en minimal, pero para la replicación minimamente se necesita el modo archive, pero para nuestro caso que ademas de eso queremos que los servidores esclavos puedan atender peticiones de solo lectura, ponemos el modo hot_standby.

Antes de arrancar el servidor, realizaremos una copia exacta del directorio, para luego transferirlos a un servidor esclavo, eso es críticamente necesario, ya que la id de la base de datos que se genera con el initdb debe ser la misma tanto en el servidor maestro como en el esclavo.

Puede darse el caso de que, no este partiendo de una instalación desde cero, en este caso necesita hacer una parada y activar las opciones que antes he comentado y realizar un backup consistente. En otro caso, si ya tiene activadas esas opciones puede realizar un backup en caliente tal como lo indica la documentación de PostgreSQL.

Y como ultimo caso, puede usarse uno de los scripts que he publicado, que realiza una sincronización completa con el servidor maestro, sin necesidad de transferir ningún backup adicional.

Una vez tenemos todo listo, los dos últimos pasos consisten en montar el sistema de ficheros compartido con los archivos «wal» del servidor maestro en algún directorio del servidor esclavo, y crear un archivo «recovery.conf» en el directorio root de la base de datos ( en el caso de archlinux es «/var/lib/postgres/data» ) antes de arrancar la base de datos.

El archivo «recovery.conf»:

    standby_mode = 'on'
    restore_command = 'cp /mnt/xlog_archive/%f %p'
    trigger_file = '/tmp/trigger_file'


Arrancamos la base de datos y analizamos el archivo de registro de la misma, nos debe aparecer algo parecido a esto:

    LOG: entering standby mode ... then some time later ...
    LOG: consistent recovery state reached LOG: database system is ready to accept read only connections

### Replicación basada en streaming. ###

A diferencia de la anterior, la replicación basada en streaming tiene claras ventajas, el retraso en el que los datos son transferidos desde el servidor maestro al esclavo son mínimos. Para poder arrancar un servidor esclavo en modo streaming, antes deberíamos haber hecho los mismos pasos que he expuesto en el anterior método, con alguna que otra modificación.

Deberiamos añadir o modifcar las siguientes lineas adicionales en «postgresql.conf»:

    max_wal_senders = 20
    wal_sender_delay = 200ms

Ademas tenemos que modificar «pg_hba.conf» y añadimos la siguiente line, la cual dice que cualquier ip de la red local pueda y deba acceder como un servidor esclavo y autenticarse mediante un usuario y contraseña:

    host replication all 192.168.1.0/24 md5

El archivo «recovery.conf» para este caso es:

    standby_mode = 'on'
    restore_command = 'cp /mnt/xlog_archive/%f %p'
    primary_conninfo = 'host=192.168.1.2 port=5432 user=root password=123123'
    trigger_file = '/tmp/trigger_file'

Todo lo demás es igual o prácticamente igual, por lo que si surge algún problema, revise sus pasos.

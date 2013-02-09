Una manera (de muchas) de desplegar un proyecto django
######################################################

:tags: django, python

Introducción
============

En mi trabajo, con cada salida de un proyecto siempre iteramos y mejoramos nuestra "manera"
de desplegar un proyecto django. Esto es posiblemente una de las iteraciones mas usadas.

No voy a tratar de explicar donde hacer deploy, ya que no es la idea de este articulo pero si
puedo decir que es un metodo mas o menos generico y serviria para casi cualquier servidor en
cloud (AWS por ejemplo) o un dedicado mas clasico.

Heroku, dotCloud, cloudfoundry y parecidos tienen sus diferencias debido a que abstraen gran
parte de lo que se va a explicar en este articulo.

Gunicorn_, Supervisor_ y Nginx_ es el stack tecnologico usado mayoritariamente. A veces he
apostado por uwsgi y me ha dado buen resultado, pero paso por una temporada de cambios que
afectaban gravemente la compatibilidad con FreeBSD y por ese motivo Gunicorn_ es la opcion
por defecto.

Otra herramienta casi imprescindible es virtualenvwrapper_ y si aun no lo has probado recomiendo
que este fuera tu primer paso.

.. _Gunicorn: http://gunicorn.org/
.. _Supervisor: http://supervisord.org/
.. _Nginx: http://nginx.com/
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/


Primeros pasos
==============

Antes de empezar a meternos de lleno en la configuración y instalar cosas, hay que tener claro
la organización que se va a tomar. Yo opto por tener la gran parte de las cosas en espacio
de usuario, es decir, nada de ``/srv`` ni ``/opt`` si no que poner todo en el **home** de un
usuario creado especifico en el proyecto.

Una aproximación: ``/home/fooproject/``. Así que, creamos el usuario:

.. code-block:: console

    useradd -g users -G sudo,nogroup -m fooproject
    mkdir -p /home/fooproject/logs

.. note::

    En distribuciones que no son ubuntu u otros sistemas operativos tipo unix (bsd) lo mas probable
    es que tengan el grupo **wheel** en vez del sudo.

.. note::

    Las instrucciones de instalación se basan en una ubuntu server. Tambien suelo usar
    FreeBSD, pero la finalidad de este articulo no es enseñar como instalar en las distros si no
    a configurar bien los servicios.


Ahora que sabemos donde va a estar todo, pasamos a la parte de instalación de herramientas basicas
como las mencionadas anteriormente.

.. code-block:: console

    sudo apt-get install nginx supervisor virtualenvwrapper python-dev build-essential

En ubuntu, como es de esperar, la instalación de virtualenvwrapper_ no es estandar, y te coloca
los archivos de arranque en sitions que menos uno se espera, pero el resultado final, es que
si vuelves a logarte como el usuario, los scripts de bootstrap habran inicializado el directorio
de virtualenvs.


Configuración de supervisord
============================

Supervisor_ es una aplicación que permete controlar y administrar procesos (daemons) de una manera
flexible y que sirve muy bien para arancar procesos controlados por el usuario sin necesidad de meterse
en las entrañas de sistemas de aranque como sysv, bsd o systemctl.

Tampoco se salva la configuración inicial de supervisord. Por lo que toca modificarla. Abrimos el
fichero ``/etc/supervisor/supervisord.conf``. Es un fichero de configuración en formato ``ini`` por
lo que seguramente ya será familiar.

Modificamos la primera sección del fichero para que quede de esta manera:

.. code-block:: ini

    [unix_http_server]
    file=/var/run/supervisor.sock
    chmod=0770
    chown=nobody:nogroup

Basicamente con esto, permitimos que los usuarios puedan controlar los procesos arrancados con supervisord
sin tener que logarse como root ni usar sudo.

Y como ultimo paso, creamos un fichero ``fooproject.conf`` dentro del directorio ``/etc/supervisor/conf.d/``.
Este seria una aproximación a lo que solemos usar:

.. code-block:: ini

    [program:django]
    command=/home/fooproject/.virtualenvs/fooproject/bin/gunicorn -w 3 -t 60 fooproject.wsgi
    directory=/home/fooproject/fooproject/src/
    numprocs=1
    autostart=true
    autorestart=false
    stopsignal=INT
    stopwaitsecs=2
    startsecs=2
    redirect_stderr=true
    stdout_logfile=/home/fooproject/logs/gunicorn.log
    stdout_logfile_backups=20
    stdout_logfile_maxbytes=20MB
    user=fooproject

Aqui podemos ver que estamos usando gunicorn instalado dentro del virtualenv correspondiente
y los logs de la aplicación reciden en su home, en el directorio ``logs``.

Gunicorn por defecto escucha en **127.0.0.1** y puerto **8000** y es el que usamos por defecto. Hay
casos en los que usamos sockets unix pero no voy a adentrarme en ello.

Nginx
=====

Una vez tenemos el supervisor levantado, ahora toca modificar la configuración de nginx. Personalmente
la configuración inicial que tiene en ubuntu tampoco me convence por lo que modificare varias partes.

Este es el archivo de configuración ``/etc/nginx/nginx.conf``:

.. code-block:: nginx

    user www-data;
    worker_processes 2;
    pid /var/run/nginx.pid;

    events {
        worker_connections 1024;
    }

    http {
        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 15;
        types_hash_max_size 2048;

        include /etc/nginx/mime.types;
        default_type application/octet-stream;

        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

        gzip on;
        gzip_disable "msie6";

        gzip_vary on;
        gzip_proxied any;
        gzip_comp_level 6;
        gzip_buffers 16 8k;
        gzip_http_version 1.1;
        gzip_types text/plain text/css application/json application/x-javascript
                        text/xml application/xml application/xml+rss text/javascript;

        include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/*;
    }

Por defecto, ubuntu trae este fichero con un monton de basura comentada, por lo que mas sincera
recomendación es borrarla y colocar un fichero simple y con contenidos especificos y controlados.

Y como ultimo paso, procedemos a añadir el siguiente archivo de configuración para nuestro host.
Como es un supuesto caso en el que es el primer y unico virtualhost, lo colocamos en ``/etc/nginx/sites-available/default``.

.. code-block:: nginx

    server {
        listen 80 default_server;
        server_name fooproject.se;

        client_max_body_size 50M;
        charset utf-8;

        access_log /home/fooproject/logs/nginx.access.log;
        error_log /home/fooproject/logs/nginx.error.log;

        location / {
            proxy_set_header Host $http_host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_set_header X-Forwarded-Protocol $scheme;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_pass http://127.0.0.1:8000/;
            proxy_redirect off;
        }

        location /static {
            alias /home/fooproject/fooproject/src/static;
            expires 30d;
        }
    }


Con esto ya tendríamos lo minimo para poder desplegar. Ahora, cada caso siempre tiene sus diferencias
y hay que adaptar la configuración a las necesidades que se nos presenten.

Enlaces de interes:

* https://speakerdeck.com/helgi/nginx-and-php-match-made-in-heaven

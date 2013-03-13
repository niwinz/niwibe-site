Optimizing server for heavy load django application
###################################################

:tags: django, nginx, gunicorn

A lot of time, I turn up


Many times, we only care to optimize the database, nginx or WSGI server, and often is more than enough.
But, when you have a web application that must be able to scale and support over 2000 concurrent users,
this is totally insufficient.

Here comes the part where we have to optimize the operating system, such as kernel parameters for TCP/IP
stack, and more.

File descriptor limit
---------------------

As a first step, we need to accept a lot of http requests. So we have to adapt nginx settings and operating
system settings (linux) for their requirements.

We know that each incoming socket is a file descriptor used. And by default a normal user has a limit of
1024 file descriptors. To accept many requests, we need to modify this parameter on both: nginx config and
linux kernel parameters.

For modify the limit of fd's for a users, your need modify ``/etc/security/limits.conf`` file, and add
these lines:

.. code-block:: limits

    # For nginx, if your nginx runs with
    # other user, put its instead of www-data
    www-data   soft    nofile      256000
    www-data   hard    nofile      260000

    # If you wsgi server runs as user
    @users      soft    nofile      256000
    @users      hard    nofile      260000

    # Puts nofile limits equals for all users
    #*          soft    nofile      256000
    #*          hard    nofile      260000

In rare cases, the kernel has a hard limit for open files vert low, and, if you put open file number
hight of kernel hight limit on limits.conf, will no have any effect. In this case, you need increase kernel
limit midifying ``fs.file-max``.

On my system the kernel hard limit is very big and I have not worry about it.

.. code-block:: console

    [5.0.2]root@niwi:~niwi# sysctl fs.file-max
    fs.file-max = 398897

Otherwhise, set a new value for this kernel paramer on **/etc/sysctl.conf**:

.. code-block:: sysctl

    fs.file-max=260000


After this, you can modify a nginx configuration, and put a accept connection parameter to a huge
number of connections:

.. code-block:: nginx

    # /etc/nginx/nginx.conf
    user www-data;

    # this number really depends of number
    # of cpu/cores on your server
    worker_processes 4;
    pid /var/run/nginx.pid;

    events {
        worker_connections 4069;
        use epoll;
    }

    http {
        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;

        # Large values reduce performance
        # for requests to wsgi server.
        keepalive_timeout 15;
        types_hash_max_size 2048;

        # [...]
    }


Connection backlog
------------------

Okay, We are able to have many open sockets, but your kernel has enough queue size to accept them? By
default, linux kernel has very small queue for connections:

.. code-block:: console

    [5.0.2]root@niwi:~niwi# sysctl net.core.somaxconn
    net.core.somaxconn = 128

For heavy load web server, this is a very bad configuration. 65536 is a possible good value for
this kernel parameter.

.. code-block:: sysctl

    # sysctl.conf
    net.core.somaxconn=65536

    # other minor tuning
    net.core.netdev_max_backlog=2500
    net.ipv4.tcp_max_syn_backlog=2500
    net.ipv4.tcp_keepalive_time=300

Additionally, you can enlarge local port range:

.. code-block:: sysctl

    # sysctl.conf
    net.ipv4.ip_local_port_range=1024 65535


Related links
-------------

* http://itresident.com/nginx/nginx-and-php-fpm-for-heavy-load-wordpress-web-server-with-high-traffic-2000-concurrent-connections/
* http://nichol.as/benchmark-of-python-web-servers

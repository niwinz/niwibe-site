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
1024 file descriptors. To accept many requests, we need to modify this parameter on both: nginx and
linux kernel.

For modify the limit of fd for a users, your need modify ``/etc/security/limits.conf`` file, and add
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

In rare cases, the kernel has a hard limit for open files, and, if you put open file number hight of
kernel hight limit, you need increase kernel limit midifying ``fs.file-max``.

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
    worker_processes 4;
    pid /var/run/nginx.pid;

    events {
        worker_connections 4069;
    }

    # [...]


Connection backlog
------------------

Okay, We are able to have many open sockets, but your kernel has enough queue to accept them? By
default, linux kernel has very small queue for connections.

.. code-block:: console

    [5.0.2]root@niwi:~niwi# sysctl net.core.somaxconn
    net.core.somaxconn = 128

For heavy load web server, this is a very bad configuration.

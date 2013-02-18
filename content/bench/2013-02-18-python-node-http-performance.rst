Python and Node performance tests
#################################

:tags: python, wsgi, nodejs

This is another benchmark for view performance of python on the web. The main idea is
to see python3 performance compared to python2 serving simple wsgi app.

Also compared with nodejs performance, performing the same task.

For benchmarks are used these software:

- uwsgi-1.4.5 + python-3.3.0
- uwsgi-1.4.5 + python-2.7.3
- gunicorn-0.17.2 + python-3.3.0
- gunicorn-0.17.2 + python-2.7.3
- nodejs-v0.8.19 + v8-3.16.4.1


Setup environment
-----------------

This is a script used on python benchmarks:

.. code-block:: python

    from __future__ import unicode_literals

    def u(data):
        return data.encode("utf-8")

    def common_response():
        for x in range(100):
            yield u("text:item:{0}".format(x*2))

        data = []
        for item in range(100):
            if item % 2 == 0:
                data.append("other:item.{0}".format(item))
            else:
                for subitem in range(item):
                    data.append("other:subitem.{0}".format(subitem))

        yield u("\n".join(data))

    def application_py2(environ, start_response):
        start_response(b'200 OK', [(b'Content-Type', b'text/plain')])
        return common_response()

    def application_py3(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return common_response()


And this is a code used with nodejs:

.. code-block:: javascript

    var http = require('http');
    var server = http.createServer(function (request, response) {
        response.writeHead(200, {"Content-Type": "text/plain"});

        for(var i=0; i<100; i++) {
            response.write("text:item:" + i);
        }

        var data = [];
        for(var i=0; i<100; i++) {
            if (i % 2 == 0) {
                data.push("other:item." + i)
            } else {
                for(var x=0; x<i; x++) {
                    data.push("other:subitem." + x)
                }
            }
        }

        response.end(data.join("\n"))
    });

    server.listen(8001);


Server setup
------------

There are a list of a commands used to start wsgi and nodejs servers.

**Gunicorn + Python3**

.. code-block:: console

    gunicorn -b 0.0.0.0:8001 -w1 app:application_py3


**Gunicorn + Python2**

.. code-block:: console

    gunicorn -b 0.0.0.0:8001 -w1 app:application_py2


**uWsgi + Python3**

.. code-block:: console

    uwsgi-py3 --http 0.0.0.0:8001 --master -p 1 -w app:application_py3 -L


**uWsgi + Python2**

.. code-block:: console

    uwsgi --http 0.0.0.0:8001 --master -p 1 -w app:application_py2 -L

**NodeJS**

.. code-block:: console

    node app.js


Benchmark
---------

For measure the performance, I used apache bench tool (ab) and httperf, with 1, 5 and 10 concurrent
clients making 1000 requests with keep-alive enabled.

**Note:** The results are average of multiple executions.


Req/s performance
^^^^^^^^^^^^^^^^^

================ =========== =========== ===========
Server           1 client    5 clients   10 clients
================ =========== =========== ===========
uWsgi+python3    235/s       315/s       323/s
uWsgi+python2    155/s       185/s       186/s
gunicorn+python3 137/s       137/s       137/s
gunicorn+python2 130/s       135/s       135/s
nodejs           330/s       375/s       375/s
================ =========== =========== ===========


Latency
^^^^^^^

================ =========== =========== ===========
Server           1 client    5 clients   10 clients
================ =========== =========== ===========
uWsgi+python3    4ms         15ms        30ms
uWsgi+python2    6ms         27ms        50ms
gunicorn+python3 7ms         35ms        72ms
gunicorn+python2 8ms         36ms        73ms
nodejs           2ms         13ms        27ms
================ =========== =========== ===========

**Note:** Additionally I've tested both: uwsgi with python3 and nodejs with a more clients
and its scales proportionally wery well, accepting same number requests per seconds and
increasing a response latency without any errors (tests up to 400 concurrent clients).


Conclusion
----------

What I really wanted to see here is if python3 is a viable option for web and deny all of
the myths that python3 is slow.

With respect to the application server, uwsgi is clearly faster. I am sure that if testing it
in a more powerful environment, could be on par with nodejs performance.

In these tests nodejs clearly has better performance, but as Guido says, performance is
not always the most important.

I usually use gunicorn for its simplicity and simplicity. Gunicorn is not the fastest,
but in my opinon, in real applications, there are other major bottlenecks to solve,
before noting the bottleneck in wsgi server.

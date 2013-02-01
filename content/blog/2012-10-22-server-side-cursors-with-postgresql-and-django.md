Title: Server side cursors with PostgreSQL and Django.
Tags: postgresql, django

By default on using ``postgresql_psycopg2`` backend, when a database query is executed, the ``psycopg2.cursor`` usually fetches all the records returned by the backend, transferring them to the client process. If the query returned an huge amount of data, a proportionally large amount of memory will be allocated by the client.

If the dataset is too large to be practically handled on the client side, it is possible to create a server side cursor. Using this kind of cursor it is possible to transfer to the client only a controlled amount of data, so that a large dataset can be examined without keeping it entirely in memory.

Server side cursor are created in PostgreSQL using the DECLARE command and subsequently handled using MOVE, FETCH and CLOSE commands.

[djorm-ext-core][1] module contains a simple integration (as python context manager) of server side cursors with django.

Here is an example of use:

    :::python
    from django.db import transaction
    from django.views.generic import View
    from djorm_core.postgresql import server_side_cursors

    class SomeView(View):
        @transaction.commit_on_success
        def get(self, request):
            with server_side_cursors(itersize=100):
                for item in Model.objects.all():
                    process_item(item)

            # [...]

All queries executed within a context manager creates new database level cursor insteand of fetching all amount of data to client side.

In order to work, you have to add ``djorm_core.postgresql`` to ``INSTALLED_APPS`` in your settings.py

You can install it with ``pip install djorm-ext-core``


#### Links ####

* <https://github.com/niwibe/djorm-ext-core>

[1]: https://github.com/niwibe/djorm-ext-core

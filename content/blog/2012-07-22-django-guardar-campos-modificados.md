Title: Django - ORM - Especificar que campos guardar al llamar `save()`
Tags: django, orm, python

Hasta ahora, al de ejcutar `save()`, de una instancia de modelo de django, se lanzaba una sentencia update para todos los campos que el modelo tiene definido. Esto realmente es poco eficiente, sobretodo si solo has modificado un campo concreto.

En la proxima version de django (1.5) se añade un parametro adicional al `save()`, que permite especificar que campos guardar. Posibilitando así un guardado mas eficiente.

Ejemplo:

    :::python
    instance = SomeModel.objects.get(pk=1)
    instance.name = u'Foo'
    instance.save(update_fields=['name'])

Adicionalmente, se espera que para django 1.5 tengamos la integracion de esta "feature" con las consultas hechas con `defer()` o `only()`.

Ejemplo:

    :::python
    instance = SomeModel.objects.only('name').get(pk=1) 
    instance.name = u'Foo'
    instance.save()

Este ejemplo, con la version 1.4 de django, ejecutaría N consultas adicionales, como campos diferidos haya y luego guardara todo en una sentencia `UPDATE`. La idea  del parche que esta a punto de entrar al core de django, es que al guardar los datos con campos diferidos, es que solo se guarden los datos disponibles, sin tocar los campos diferidos. Así evitando las innecesarias consultas adicionales.

#### Enlaces ####

<https://docs.djangoproject.com/en/dev//ref/models/instances/#specifying-which-fields-to-save>


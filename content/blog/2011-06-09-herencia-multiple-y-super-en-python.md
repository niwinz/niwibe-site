Title: Herencia multiple y super() en python
Tags: python

Se que hay mucha polemica y muchos debates respeto a la herencia multiple, algunos estan a favor y otros como lo mas habitual, en contra. Seguramente todos tendran sus razones, todas dignas de ser tomadas en cuenta. La principal critica es que incorpora una complejidad al lenguaje y como tratar las ambiguedades, ademas de que cada lenguaje lo hace a su manera.

Pero en este caso estamos hablando de python, y a mi parecer, no lo hace tan mal, si no al reves, creo que resuelve este tema con bastante elegancia (casi igual que perl). En mi opinion creo que el tema de ambiguedades, diferencias de las clases y la complejidad que comporta, es dependiente del desarrollador, y no 100% de la forma en la que el lenguaje resuelve este tema.

Este articulo en realidad no viene a habalar de la herencia multiple en si, ni generar debates ni polemicas, si no que explicar por encima de como lo tiene implementado python y como aprovecharla mediante la funcion super().

#### ¿Como funciona? ###

La herencia multiple en python se define como una lista de superclases, ordenada con una especie de algoritmo por orden de profundidad y ejecuta el primer metodo que encuentra. Para la curiosidad, esta lista se encuentra guardada en la propiedad __mro__ de la clase.

¿Si ejecuta el primer metodo que encuentra, que pasa con los metodos padres si es que existen?, pues es bastante facil, aqui es donde entra en juego super(). Su funcion principal es ejecutar el metodo padre.


#### Ejemplo 1 ####

Para ver el funcionamiento basico de super(), puede observar el ejemplo1, el cual contiene 2 clases que imprimen su nombre, y ejecutan el metodo __init__ padre. En la lista de __mro__ como ya dije anteriormente, podemos observar el orden de prioridad/profundidad con las que se va ir ejecutando los metodos de las superclases.

    :::python
    # -*- coding: utf8 -*-

    class A(object):

        def __init__(self):
            print "A"
            super(A, self).__init__()

    class B(A):
        def __init__(self):
            print "B"
            super(B, self).__init__()

    print "__mro__:", [x.__name__ for x in B.__mro__]
    instance = B()


Y la salida de este ejemplo es:

    :::console
    [3/4.3.11]niwi@vaio:~/doc.herencia.multiple> python2 example1.py
    __mro__: ['B', 'A', 'object']
    B
    A



#### Ejemplo 2 ####

En este ejemplo veremos un poco mas de complejidad, utilizando ya lo que tenemos del codigo anterior y añadimos 2 clases mas. Una que herede de A que la llamaremos C y otra que herede de B y C que la llamaremos D. Aqui es donde podremos ver en accion de como python maneja la herencia multiple. Como ya mencione en la introduccion, es bastante simple: primero ejecuta todas las superclases de primer nivel de profundidad y luego ejecuta el segundo nivel asi llegando hasta el final que es object.

Esto ultimo que acabo de contar funciona cuando tenemos una especie de rombo de dependencia, en otros casos pasa algo diferente que lo veremos en otros ejemplos.

Una cosa que tenemos que darnos cuenta, y si es que si muchas superclases de primer nivel heredan de una superclase del segundo nivel, solo se ejecutara una vez. Para verlo mas claro, mire ele ejemplo2.

    :::python
    # -*- coding: utf8 -*-

    class A(object):
        def __init__(self):
            print "A"
            super(A, self).__init__()

    class B(A):
        def __init__(self):
            print "B"
            super(B, self).__init__()

    class C(A):
        def __init__(self):
            print "C"
            super(C, self).__init__()

    class D(C,B):
        def __init__(self):
            print "D"
            super(D, self).__init__()


    print "__mro__:", [x.__name__ for x in D.__mro__]
    instance = D()


Y la salida de este ejemplo es:

    :::console
    [3/4.3.11]{2}niwi@vaio:~/doc.herencia.multiple> python2 example2.py
    __mro__: ['D', 'C', 'B', 'A', 'object']
    D
    C
    B
    A


#### Ejemplo 3 ####

Una vez comprendidos los ejemplos anteriores, vamos a ver que pasa cuando a la clase D añadimos otra superclase, pero que esta vez esa superclase herede de otro objeto de segundo nivel, como podria ser el mismo object.

El funcionamiento, se puede deducir a simple vista, pero intentare explicarlo. El algoritmo que usa python, analiza el primer nivel y lo agrupa por la superclase de segundo nivel. Si nos encontramos en el caso del ejemplo 2, vemos que C y B heredan de una sola superclase que es A, entonces, el procedimiento es ejecutar C, B y luego A, pero en el caso de C y B heredaran de una superclase diferente el orden seria por profundidad. Es decir Que ejecutaria el __init__ de la superclase C y luego la superclase de la que hereda C, seguido de __init__ de B que a su vez ejecutaria el __init__ de la superclase de B.

Para ver con claridad, he creado una clase Z que deriba de object y la he añadido como superclase a D, a continuacion puede ver el codigo final y su ejecucion para que pueda ver con mas claridad el funcionamiento:

    :::python
    # -*- coding: utf8 -*-

    class A(object):
        def __init__(self):
            print "A"
            super(A, self).__init__()

    class B(A):
        def __init__(self):
            print "B"
            super(B, self).__init__()

    class C(A):
        def __init__(self):
            print "C"
            super(C, self).__init__()

    class Z(object):
        def __init__(self):
            print "Z"
            super(Z, self).__init__()

    class D(C,B,Z):
        def __init__(self):
            print "D"
            super(D, self).__init__()

    print "__mro__:", [x.__name__ for x in D.__mro__]
    instance = D()

Y la salida de este ejemplo es:

    :::console
    [3/4.3.11]niwi@vaio:~/doc.herencia.multiple> python2 example3.py
    __mro__: ['D', 'C', 'B', 'A', 'Z', 'object']
    D
    C
    B
    A
    Z

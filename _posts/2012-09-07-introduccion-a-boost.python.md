---
layout: post.html
title: Introduccón a boost::python con python3
tags: [python python3 metaprogramming]
---


Hay varias maneras de extender python con lenguajes de mas bajo nivel (C / C++). Entre ellas la oficial, con la api de C estandar. Tambien existen alternativas como cython que permiten traducir código python a C (para mas información mirar la documentación oficial).

La idea de este articulo (igual, posteriormente algunos mas) es explicar como crear módulos en C++ para python3 con una api simple y no intrusiva, gracias a [Boost::Python](http://www.boost.org/doc/libs/1_51_0/libs/python/doc/).

## Ejemplo 1: exponer una función c++ a python.

Como no, la mejor manera de enseñar como funcionan las cosas que con un buen ejemplo. Como dice bien el titulo, la idea principal es exponer una función en C++ a python y usarla desde python.


~~~ { cpp }
#include <boost/python.hpp>
#include <boost/lexical_cast.hpp>

using boost::lexical_cast;
namespace py = boost::python;

std::string to_str(int x) {
    return lexical_cast<std::string>(x);
}


/*
 * Macro de Boost::Python que expone el modulo
 * de python con los metodos que nosotros especificamos
*/

BOOST_PYTHON_MODULE(example1) {
    py::def("to_str", to_str);
}
~~~

Colocamos esto, por ejemplo en `example1.cpp`, y lo compilamos. Nota, en este tutorial se utiliza `clang++` como compilador por defecto, si desea utilizar gcc, las diferencias deben ser mínimas en lo que se refiere a la instrucción que hay que ejecutar para compilar el modulo.

    clang++ -std=c++11 example1.cpp -shared -o example1.so -l boost_python3 -I /usr/include/python3.2mu -fpic

Luego, para probar el modulo, podemos utilizar el siguiente código python como ejemplo:

~~~ { python3 }

import example1

result = example1.to_str(2)
print(type(result), result)
~~~

Y obtenemos el siguiente resultado:

~~~
[3/5.0.0]niwi@niwi:~/tmp> python3 example1.py
<class 'str'> 2
~~~

Como se ha visto, exponer una función de c++ a python es trivial, si es muy util si tenemos calculos complicados que puedan rendir mejor si estubieran en C++ y el resto de logica menos importante en python. Permite de una manera simple transladar ciertas partes criticas a un lenguaje de mas bajo nivel.


## Ejemplo 2: exponer una simple clase.

Una vez visto el trivial ejemplo de como exponer una simple funcion, vamos a dar un paso mas y exponer una clase de C++ con sus metodos y atributos.

~~~ { cpp }
#include <boost/python.hpp>
#include <boost/lexical_cast.hpp>

namespace py = boost::python;

class Person {
public:
    Person() { Person("Unnamed"); };
    Person(std::string name): full_name(name) {}

    void set_name(std::string name) {
        this->full_name = name;
    }

    std::string get_name() {
        if (this->visible) {
            return this->full_name;
        } else {
            return std::string("Anonymous");
        }
    }

    void set_visibility(bool value) {
        this->visible = value;
    }

    bool get_visibility() {
        return this->visible;
    }

private:
    std::string full_name;
    bool visible = true;
};

BOOST_PYTHON_MODULE(example2) {
    py::class_<Person>("Person")
        .def(py::init<std::string>())
        .def("set_visibility", &Person::set_visibility)
        .add_property("full_name", &Person::get_name, &Person::set_name)
        .add_property("visibility", &Person::get_visibility);
}
~~~

Puede compilar este modulo igual que el primer ejemplo, solo cambiando el nombre de fichero del código fuente. Ahora probaremos el modulo con el siguiente código python:

~~~ { python3 }
import example2

p = example2.Person("Andrey")
print(p.full_name)

p.full_name = "Andrey Antukh"
print(p.full_name, p.visibility)

p.set_visibility(False)
print(p.full_name, p.visibility)
~~~

Con un resultado de la ejecucion:

    [3/5.0.0]niwi@niwi:~/tmp> python3 example2.py
    Andrey
    Andrey Antukh True
    Anonymous False

Para entender un poquito, aun que creo que se entiende solo con ver el ejemplo, voy a explicar un poco las partes que componen el bloque de la macro de boost::python.Para empezar tenemos `py::class_<>` con la que indicamos que queremos exponer la clase, y con el nombre tal. Ademas podemos pasarle como segundo argimento la función `py::init<>`  para especificarle el constructor por defecto. Como en este caso no le pasamos, el usa el por defecto, es decir el que no requiere ningun argumento.

A continuacion, se definen las funciones miembro de la clase que se quiere exponer mediante el metodo `py::def`, esto es igual que el primer ejemplo solo que con la variación de que tiene que exponer un metodo miembro de una clase y no una simple funcion. Y luego, por ultimo tenemos `add_property` con la que podemos añadir propertyes de clases de python con un setter y un getter. Si omitimos el setter, la property queda en modo solo lectura.

Existen otros metodos para exponer atributos publicos directamente sin seters y getters, y otras muchas opciones que pueden ser consultado en la documentación oficial.


Con esto termina esta parte, y en un futuro veo de continuar explicar mas detalles de `Boost::Python` en otros articulos, esto es igual que el primer ejemplo solo que con la variación de que tiene que exponer un metodo miembro de una clase y no una simple funcion. Y luego, por ultimo tenemos `add_property` con la que podemos añadir propertyes de clases de python con un setter y un getter. Si omitimos el setter, la property queda en modo solo lectura.

Existen otros metodos para exponer atributos publicos directamente sin seters y getters, y otras muchas opciones que pueden ser consultado en la documentación oficial.


Con esto termina esta parte, y en un futuro veo de continuar explicar mas detalles de `Boost::Python` en otros articulos.

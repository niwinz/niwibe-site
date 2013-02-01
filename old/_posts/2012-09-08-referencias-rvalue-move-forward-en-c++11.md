---
layout: post.html
title: Refernecias rvalue de C++11 e introducción a std::move y std::forward.
tags: [cpp, cpp11]
---

Es algo abitual en programación usar parametros por referencia, en c++ las que habia hasta ahora son las que se llaman las referencias lvalue, y en C++11 se han introducido un tipo nuevo de referencias, las que llaman rvalue.

NOTA: hay que decir la que estas referencias se han implementado en todos los compiladores modernos mucho antes de que se haya finalizado el TR1.

Las referencias lvalue se forman poniendo `&` despues del tipo:

~~~ { cpp }
T t;
T& other_t = t // referencia lvalue
~~~

Y las referencias rvalue se forman poniendo `&&` despues del tipo:

~~~ { cpp }
T t;
T&& other_t = t // referencia rvalue
~~~

Tienen un comportamiento muy parecido a lvalue aun que no identico y se ha introduciodo por varios propositos, entre los cuales esta el evitar copias innecesarias y/o exhaustivas de memoria alojada dinamicamente.

## std::move

~~~ { cpp }
template <class T> swap(T& a, T& b)
{
    T tmp(a);   // Ahora tenemos dos copias de a
    a = b;      // Ahota tenemos dos copias de b
    b = tmp;    // Y ahora tenemos dos copias de tmp (tmp == a)
}
~~~

Vemos que se realizan una cantidad inmensa de copias solo para intercambiar 2 valores. Para evitar esto, se ha introducido la función `std::move`, que basicamente lo que hace es obtener la referencia rvalue a partir de un lvalue. Entonces, convertimos el ejemplo de antes, usando `std::move`:

~~~ { cpp }
template <class T> swap(T& a, T& b)
{
    T tmp(std::move(a));
    a = std::move(b);
    b = std::move(tmp);
}
~~~

En este ultimo ejemplo, se crea una variable temporal `tmp` en que guardamos el contenido de la `a`, sin copiarlo, sino moverlo. Despues se mueve el contenido de `b` a `a`. Y finalizando mueve el contenido de `tmp` a `b`. Asi evitando por completo las copias innecesarias.

## std::forward

Otra función que se ha introducido con C++11, y basicamente tiene un proposito: pasar el argumento de una función a otra tal cual como te viene. Es decir, si viene rvalue pues lo pasa como rvalue, si viene lvalue, lo pasa como lvalue...

Un ejemplo igual puede aclarar mejor el funcionamiento:

~~~ { cpp }
#include <iostream>
#include <memory>
#include <utility>
#include <string>

struct A {
    A(std::string &&n) {
        std::cout << "rvalue overload, s=" << n << "\n";
    }

    A(const std::string &n) {
        std::cout << "lvalue overload, s=" << n << "\n";
    }
};

template<class T, class U>
std::unique_ptr<T> make_unique(U&& u) {
    // Descomentar esta sentencia y veis la diferencia.
    // return std::unique_ptr<T>(new T(u));
    return std::unique_ptr<T>(new T(std::forward<U>(u)));
}

int main()
{
    // Parametro explicito con referencia rvalue (solo en C++11)
    std::cout << "************************" << std::endl;
    std::unique_ptr<A> p1 = make_unique<A>("1"); // rvalue

    // Parametro explicito con referencia lvalue, eso es
    // debido a que se ha declarado un temporal explicito en el
    // ambito de ejecucion.
    std::cout << "************************" << std::endl;
    std::string s = "2";
    std::unique_ptr<A> p2 = make_unique<A>(s); // lvalue

    // Uso de std:move para obtener la referencia rvalue a partir
    // de una referencia lvalue.
    std::cout << "************************" << std::endl;
    std::string m = "3";
    std::unique_ptr<A> p3 = make_unique<A>(std::move(m)); //rvalue
}
~~~

Una vez compilado con:

    clang++ -std=c++11 test-forward.cpp -o test-forward

Obtenemos el siguiente resultado:

    [3/5.0.0]niwi@niwi:~/tmp> ./test-forward
    ************************
    rvalue overload, s=1
    ************************
    lvalue overload, s=2
    ************************
    rvalue overload, s=3

Vemos que en primer caso, no creamos ninguna variable temporal si no que pasamos el contenido tal cual a la función `make_unique<T>()`, esto por definición es un rvalue y se pasa tal. El segundo caso, creamos un temporal y lo pasamos como parametro, en este caso por definición es una referencia lvalue. Y aqui el caso que creo que es mas relevante: usando la función `std::move` creamos una referencia rvalue a partir de la variable temporal y la pasamos como parametro.

En este ultimo caso si no usaramos `std::forward` el parametro llegaria como una referenca lvalue al constructor de `A`.

Hay que tener en mente que, el ultimo caso pasa la referencia rvalue, es decir que si la función modifica esa referencia, esa misma puede apuntar hacia otro sitio y tener comportamientos inesperados.

~~~ { cpp }
#include <iostream>
#include <memory>
#include <utility>
#include <string>
#include <vector>

int main()
{
    std::vector<std::string> v;
    std::string s1 = "Hello";
    std::string s2 = "Goodbye";

    v.push_back(s1);
    v.push_back(std::move(s2));

    std::cout << "s1 after .push_back == '" << s1 << "'" << std::endl;
    std::cout << "s2 after .push_back == '" << s2 << "'" << std::endl;
    std::cout << "v = [ '" + v.at(0) << "', '" <<  v.at(1) << "']" << std::endl;
}
~~~

Lo compilamos con:

    clang++ -std=c++11 test-move.cpp -o test-move

Y el resultado de ejecucion, obtendriamos la siguiente salida:

    [3/5.0.0]niwi@niwi:~/tmp> ./test-move
    s1 after .push_back == 'Hello'
    s2 after .push_back == ''
    v = [ 'Hello', 'Goodbye']

Vemos, como el contenido de s2 quedo como una cadena vacia despues de pasarlo como rvalue a `vector.push_back()`.

Con esto doy por concluida una pequeña introducción a las referencias rvalue. En los enlaces de abajo, podeis encontrar mas explicaión y mas ejemplos.


### Referencias ###

* http://www.artima.com/cppsource/rvalue.html
* http://blogs.msdn.com/b/vcblog/archive/2009/02/03/rvalue-references-c-0x-features-in-vc10-part-2.aspx

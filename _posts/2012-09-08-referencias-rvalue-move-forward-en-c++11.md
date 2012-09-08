---
layout: post.html
title: Refernecias rvalue de C++11 e introducción a std::move y std::forward.
tags: [freebsd, linux, gpt]
---

Es algo abitual en programacion usar parametros por referencia, en c++ las que habia hasta ahora son las que vamos a llamar las referencias lvalue, y en C++11 se han introducido un tipo nuevo de referencias, las que llaman rvalue.

La razon de las referencias rvalue es para basicamente para evitar copias profundas innecesarias.

    template <class T> swap(T& a, T& b)
    {
        T tmp(a);   // Ahora tenemos dos copias de a
        a = b;      // Ahota tenemos dos copias de b
        b = tmp;    // Y ahora tenemos dos copias de tmp (tmp == a)
    }

Vemos que se realizan una cantidad inmensa de copias solo para intercambiar 2 valores. Para evitar esto, se ha introducido la funcion `std::move`, que basicamente lo que hace es obtener la referencia rvalue a partir de un lvalue. Entonces, convertimos el ejemplo de antes usando `std::move`:

    template <class T> swap(T& a, T& b)
    {
        T tmp(std::move(a));
        a = std::move(b);
        b = std::move(tmp);
    }

En este ultimo ejemplo, se crea una variable temporal `tmp` en que guardamos el contenido de la `a`, sin copiarlo sino, moverlo. Despues se mueve el contenido de `b` a `a`. Y finalizando moviendo el contenido de `tmp` a `b`. Asi evitando por completo las copias innecesarias.


http://www.artima.com/cppsource/rvalue.html
http://blogs.msdn.com/b/vcblog/archive/2009/02/03/rvalue-references-c-0x-features-in-vc10-part-2.aspx

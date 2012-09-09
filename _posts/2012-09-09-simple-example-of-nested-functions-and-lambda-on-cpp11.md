---
layout: post.html
title: Nested functions and lambdas on C++11
tags: [cpp, cpp11]
---

With dynamic languages like Python, Ruby and javascript, we are quite used to the fact that a function can return another function defined within the first (which by definition is called nested function or closure). We are also accustomed to using Anonymos blocks of code, or lambdas ie. 

Concepts are quite common in dynamic languages but I think in languages like C++ are not as known.

In c++11 lambdas have been introduced. And thanks to the boost library that allows us to define types of functions. Here's an example of a function that returns another function, depending on some parameter:

~~~ { cpp }
#include <boost/function.hpp>
#include <string>

typedef boost::function<int (int x, int y)> nested_function;

nested_function get_function(std::string &&name) {
    // Unnecesary but usefull for this example, constant
    // defined under get_function scope
    const int somme_nested_modificator = 2;

    if (name == "sum") {
        // return dynamically defined lambda function
        return [somme_nested_modificator](int x, int y) {
            return somme_nested_modificator + x + y;
        };
    }

    throw std::runtime_error("Method not found");
}
~~~

Basically we define the type of function that will return and then return a lambda that depends on the parameter name. Here the example of use:

~~~ { cpp }
int main() {
    nested_function sum_function = get_function("sum");
    std::cout << "Sum: " << sum_function(2,4) << std::endl;
    return 0;
}
~~~

Output:

~~~
[3/5.0.0]niwi@niwi:~/tmp> clang++ -std=c++11 test-nested-functions.cpp -o test-nested-functions     
[3/5.0.0]niwi@niwi:~/tmp> ./test-nested-functions 
Sum: 8
~~~

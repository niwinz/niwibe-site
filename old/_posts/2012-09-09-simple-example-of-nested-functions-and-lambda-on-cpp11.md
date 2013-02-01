---
layout: post.html
title: Nested functions and lambdas on C++11
tags: [cpp, cpp11]
---

With dynamic languages like Python, Ruby or javascript, we are quite used to seeing a function can return another function defined within the first (which by definition is called nested function or closure). Also, we are accustomed to using Anonymos blocks of code, or lambdas ie. Concepts are quite common in dynamic languages but I think in languages like C++ are not as known.

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


Also, there are cases where they need to declare a local function and use it several times without exposing outside the current scope.

~~~ { cpp }
#include <iostream>
#include <vector>
#include <algorithm>
#include <boost/bind.hpp>

int main() {
    int sum = 0;

    // Define named lambda function
    auto greater_than = [](const int &x, const int &y) -> int {
        return x > y;
    };

    // Bind some default parameter
    auto greater_than_three = boost::bind<int>(greater_than, _1, 3);

    std::vector<int> nums = {1,2,3,4,5,6};
    std::replace_if(nums.begin(), nums.end(),  greater_than_three, 0);

    std::cout << "Results: ";
    for(auto x: nums) {
        std::cout << x  << ", ";
    }

    std::cout << std::endl;
    return 0;
}
~~~

And output is:

~~~
[3/5.0.0]niwi@niwi:~/tmp> clang++ -std=c++11 test-lambdas.cpp -o test-lambdas
[3/5.0.0]niwi@niwi:~/tmp> ./test-lambdas                                   
Results: 1, 2, 3, 0, 0, 0,
~~~


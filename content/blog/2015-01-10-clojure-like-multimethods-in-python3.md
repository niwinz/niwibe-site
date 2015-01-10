Title: Multimethods with python3
Tags: clojure, python

After using clojure for some time on my hobby projects, I find clojure's multimethods
feature really exciting. In popular words, multimethods provides "polymorphism a la carte".

I thought it was funny to try implement that using python3. Amazingly, the result seems
very expressive and maybe it is can be more flexible than singledispatch.


## Implementation details ##

Let see how it is implemented.

```python
from inspect import isclass

def isa(cls_child, cls_parent) -> bool:
    if not isclass(cls_child):
        return False

    if not isclass(cls_parent):
        return False

    return issubclass(cls_child, cls_parent)
```

The `isa` function is a helper function for safe check if one class is subclass of other, and
it is used in one of two matching search process.

Then, multimethod is implemented using a plain python class with callable interface. That additionally
exposes methods for easy register implementations using python decorator syntax.

```python
from threading import Lock
from functools import partial

class _multimethod:
    def __init__(self, dispatch):
        self.__name__ = dispatch.__name__
        self.__doc__ = dispatch.__doc__

        self._dispatch = dispatch
        self._dispatch_entries = []
        self._dispatch_cache = {}
        self._dispatch_default = None
        self._mutex = Lock()
        self._notfound = object()

    def register(self, value, func=None):
        if func is None:
            return partial(self.register, value)

        with self._mutex:
            _callable = _multimethod_callable(value, func)
            self._dispatch_entries.append(_callable)

        return self

    def register_default(self, func):
        self._dispatch_default = _multimethod_callable(None, func)
        return self

    def __call__(self, *args, **kwargs):
        self._mutex.acquire()

        # Calculate the dispatch value
        dispatch_match = self._dispatch(*args, **kwargs)

        # If a dispatch resolution is already
        # exists in cache, use it as is. It
        # just an optimization for avoid compute
        # the resoultion in each call.
        if dispatch_match in self._dispatch_cache:
            dispatch_func = self._dispatch_cache[dispatch_match]

            # Explicit release lock befor execute the method.
            self._mutex.release()
            return dispatch_func(*args, **kwargs)

        # If no resolution found on cache, start the first
        # search iteration using isa? method.
        for dispatch_func in self._dispatch_entries:
            dispatch_value = getattr(dispatch_func, "_dispatch_value", self._notfound)
            if dispatch_value is self._notfound:
                continue

            if isa(dispatch_value, dispatch_match):
                self._dispatch_cache[dispatch_match] = dispatch_func
                self._mutex.release()
                return dispatch_func(*args, **kwargs)

        # If no resolution foun on first iteration, go to
        # the second iteration using == operator.
        for dispatch_func in self._dispatch_entries:
            dispatch_value = getattr(dispatch_func, "_dispatch_value", self._notfound)
            if dispatch_value is self._notfound:
                continue

            if dispatch_value == dispatch_match:
                self._dispatch_cache[dispatch_match] = dispatch_func
                self._mutex.release()
                return dispatch_func(*args, **kwargs)

        # If we are here, so no match is found.
        self._mutex.release()
        if not self._dispatch_default:
            raise RuntimeError("No match found.")

        return self._dispatch_default(*args, **kwargs)
```

The registred functions are wrapped with simple callable class: `_multimethod_callable`.
This really can be done with adding a property to function instance directly, but I don't
like mutation.

`_multimethod_callable` is defined like this:

```python
class _multimethod_callable:
    """
    Callable wrapper. The main purpose of this
    callable container is not mutate the registered
    function in a multimethod with dispatch value.
    """
    def __init__(self, dispatch_value, func):
        self._callable = func
        self._dispatch_value = dispatch_value

    def __call__(self, *args, **kwargs):
        return self._callable(*args, **kwargs)
```

And finally, the api is exposed by simple decorator function:

```python
def multimethod(func):
    """Decorator that creates multimethods."""
    return _multimethod(func)
```

Obvioulsy, this implementation does not cover all use cases of clojure multimethods
but I think is good result for an experiment.


## Usage examples ##

As first example, we have a `say_hello` multimethod that geets dispatching by
person language.

Here a multimethod definition:

```python
@multimethod
def say_hello(person):
    return person.get("lang", "es")

@say_hello.register("es")
def say_hello(person):
    return "Hola {}".format(person["name"])

@say_hello.register("en")
def say_hello(person):
    return "Hello {}".format(person["name"])
```

And having this sample data, this is a result:

```python
person_es = {"name": "Foo", "lang": "es"}
person_en = {"name": "Bar", "lang": "en"}

print(say_hello(person_en))
print(say_hello(person_es))

# => "Hello Foo"
# => "Hola Bar"
```

Another example, uses multiple value dispatching and also has fallback implementation.

```python
@multimethod
def do_stuff(data):
    return (data.get("a"), data.get("b"))

@do_stuff.register((1,2))
def do_stuff(_):
    return "foo"

@do_stuff.register((2,2))
def do_stuff(_):
    return "bar"

@do_stuff.register_default
def do_stuff(_):
    return "baz"
```

Let see how the result of using the `do_stuff` multimethod:

```python
print(do_stuff({"a": 1, "b": 2}))
print(do_stuff({"a": 2, "b": 2}))
print(do_stuff({"a": 3, "b": 2}))

# => "foo"
# => "bar"
# => "baz"
```

## Links ##

You can found more about multimethods on clojure documentation: [http://clojure.org/multimethods](http://clojure.org/multimethods)

The complete source of this post: [https://gist.github.com/niwibe/27a91ae399e5de5dba10](https://gist.github.com/niwibe/27a91ae399e5de5dba10)

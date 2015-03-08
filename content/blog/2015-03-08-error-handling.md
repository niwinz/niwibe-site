Title: A little overview of error handling.
Tags: error, monad, clojure

In this article, I'll try to make a little overview over different "modern" approaches
for error handling and converge to one concrete, that in my opinion is the right way
to do it.

## Exceptions ##

What is an _exception_? An exception is an event that occurs during the execution of a
program that disrupts the normal flow of instructions

Is the most common and accepted way to handling errors in popular and most used languages
today is using Exceptions. _Exceptions_ as is is not a bad thing and it has great uses
cases. But in my opinion, the culture of languages that uses exceptions approach for
error handling invites to use _exceptions_ as flow control structures or label ordinary
and expected errors (such as failing open a file) as exceptional situations.

And if you look back, that approach is very similar to the hated *goto*.

```python
def read_report_file(name:str, owner:User) -> Report:
    try:
        path = os.path.join(REPORTS_DIR, name)
        file = io.open(path, "rt")
        return process_file_and_get_report(file, owner)

    except PermissionDeniend as e:
        send_notification_about_unauthorized_request(e, owner)
        raise e

    except FileNotFound as e:
        raise ReportNotFound("Report file does not exists") from e

    finally:
        file.close()
```

Having this code snippet, you can observe:

- Using exceptions violation of the "Single Responsibility Principle". By definition,
  any function using a try/catch is doing more that one thing at time: function
  logic and error handling.
- That approach also violates the open/closed principle. If you want extend error
  handling, you should touch a function code that also has domain logic.

Obviously is my opinion, not every one has the same perception when error handling
is mixed with domain logic.

Good literature about this:

- <http://250bpm.com/blog:4>
- <http://stackoverflow.com/questions/1736146/why-is-exception-handling-bad>
- <http://blogs.atlassian.com/2011/05/exceptions_are_bad/>


## Null / Optional ##

In multiple situations, return (from function or method) something that can represent
"Nothing" is more that enough.

```groovy
SoundCard soundCard = computer.getSoundCard()
```

Having this code snippet in mind, we can see that `getSoundCard` operation has two possible
states: return a sound card, or return "Nothing" in case of computed does not has a sound
card.

For this situations, different languages has different approaches. There are languages that
uses a `NULL` as value that represents "Nothing". Other languages has an special type commonly
known as `Optional<T>`, and others directly does not have `NULL`.

This is the way to do it in a classic way using java:

```java
String version = "UNKNOWN";
if (computer != null) {
    Soundcard soundcard = computer.getSoundcard();
    if (soundcard != null) {
        USB usb = soundcard.getUSB();
        if (usb != null){
            version = usb.getVersion();
        }
    }
}
```

Is clearly an approach that not scales very well. The code is already looks ugly and if
more steps will be added, the situation not will be improved.

Some languages offers sugar syntax for handling with `NULL` pointers. Here the groovy
approach for represent the same code but in more readable syntax:

```groovy
String version = computer?.getSoundcard()?.getUSB()?.getVersion();
```

And the same code using clojure:

```clojure
(some-> computer get-sound-card get-usb get-version)
```

Later, modern versions of languages start adding a special type for help handling that
situations: `Optional<T>`. Here, you can see the same example but implemented using
the _java8 optional_ type as return value:

```java
String version = computer.flatMap(Computer::getSoundcard)
                         .flatMap(Soundcard::getUSB)
                         .map(USB::getVersion)
                         .orElse("UNKNOWN");
```

It is clearly an improvement, but in my opinion, using function names like `map` or `flatMap` for
compositions like this, is not very semantic.

In summary:

- Null pointers are usually a source of much problems and should be avoided.
- Some languages has a "safe" way for handling the null pointer, with specific
  types or syntax abstractions.
- Safe helpers must be used in case you are bound to use null pointers.


## Errors as value ##

Let start with a mixed way to handle errors. Mixed approach uses something like exceptions
but instead of raising them, returns them as value.

This approach can be used in almost all languages, but some languages enforces the usage of
this approach (golang as example). And this approach has problems from both previously explained
approaches, and if a language does not have enough expressiveness, the code using this
error handling approach tends to be tricky.

Imagine that functions from previous examples, now returns a something like a tuple or
list with two values, the result and the error.

```python
def get_soundcard_usb_version(computer):
    sound_card, err = get_sound_card(computer)
    if err:
       return None, err
    usb, err = get_usb(sound_card)
    if err:
       return None, err
    version, err = get_version(usb)
    if err:
       return None, err
    return version, None
```

Like exceptions, this has mixed domain logic with constant and tedious error handling in the
same function. Then, languages of lisp family allows create some syntactic sugar, that can convert this
unexpressive code in something more expressive.

Here the code for make the syntactic abstraction in clojure:

```clojure
(defn apply-or-error [f [val err]]
  (if (nil? err)
    (f val)
    [nil err]))

(defmacro err->> [val & fns]
  (let [fns (for [f fns] `(apply-or-error ~f))]
    `(->> [~val nil]
          ~@fns)))
```

And here, the same example using above syntax sugar:

```clojure
(defn get-soundcard-usb-version
  [computer]
  (err->> computer
          get-sound-card
          get-usb
          get-version))
```

A little summary:

- If your language allows construct am expesive way to handle, this may be the most expressive one.
- This approach not uses bad practices and not uses the goto.
- Unexpressive languages like golang tends to be completely unnecessary more verbose.


## Monads as error type ##

Explaining monads I think that is completely out of scope of this article. For people that not known
the monads and related thing, in our examples it looks to be an lightweight wrapper for return
values or errors. The main difference with previous example, is that the error logic is found in
the type and not in the separate ad-hoc functions.

That approach is the most common in functional languages and haskell encourages this approach. Imagine
the previous examples, that instead of return a tuple of two values, returns a result wrapped in a
some kind of wrapper.

In this case the wrapper is a Either monad that has two constructors: Left and Right. Where Left
represents a failed operation, and Right represents a successful operation.

```haskell
getSoundCardUsbVersion computer = do
    soundCard <- getSoundCard computer
    usb <- getUsb soundCard
    version <- getVersion usb
    return version
```

This code that looks completely procedural, is completely functional and has short-circuiting
mecanism if one of the operations fails (returning a error wrapped in a Left instance).

But how it really works? It is very very simple. In previous example we have used lisp macros
for define an ad-hoc sugar syntax with ad-hoc error handling logic. In this case, the error handling
logic is defined in the type what we are using as return value: `Either`.

And the haskell do notation is a some kind of macro/sugar-syntax. The main difference with that
sugar syntax and the lisp's above one, is that the do syntax is completely generic and works
with any type that implements the Monad protocol/type.

In clojure, we also can use the monadic types for handle errors (
[cats](https://github.com/funcool/cats) library will be used in the following examples)

```clojure
(require '[cats.core as m])

(defn get-soundcard-usb-version
  [computer]
  (m/mlet [sound-card (get-sound-card computer)
           usb (get-usb sound-card)
           version (get-version usb)]
    (m/return version)))
```

That code, like the haskell one, short-circuits in case of one of operations returns a value
that can be treat as failure case.

This approach in languages like clojure, that not uses monadic error handling as default approach
may be slightly intrusive, because it obliges that all function used in mlet macro (clojure's do
notation) return always an instance of monadic type (Left or Right in this case). And is more
tedious if you are using third party libraries in your domain logic and that third party libraries
uses exceptions.

For that cases exists the *exception monad*, with little sugar syntax for wrap third party libraries
in a monadic types (wrappers). Imagine that functions used in previous examples are coming
from third party library and raises an exception in case of error.

This is the aspect of the previous example with new constrains:

```clojure
(require '[cats.core as m])
(require '[cats.monad.exception :as exc])

(defn get-soundcard-usb-version
  [computer]
  (m/mlet [sound-card (exc/try-on (get-sound-card computer))
           usb (exc/try-on (get-usb sound-card))
           version (exc/try-on (get-version usb))]
    (m/return version)))
```

You can see, that in both examples (haskell and clojure) the error handling is completely out
of domain logic.

More literature:

- <http://adambard.com/blog/acceptable-error-handling-in-clojure/>
- <http://brehaut.net/blog/2011/error_monads>
- <http://yellerapp.com/posts/2014-06-27-api-error-handling.html>
- <https://www.fpcomplete.com/school/starting-with-haskell/basics-of-haskell/10_Error_Handling>
- <http://www.lispcast.com/nil-punning>
- <http://swannodette.github.io/2013/08/31/asynchronous-error-handling/>
- <http://tersesystems.com/2012/12/27/error-handling-in-scala/>
- <http://lucumr.pocoo.org/2014/10/16/on-error-handling/>
- <http://mauricio.github.io/2014/02/17/scala-either-try-and-the-m-word.html>
- <http://danielwestheide.com/blog/2012/12/26/the-neophytes-guide-to-scala-part-6-error-handling-with-try.html>
- <http://java.dzone.com/articles/whats-wrong-java-8-part-iv>


## Summary ##

In my opinion, monads or something similar is a path for good and safe error handling that
allows focus on domain logic and not mix it with constant and tedious error handling.

With that approach you can clearly split and isolate the error handling code from your
domain logic.

This is my approach:

- Use Maybe to return optional values.
- Use Either to report expected failure.
- Use Try (Exception monad) for adapt third party libraries.
- Throw Exception to signal unexpected failure in purely functional code.

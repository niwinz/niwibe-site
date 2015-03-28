Title: Promises and ClojureScript
Tags: clojure, clojurescript

When I start developing in ClojureScript one year ago, the most adopted way to treat and compose async
computations was using _core.async_.

It is not very bad approach because _core.async_ is a great
library, but in my opion is not a good abstraction for represent a result of async computation.
An other disadvantatge of using _core.async_ instead of some promise library is that it does not
includes any facility for error handling. Something that is very habitual.

Due to no existence of well established, idionamtic, documented and high performance promise library for
clojurescript until today, I have written [promesa](https://github.com/funcool/promesa).

The _promesa_ library uses the powerful and high performan [bluebird](https://github.com/petkaantonov/bluebird/) promise library for javascript for not reinvent the wheel and exposes an idiomatic and
lighweight api for use from clojurescript.

```clojure
(-> (p/all [(do-some-async-job)
            (do-some-other-async-job)])
    (p/spread (fn [result1 result2]
                (do-stuff result1 result2)))
    (p/catch (fn [error]
               (do-something-with-error error))))
```

Other of the amazing things that _promise_ library exposes, is a way to compose async computations
that looks like sync one. If you know the ES7 async/await syntax, the _promise_ library offers
a similar syntax:

```clojure
(require '[cats.core :as m])

(defn do-stuff []
  (m/mlet [x (p/promise 1)   ;; do async operation
           _ (p/delay 1000)  ;; emulate sleep
           y (p/promise 2)]  ;; do an other async operation
    (+ x y)))                ;; do the operation with results
                             ;; of previous two async operations

(p/then (do-stuff)
        (fn [v] (println v)))
```

The result of `mlet` expression is an other promise that will be resolved with result of final
operation or rejected in case of one of its operations is rejected.

In this example, the [cats](https://github.com/funcool/cats) library is used. Is a included dependency
of the _promise_ library and you do not need include it as additional dependency.

You can read the _promise_ [documentation](http://funcool.github.io/promesa/latest/) that has a lot
of examples for almost all the things that you can do with promises.

Here some additional documentation about promises and ES7 async/await sugar syntax:

- [JavaScript Promises](http://www.html5rocks.com/en/tutorials/es6/promises/)
- [ES7 async functions](http://jakearchibald.com/2014/es7-async-functions/)
- [Taming the asynchronous beast with ES7](http://pouchdb.com/2015/03/05/taming-the-async-beast-with-es7.html)


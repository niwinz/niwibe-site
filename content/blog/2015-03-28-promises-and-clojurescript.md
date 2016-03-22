Title: Promises and ClojureScript
Tags: clojure, clojurescript

Updated: 2016-03-22

When I start developing in ClojureScript one year ago, _core.async_ was (
and surelly continues to be) the most adopted library for work with
asynchronous code.

It is not very bad approach because _core.async_ is a great library,
but in my opion is not a good abstraction for represent a result of async
computation because it does not has builtin mechanism for handling
errors.

Due to no existence of well established, documented and high performance
promise library for clojurescript until today, I have written [promesa][1].

It uses the the powerful and high performant [bluebird][2] promise library
as underlying implementation for ClojureScript and jdk8 completable futures
as underlying impl. for Clojure.

This is a quick preview of the api

```clojure
(require '[promesa.core :as p])

(->> (p/all [(do-some-async-job)
            (do-some-other-async-job)])
     (p/map (fn [[result1 result2]]
              (do-stuff result1 result2)))
     (p/err (fn [error]
              (do-something-with-error error))))
```

Other of the amazing things that _promesa_ library exposes, is the ability
to compose async computations that looks synchronous:

```clojure
(defn do-stuff
  []
  (p/alet [x (p/await (p/promise 1))   ;; do async operation
           _ (p/await (p/delay 1000))  ;; emulate sleep
           y (p/await (p/promise 2))]  ;; do an other async operation
    (+ x y)))                          ;; do the operation with results
                                       ;; of previous two async operations

(p/map #(println %) (do-stuff))
```

The result of `alet` expression is an other promise that will be resolved with result
of final operation or rejected in case of one of its operations is rejected.

This post only shows a little portion of the available api. If you want know more, the
_promesa_ [documentation][3] has a lot of examples.

[1]: https://github.com/funcool/promesa
[2]: https://github.com/petkaantonov/bluebird/
[3]: http://funcool.github.io/promesa/latest/


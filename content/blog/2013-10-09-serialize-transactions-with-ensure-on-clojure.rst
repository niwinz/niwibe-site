Serialize transaction (clojure stm) using ensure
################################################

:tags: clojure, jvm

When I looked real examples for ensure_ function, I have not found much information and I decided to investigate.

With clojure stm, when one transaction is abborted, it tries a retry commit again many times. But, some times we need
ensure serialized access to some resource (ref). **ensure** function makes this behavior.

It serializes access to ensured ref, blocking a entire transaction if you try change state of it. This is a simple
example of how changing state of some ref in one transaction blocks while other transaction ensure's it:

.. code-block:: clojure

    user=> (import java.lang.Thread)
    java.lang.Thread
    user=> (def r (ref 0))
    #'user/r
    user=> (def y (ref 0))
    #'user/y
    user=> (def f (fn [r y] (dosync (ensure r) (println @r @y) (Thread/sleep 10000) (println @r @y))))
    #'user/f
    user=> (.start (Thread. #(f r y)))
    0 0
    nil
    user=> (dosync (ref-set r 20)) ;; Blocks until dosync code block of started threads ends.
    0 0
    20

But if you change value of other ref also used in both transactions, the second transaction don't blocks:

.. code-block:: clojure

    user=> (.start (Thread. #(f r y)))
    0 0
    nil
    user=> (dosync (ref-set y 20)) ; Don't blocks
    20
    0 20
    0 20 ;; Repeated output because of one rollback and corresponding retry.


.. _ensure: http://clojure.github.io/clojure/clojure.core-api.html#clojure.core/ensure

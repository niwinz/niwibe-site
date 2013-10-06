Serialize transaction (clojure stm) using ensure
################################################

:tags: clojure

When I looked real examples for ensure_ function, I have not found much information and I decided to investigate.

Clojure STM as default behavior, when one transaccion is abborted, try retry commit again a transaction. But some times
we need directly blocks other concurrent access to same data (like traditional locks, but with little difference that it
blocks only if you modify a ensured **ref** insted of block unconditionally).

This is a simple example of how changing some ref in one transaction blocks while other transaction ensure's it:

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
    user=> (dosync (ref-set r 20)) ;; Blocks until dosync block of started threads ends.
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
    0 20 ;; Repeated output due to one rollback and corresponding retry.


.. _ensure: http://clojure.github.io/clojure/clojure.core-api.html#clojure.core/ensure

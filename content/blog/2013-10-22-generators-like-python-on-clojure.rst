Clojure Generators (like lazy-seq but without memory footprint)
###############################################################

:tags: clojure, jvm

Lazy sequences on clojure works very well, but it stores reference of all computed values, that
it consumes lots of memory over time of use.

Sometimes, you need iter over a lot of elements of lazy-seq but without "caching" old results. This
problem can not be solved with lazy-seq's. For it, on this post, I go to implement some prototype
that creates a generator object with desired behavior (behaves much like python generators).

As first step, create a type. For it purpose I have used defrecord, without any protocolo:

.. code-block:: clojure

    ;; Generator type, works as container
    (defrecord Generator [func res])

    ;; Low level interface for create generator from function
    (defn generator
      [^clojure.lang.IFn func]
      (Generator. (fn [& args] (func)) (atom nil)))

As second step, I have defined functions for consume data:

.. code-block:: clojure

    (defn consume-one
      "Get next number from generator."
      [^Generator i]
      (swap! (.-res i) (:func i)))

    (defn consume-n
      "Take n next numbers from generator."
      [^Integer n, ^Generator i]
      (for [_ (range n) :let [rs (consume-one i)]] rs))


This is a sample example of use it:

.. code-block:: clojure

    (require '[generators.core :as iter])
    (def i (iter/generator (fn [] (rand-int 200))))
    ;; -> #generators.core.Generator{:func #<core$generator$fn__1210 generators.core$generator$fn__1210@44e69580>, :res #<Atom@1d01e16c: nil>}

    (iter/consume-one i)
    ;; -> 32

    (iter/consume-n 20 i)
    ;; -> (195 177 182 89 13 95 40 62 98 193 179 158 197 186 154 137 96 33 138 189)



Also, we can emulate behavior of `clojure.core/iterate` with this code:

.. code-block:: clojure

    (defn iterate
      "Same as clojure.core/iterate but returns Generator
      instance instead of lazy-seq"
      [^clojure.lang.IFn func, initial]
      (let [state (atom initial)
            wfunc (fn [] (swap! state (fn [& args] (func @state))))]
        (generator wfunc)))

    (iter/consume-n 10 (iter/iterate inc 2))
    ;; -> (3 4 5 6 7 8 9 10 11 12)



This is a complete code:

.. code-block:: clojure

    (ns generators.core
      (:refer-clojure :exclude [next take last iterate])
      (:gen-class))

    (defrecord Generator [func res])

    (defn generator
      [^clojure.lang.IFn func]
      (Generator. (fn [& args] (func)) (atom nil)))

    (defn consume-one
      "Get next number from generator."
      [^Generator i]
      (swap! (.-res i) (:func i)))

    (defn consume-n
      "Take n next numbers from generator."
      [^Integer n, ^Generator i]
      (for [_ (range n) :let [rs (consume i)]] rs))

    (defn iterate
      "Same as clojure.core/iterate but returns Generator
      instance instead of lazy-seq"
      [^clojure.lang.IFn func, initial]
      (let [state (atom initial)
            wfunc (fn [] (swap! state (fn [& args] (func @state))))]
        (generator wfunc)))

##########################
Auto currying with clojure
##########################

:tags: clojure, lisp

Currying, is one of the much others featues that haskell implements nativelly but
is not widelly extended on lisp like languages. But thanks to the power of lisp,
it should be possible to extend the language so that is able to support autocurry.

This is my simple experiment using clojure macros for implement
autocurrying:

.. code-block:: clojure

    (defmacro defc
      [identifier bindings & body]
      (let [n# (count bindings)]
        `(def ~identifier
           (fn [& args#]
             (if (< (count args#) ~n#)
               (apply partial ~identifier args#)
               (let [myfn# (fn ~bindings ~@body)]
                 (apply myfn# args#)))))))


This is a very ugly macro that contains also ugly var names, all is so because it
was an experiment of ten minuts.

Here, a simple example using previously defined macro:

.. code-block:: clojure

   ;; Sample function with three arguments. defc works
   ;; like clojure's defn (but much less complete)
   (defc sum-three-numbers
     [num1 num2 num3]
     (+ num1 num2 num3))

   ;; Normal call, return a sum of three numbers
   (sum-three-numbers 1 2 3)
   ;; -> 6

   ;; When function is called with less arguments,
   ;; it returns a curried function.

   (sum-three-numbers 1)
   ;; -> #<core$partial$fn__4190 clojure.core$partial$fn__4190@8a20568>

   (sum-three-numbers 1 2)
   ;; -> #<core$partial$fn__4192 clojure.core$partial$fn__4192@892c746>

   ((sum-three-numbers 1) 2)
   ;; -> #<core$partial$fn__4192 clojure.core$partial$fn__4192@4be0ae98>

   (((sum-three-numbers 1) 2) 3)
   ;; -> 6

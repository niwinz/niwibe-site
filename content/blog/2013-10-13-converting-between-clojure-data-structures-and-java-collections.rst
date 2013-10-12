Converting between clojure data structures and java collections
###############################################################

:tags: clojure, jvm

In some situations you need convert some data structures of clojure (like vectors, maps or sets)
to java collections and vice versa.

This problem has simple solution: clojure data structures implements **java.util.Collection** interface
and uses it constructor for make conversion to corresponding types.

As first example, you can convert clojure vector to **java.util.ArrayList**:

.. code-block:: clojure

    (def list1 (java.util.ArrayList. [1 2 3]))
    ;; list1 -> #<ArrayList [1, 2, 3]>

    (.get list1 0)
    ;; -> 1


In same way, you can convert clojure map to **java.util.HashMap**:

.. code-block:: clojure

    (def map1 (java.util.HashMap. {"a" 1 "b" 2}))
    ;; map1 -> #<HashMap {b=2, a=1}>

    (.get map1 "a")
    ;; -> 1


For backward conver from java to clojure data, you can use **into** function:

.. code-block:: clojure

    (into [] (java.util.ArrayList. [1 2 3]))
    ;; -> [1 2 3]

    (into #{} (java.util.HashSet. #{1 2 3}))
    ;; -> #{1 2 3}

    (into '() (java.util.LinkedList. '(1 2 3)))
    ;; -> (3 2 1)

    (into {} (java.util.HashMap. {:a 1 :b 2}))
    ;; ->{:b 2, :a 1}


In clonclusion, clojure has well interoperability with java, and convert form clojure data structures to
java collections is almost transparent.

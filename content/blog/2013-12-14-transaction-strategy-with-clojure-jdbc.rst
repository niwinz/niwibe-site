Transaction strategy with Clojure JDBC
######################################

:tags: clojure, jdbc

In previous article, I have introduced a new jdbc library for clojure. On this article I want
introduce one of the new features that it have.

clojure.jdbc comes with powerful tranasaction management, in comparison with clojure.java.jdbc it,
by default, handles well subtransactions. All transaction block works as an atomic unit. But in
some cases, a uses wants relaxe this transaction management such as all nested transactions
are grouped into the first/main transaction.

Thanks to the new feauture, introduced in the last version of clojure.jdbc (0.1.0-beta4) you can
change a transaction strategy without change any other code of your application.

For show one example, we go to imitate a simple transaction management available in
clojure.java.jdbc. For it, we go to make a new implementation of ``ITransactionStrategy``
protocol available in ``jdbc`` namespace:

.. code-block:: clojure

    (defrecord BasicTransactionStrategy []
      ITransactionStrategy
      (begin [_ conn opts]
        (let [depth    (:depth-level conn)
              raw-conn (:connection conn)]
          (if depth
            (assoc conn :depth-level (inc (:depth-level conn)))
            (let [prev-autocommit-state (.getAutoCommit raw-conn)]
              (.setAutoCommit raw-conn false)
              (assoc conn :depth-level 0 :prev-autocommit-state prev-autocommit-state)))))

      (rollback [_ conn opts]
        (let [depth    (:depth-level conn)
              raw-conn (:connection conn)]
          (if (= depth 0)
            (do
              (.rollback raw-conn)
              (.setAutoCommit raw-conn (:prev-autocommit-state conn))
              (dissoc conn :depth-level :prev-autocommit-state))
            conn)))

      (commit [_ conn opts]
        (let [depth    (:depth-level conn)
              raw-conn (:connection conn)]
          (if (= depth 0)
            (do
              (.commit raw-conn)
              (.setAutoCommit raw-conn (:prev-autocommit-state conn))
              (dissoc :depth-level :prev-autocommit-state))
            conn))))

As you can see, is not very complicated. It simply consist on three methods. If you want disable completely
transaction management you can implement some dummy transaction strategy like this:

.. code-block:: clojure

    (defrecord DummyTransactionStrategy []
      ITransactionStrategy
      (begin [_ conn opts] conn)
      (rollback [_ conn opts] conn)
      (commit [_ conn opts] conn))


And this is a simple example of how you can use one of previously defined strategies on your code:

.. code-block:: clojure

    ;; Simple macro usage

    (with-connection [conn dbspec]
      (with-transaction-strategy conn (DummyTransactionStrategy.)
        (do-some-thing conn)))

    ;; Or more low level access

    (with-open [conn (-> (make-connection dbspec)
                         (wrap-transaction-strategy (BasicTransactionStrategy.)))]
      (do-some-thing conn))


You can read more about it on the `project documentation <http://niwibe.github.io/clojure.jdbc/>`_
or view a source code on `Github <https://github.com/niwibe/clojure.jdbc>`_.

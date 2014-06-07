Title: PostgreSQL json field with clojure and jdbc
Tags: postgresql, clojure, jdbc, json

PostgreSQL have awesome types like **json** or **hstore**, but how we can use them with clojure
and jdbc?

It is very simple!

**clojure.jdbc** exposes some protocols (`jdbc.types/ISQLType` and `jdbc.types/ISQLResultSetReadColumn`)
to extend user types making them compatible with jdbc in both directions.

The first handles conversion from user type to jdbc compatible type and the second handles the
backward process (from sql/jdbc type to user type).

This is a working example of implementing these protocols for json support:

```clojure
(require '[jdbc.types :as types])

;; Import class that postgresql jdbc implementation
;; uses for handle custom types.
(import 'org.postgresql.util.PGobject)

;; Json library for clojure: https://github.com/dakrone/cheshire
(require '[cheshire.core :as json])

;; ISQLType handles a conversion from user type to jdbc compatible
;; types. In this case we are extending any implementation of clojure
;; IPersistentMap (for convert it to json string).
(extend-protocol types/ISQLType
  clojure.lang.IPersistentMap

  ;; This method, receives a instance of IPersistentMap and
  ;; active connection, and return jdbc compatible type.
  (as-sql-type [self conn]
    (doto (PGobject.)
      (.setType "json")
      (.setValue (json/generate-string self))))

  ;; This method handles assignation of now converted type
  ;; to jdbc statement instance.
  (set-stmt-parameter! [self conn stmt index]
    (.setObject stmt index (types/as-sql-type self conn))))

;; ISQLResultSetReadColumn handles the conversion from sql types
;; to user types. In this case, we are extending PGobject for handle
;; json field conversions to clojure hash-map.
(extend-protocol types/ISQLResultSetReadColumn
  PGobject
  (from-sql-type [pgobj conn metadata i]
    (let [type  (.getType pgobj)
          value (.getValue pgobj)]
      (case type
        "json" (json/parse-string value)
        :else value))))
```



Now having the corresponding type extended, you should be able to use json field without any problem.
This is a little example:

```clojure
(require '[jdbc :as j])

(def dbspec "postgresql://localhost/test")

;; Creating table and inserting a new row, using clojure plain
;; hash-map as parameter without any special conversion.
(j/with-connection [conn dbspec]
  (j/execute! conn "CREATE TABLE example (data json);")
  (j/execute-prepared! "INSERT INTO example (data) VALUES (?);" [{:foo "bar"}]))

;; Now, you can query previously inserted data
(j/with-connection [conn dbspec]
   (println (-> (j/query conn "select * from example;")
                (first))))
;; => {"foo" "bar"}
```


This is a list of libraries used for this examples:

- <https://github.com/niwibe/clojure.jdbc>
- <https://github.com/dakrone/cheshire>

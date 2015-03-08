Title: Dealing with persistence with jdbc in asyncrhonous environments (with clojure)
Tags: clojure, persistence, jdbc

Is well known that in async environments, nothing can be blocking. Asynchronous environments
uses uses different approach for handling high concurrencly: instead of using a "thread per connection"
it uses a limited number of threads for handle thousands of connections, almost always with help
with an event loop for handle IO.

In that situations, making blocking operations in one thread, is more harmful. Is not same thing
block 1 of 200 threads and block 1 of 4 threads (as example).

In case of persistence and concretelly jdbc, the api is totally blocking.

The jdbc api is build with threaded environment in the mind. And very often I found people
that thinking that some part of jdbc implementation is bound to the thread. But, the only thing
that we shoult take care with jdbc and concurrency, is not using the same connection from different
threads in the same time. That operation is not safe.

The approach for handling with blocking calls in async environments is having a separate group
of workers (thread pool) for execute blocking calls, so allow to the main threads not block.

## How I have done it in suricatta? ##

Having clear the constrains, I implemented async support for _suricatta_.

[_Suricatta_](https://github.com/niwibe/suricatta) is a toolkit (build on top of fantastic
[jOOQ](http://www.jooq.org/) java library) for work with sql in clojure, that allows build, format
and execute sql. It uses jdbc in its internals.

For implement the async support in _suricatta_, two main pieces are used: agents, monads and core.async.
Agents and its internals provides a threadpool and serializable operations semantics, core.async
provides an abstraction for avoid callbacks and the _exception_ monad for error handling.

In _suricatta_, each connection maintains an agent as part of it internal state. This allows guarrantee
that all async operations over one connections are done in serializable way. Obviously, different
operations over one connection can be done in different threads (of clojure internal thread pool).
That is completelly assumable, because the safe constrain is: not use the connection from different
threads at *same time*.

Let's go to see an example:

```clojure
(require '[clojure.core.async :refer [<! go]]
         '[surricata.core :as sc]
         '[suricatta.async :as sa])

(def dbspec {:subprotocol "h2"
             :subname "mem:"})

(go
  (with-open [ctx (sc/context dbspec)]
    (let [result (<! (sa/fetch "select 1 as x;"))]
      (println "Result:" @result))))
;; => "Result:" [{:x 1}]
```

A _result_ is an instance of _exception_ monad (from [cats](https://github.com/funcool/cats) library),
if you are not familiar with monads, you can treat it as container like any ref like type in clojure
that can contain a value or an exception.

Maybe, you have an cuestion, that approach is valid for use with transactions?

The response is: *Yes*. The jdbc maintains transaction state directly in a connection, without
using something like threadlocals. There an example of use transactions in with async operations:

```clojure
(go
  (with-open [ctx (sc/context dbspec)]
    (sc/atomic ctx
      (<! (sa/execute "insert into foo (n) values (1);"))
      (<! (sa/execute "insert into foo (n) values (2);")))))
```

## Final notes ##

Clojure and clojure ecosystem comes with great abstractions for different concurrency models, and
this allows an easy way for creating an abstraction for dealing with blocking apis in asynchronous
environments.

This apporoach is not an optimization, this will not make your async api faster. It just allows
properly use jdbc persistence in you async based environments.

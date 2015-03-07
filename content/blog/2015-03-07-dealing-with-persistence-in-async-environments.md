Title: Dealing with persistence with jdbc in asyncrhonous environments (with clojure)
Tags: clojure, persistence, jdbc

Is well known that in async environments, nothing can be blocking. Asynchronous environments
uses uses different approach for handling high concurrencly: instead of using a "thread per connection"
it uses a limited number of threads for handle thousands of connections, almost always with help
with an event loop for handle IO.

In that situations, making blocking operations in one thread, is more harmful. Is not same thing
block 1 of 200 threads and block 1 of 4 threads (as example).

In case of persistence and concretelly jdbc, the api is totally blocking.

The approach for handling with blocking calls in async environments is having a separate group
of workers (thread pool) for execute blocking calls, so allow to the main threads not block.

## How it can be done? ##

The jdbc api is build with threaded environment in the mind. And very often I found people
that thinking that some part of jdbc implementation is bound to the thread.

But, the only thing that we shoult take care with jdbc and concurrency, is not using the same
connection from different threads in the same time. That operation is not safe.

*Jdbc interface is not thread safe*.


Clojure and clojure ecosystem comes with great abstractions for different concurrency models

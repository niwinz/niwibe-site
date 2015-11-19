Title: State management in ClojureScript web applications
Tags: clojure, security, auth

If you are here, probaly you know about the new trending things like relay,
falcor or om.next. In contrary to them, I'll try to explain my throughts about
state management in clojurescript web applications.


## Local state ##

The first approach that was popularized with om, was using the **cursor**
abstraction for provide a "limited" vision of global state to the subcomponents
and remove some kind of coupling. The state transformation in that approach
is usually mixed with the UI logic.

Also, the **cursor** approach has its own downslides and limitations such as
making mandatory use plain types removing the facilities such as declaring own
types and polymorphic abstractions with protocols.


### Use lenses instead of cursors ###

A good cursor replacement I think are lenses. Them provides all the good things
of cursrors but does not provides any of them downsides.

Imagine you have this state:

```clojure
(defrecord A [v])

(def state
  (atom {:items [#user.A{:v 2}
                 #user.A{:v 5}]}))
```

Now, using a lenses implementation in [cats][1] you can focus on different positions
of the datastructure:

```clojure
(require '[cats.labs.lens :as l])

(def l1 (l/focus-atom (l/in [:items 0]) state))
(def l2 (l/focus-atom (l/in [:items 0 :v]) state))

@l2
;; => 2

@l1
;; => #user.A{:v 2}
```

Also, you can apply some transformations to the focused values using the
well known atom interface:

```clojure
(swap! l2 inc)

@l2
;; => 3

@l1
;; => #user.A{:v 3}
```

You can observe that you can focus also on portion of records and apply
transformations over its values. This allows us have atom like visions of the
global state without any limitations of cursors.


### Use named state transitions ###

Instead of using adhoc state transformations in your UI related code.

This is can be done in bunch of different ways, byt my prefered approach for it
is just use a reduce function defined as multimethod for easy extensibility.

This is a little example of the multimethod aspect:

```clojure
(defmulti state-transition
  (fn [state [event param]] event))
```

It can be used in this way:

```clojure
(defmethod state-transition :index-users
  [state [_ users]]
  (letfn [(index-counter [state item]
            (assoc-in state [:users-by-id (:id item)] item))]
    (reduce index-counter state counters)))

(defmethod state-transition :set-users
  [state [_ users]]
  (-> (assoc state :users (mapv :id counters))
      (state-transition [:index-counters counters])))
```

The previous example defines a simple example for put an hipotetical
users list to the state in a denoramalized way (for easy access by id from
react components).


This is really very simple improvement but adds a lot of value in decoupling
the UI code from the domain logic in state transformations.


## Remote state ##

The most popular approach for manage and retrieve remote state at this moment
are the RESTful api's. However the unit of work of composition is slightly
inexpresive.

There are also the new approaches such as [relay][2] and [falcor][3] that are
growing in popularity that offers much rich and expresive way to define the
communication with the backend.

Independently of what approach you are using, my prefered way to access to the
remote resources should be decoupled from any framework. It should be simple
for plug for different kinds of API's or various of them behind of an uniform
data based application interface.

Let imagine we have something like this:

```clojure
(defmulti read-fn (fn [store key params] key))
(defmulti novelty-fn (fn [store key params] key))

(defonce state (atom {}))

(defonce store
  (s/store state {:read read-fn
                  :novelty novelty-fn}))
```

Do not wory about `s/store` implementation, it will be explained later, at this
moment is more important understand its purpose.

The store instance is just a wraper for your global state (and behaves like it
because it implemes the basic atom interface) that allows attach a user defined
impl to specific state.

The **read** and **novelty** concepts are self descriptive, the first one is
for retrieve data and the second is for put some transformation back to the
backend.

Let define a impl for load an hipotetical users from some kind of api:

```clojure
(require '[promise.core :as p]
         '[your.app.rest :as api])

(defmethod read-fn :load-users
  [_ _ _]
  (p/then (api/get-users)
          (fn [users]
            (swap! state-transition [:set-users users]))))
```

You can observe that the main difference of this with the previous local state
management approach is that this works with [promises][4]. The promises here are
because the communication with the potential api are surelly asynchronous.

Here is a example on how this can be consumed:

```clojure
(-> (s/read store [:load-users])
    (p/then #(println "Completed")))
```

The **s/read** function returns a promise that will be resolved when the operation
is completed. There is also **s/novelty** function for novelty events.

I think this approach allows a clear "client-server" like separation between UI
code and the state management and it is also desirable for applications that
works completly in client side.

Here an other example but using [cats alet][6] for make parallel requests:

```clojure
(require '[cats.core :as m])

(defmethod read-fn :get-user
  [_ _ id]
  (m/alet [user (api/get-user id)
           friends (api/get-friends id)]
    (assoc user :friends friends)))

;; And then:

(m/mlet [user (s/read store [:get-user 1])]
  (swap! state-transition [:add-user user]))
```

[1]: http://www.niwi.nz
[2]: http://www.niwi.nz
[3]: http://www.niwi.nz
[4]: http://www.niwi.nz
[5]: http://www.niwi.nz
[6]: http://www.niwi.nz

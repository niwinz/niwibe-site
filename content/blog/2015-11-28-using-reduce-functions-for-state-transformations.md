Title: Using reduce functions for state transformations
Tags: clojurescript, state management, state, reactjs, multimethods

Most of the times I found clojurescript web applications mixing UI code with
state transformation logic, that inherently tends to create a lot of coupling
between them.

I think that can be solved very easily using some kind of named events
instead of direct state manipulation, being in server-client like architecture
in a client only web application. And it can be approached using the clojure
multimethods for define simple and extensible interface for state transformations.

This can be the aspect of the multimethod declaration:

```clojure
(defmulti state-transition
  (fn [state [event param]] event))
```

The function receives a state as first argument and event object represented
with a vector of two elements, first the event name and the second an optional
parameters. That function can be used directly in `swap!`, that makes it
really versatile.

Imagine to have defined this state transformations:

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

You can use in this way:

```clojure
(swap! state state-transition [:set-users users])
```

You can use it just as code to execute on event handlers of the react components
or just on initialization of state.

The state transitions also can be composed easily unsing **->** theading macro:

```clojure
(defn populate-users
  [state users]
  (-> state
      (state-transition [:set-users users])
      (state-transition [:index-users users])))
```

In fact, this is not a big revolutionary idea, is just a simple one that have
worked in my case and that I hope you find it useful.

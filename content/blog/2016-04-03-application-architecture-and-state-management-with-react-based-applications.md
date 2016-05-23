Title: Application architecture and state management with react based applications.
Tags: rum, react, clojurescript, architecture
Author: Andrey Antukh

This is a brief summary of the architectural decisions that I have taken when I
have started the development of [uxbox][1] and with time I found that the result
is scaling pretty well for relatively big project, so I decided to write about it.

I will use ClojureScript as base lenguage but the main ideas explained here can
be done with plain javascript with minor adaptations.

## TL;DR ##

A quick summary of the design decisions (almost all explained in the article):

- Unidirectional state transformation flow.
- Event based system with three well defined event types: pure state transformations,
  async state transformations and side effectful actions.
- A client-server architecture on the frontend-only application with strong
  separation of logic from UI.
- FRP streams as a glue between UI and the state transformation logic.
- State modeled for fast lookup (like a database) instread of to be UI driven.


## The event system ##

Let start with the first piece: the event system. As I have said previously, there
are three different events:

- pure state transformations
- asynchronous actions that can or not be state transformations
- side effects actions

The concept of an **event** is modeled using a basic ClojureScript constructions
such are **records** for define new types and protocols for define the different
event interfaces. For understand it better, let see some code. This is how a
pure state transformation event is defined:

```clojure
(defprotocol UpdateEvent
  "Defines a simple state transformation.
  It receives a state and should return the
  transformed state."
  (-apply-update [event state]))

```

And this is how an implementation of that event will look in an hipotetical
toy project that manages one unique counter:

```clojure
(defrecord Increment [n]
  UpdateEvent
  (-apply-update [_ state]
    (update state :counter (fnil #(+ n %) 0))))

(defn increment
  "Create an instance of Increment event."
  ([] (increment 1))
  ([n] (Increment. n)))
```

If you don't need a named types, you can use `reify` for create anonymous objects,
you are not restricted to use **records**.

Evidently, for small things like this, it seems like too much boilerplate, but for
big applications having well defined events makes things more clear to understand
and allows to have the application logic encapsulated in small, testeable events.

I have said that there are three different kind of events, this is how the rest
two events can be defined:

```clojure
(defprotocol WatchEvent
  "Defines a asynchronos state transformation.
  It receives the state and the reference to the current
  stream of events and should return an other stream
  of same kind of events (that can be of `UpdateEvent`,
  `WatchEvent` or `EffectEvent`."
  (-apply-watch [event state stream]))

(defprotocol EffectEvent
  "Defines a side effectfull action.
  It receves the state and the reference to the current
  stream of events. The return value will be ignored."
  (-apply-effect [event state stream]))
```

Do not worry about them, they will be explained later with better examples.


### Stream Loop ###

In order to start playing with events, there are two additional functions,
`init` and `emit!`.

```clojure
(defonce ^:private bus (rx/bus))

(defn emit!
  "Emits an event or a collection of them."
  ([event]
   (rx/push! bus event))
  ([event & events]
   (run! emit! (cons event events))))

(defn init
  "Initializes the stream event loop and
  return a stream with model changes."
  [state]
  ;; [implementation ommited]
  ))
```

The `init` funtion just initializes something that I call
**streamloop**, it receives a initial state and returns a stream of state
transformations:

```clojure
(defn get-initial-state
  []
  {:counter 1})

(defonce stream
  (init (get-initial-state)))
```

It's responsability is pretty simple: process events and emit state snapshots after
each transformations. At this moment you should not care how `init` is implemented,
because is important to understand its purpose to be here (the complete
implementation of that is referenced on the end of this article).

And later, the `emit!` variadic function, that just does that you will expect,
emit event instances into the stream:

```clojure
(emit! (increment 1)
       (increment 1))
;; => nil
```

If we subscribe to the stream returned by `init` function before emiting any events,
we will obtain a stream of state snapshots after each applied transformation:

```clojure
(require '[beicon.core :as rx])

(rx/subscribe stream (fn [state]
                       (println "state:" state)))
;; [console] state: {:counter 1}
;; [console] state: {:counter 2}
```

Obviously, every approach has its advantages and tradeoff's. In this case the
advantadge and the tradeoff at the same time is that the state lives in the stream,
so it only can be modified emiting events.

In order to start using that state in your react based application, you have to
materialize the state to something that components can understand.

Let see a little example using rum:

```clojure
(require '[rum.core :as rum])

(defonce state (rx/to-atom stream))

(rum/defc counter < rum/reactive
  []
  (let [counter (:counter (rum/react state))
        increment #(emit! (increment 1))]
    [:div.label {:on-click increment}
     [:span counter]]))

(rum/mount (counter) js/document.body)
```

The state is materialized into atom and then used in a example rum component.

Independently of the explained tradeoff, this approach is quite flexible because
it does not dictate how you should pass the state to the UI components. In fact
this approach can be used without problems with [om][5] or [reagent][6] based
applications.


### Async state transformations & side effects ###

Pure state transformations are nice for show in examples, but real applications
are full of side effects and asynchronous stuff.

Before going deeper, let's go to see an example event using `WatchEvent` protocol.
Imagine that you need to load the counter value from some kind of backend or
database that has asynchronous interface:

```clojure
(defrecord CounterLoaded [value]
  UpdateEvent
  (-apply-update [_ state]
    (assoc state :counter value)))

(defrecord LoadCounter [path]
  WatchEvent
  (-apply-watch [_ state stream]
    (->> (http/get path)
         (rx/from-promise)
         (rx/map ->CounterLoaded))))

(defn load-counter []
  (LoadCounter. "/my/counter"))
```

As you can see, if you want to perform asynchronous stuff, you should implement
two events: one for fetch the counter and other for set it in the state.

However, the flexibility of clojurescript allows us implement the `UpdateEvent`
protocol directly to the javascript function, allowing the use of plain functions
as pure transformations event instances. So the previously code can be expressed
in this manner:

```clojure
(defrecord LoadCounter [path]
  WatchEvent
  (-apply-watch [_ state stream]
    (->> (http/get path)
         (rx/from-promise)
         (rx/map (fn [value]
                   #(assoc % :counter value))))))

(defn load-counter []
  (LoadCounter. "/my/counter"))
```

The first most common problem that you will found using this approach is: **How I
can syncronize two or more asynchronous events?**.

A good use case for the demostration purposes is: *load some data* and then
*redirect user to other page*. Using the previously defined events, let see how it
can be approached:

```clojure
(defrecord GoToCounter []
  WatchEvent
  (-apply-watch [_ state stream]
    (rx/merge
      (rx/of (load-counter))
      (->> stream
           (rx/filter #(instance? CounterLoaded %))
           (rx/map (fn [_] #(assoc % :location :counter)))))))
```

The third parameter on `-apply-watch` is a reference to the main stream where
`emit!` publish events. So you can subscribe to changes that will hapen in some
future and react in terms of them. As streams are cancellable by default, implement
something like autocompleting using this kind of constructions is quite simple.

You should expect that two events passed to `emit!` function will be processed by
the **streamloop** in order and pure state transformations will be executed in
expected order, but the operations of resulting async operations will be executed
in completly arbitrary order and the explained approach serves for
synchronize two or more asynchronous events.


## The state model ##

An other very important part of the application architecture is how you have plan
to model your state and how your components will have access to it. There
are a lot of solutions to this and I think no solution is better than another 
because everything depends on type of the application.

In my project I've taken the approach where the whole state is visible to all
components. The coupling with state problem is solved in this way:

- Small resuable components usually receives everything that they needs by
  parameters from its parent components.
- Big and/or not reusable components just access directly to the state or uses
  a [lenses][3] approach just for create a focused vision of the state.

In fact, in [uxbox][1], the direct access to the state is used in very little
portion of code and almost always [lenses][3] are used instead. Maybe you are now
asking yourself: but that is this so called **lenses**? As a very simplistic
description: lenses are the *functional* approach to focus to some portion of data
structure (tree or seequence like) for easy access to it or transform it.

The most interesting and important part is the ability to derive atoms from other
atoms:

```clojure
(require '[lentes.core :as l])

(defonce counter
  (-> (l/key :counter)
      (l/from-atom state)))
```

That allows create new derived atoms that focuses on exactly state that the
component need:

```clojure
(rum/defc counter < rum/reactive
  []
  (let [counter (rum/react counter)
        increment #(emit! (increment 1))]
    [:div.label {:on-click increment}
     [:span counter]]))
```

One of the big advantages of using lenses in reactive components is because they
**does not trigger the component rerendering** if other portion of the atom is
modified.

Also, the lenses are not limited to tree like structures, in fact you can provide
just a plain function that receives the state as first arguent and should return the
focused data. In [uxbox][1] the state is strictly organized like a database using
data normalization and indexing for fast lookup by id. Using lenses allows have
different versions of state just adapted for the UI.

An other very interesting property of lenses is that they are composable in the
same way as transducers: using plain function composition facilities such as
`comp`:

```clojure
(defonce sample-state (atom {:foo {:bar 2}}))

(defonce derived-state
  (-> (comp (l/key :foo)
            (l/key :bar))
      (l/focus-atom sample-state)))

@derived-state
;; => 2

(swap! derived-state inc)

@derived-state
;; => 3
```

Although, the derived atoms are mutable in the same way as normal atoms, the use
of the explained approach of state management they works as read-only focused values
because the main state atom is just a materialization of the state that lives in the
stream.


## Conclusion ##

This approach works pretty well in my project but I can't assure that it will fits
for other projects. Everything depends on the application that you need to build.

I think is pretty flexible, and with little modifications surelly it can work well
with different that mine (such as using [DataScript][4] for manage the state or
anything else).

## Referecences ##

- [Event System][7] implemented in uxbox.


[1]: https://github.com/uxbox/uxbox
[2]: https://github.com/tonsky/rum
[3]: https://github.com/funcool/lentes
[4]: https://github.com/tonsky/datascript
[5]: https://github.com/omcljs/om
[6]: https://github.com/reagent-project/reagent
[7]: https://github.com/uxbox/uxbox/blob/95c4f2fbc178d1e03f7765d6beae733ea8cf763b/src/uxbox/rstore.cljs

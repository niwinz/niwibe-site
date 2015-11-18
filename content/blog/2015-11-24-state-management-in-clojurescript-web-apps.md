Title: State management in ClojureScript web applications
Tags: clojure, security, auth

If you are here, probaly you know about the new trending things like relay,
falcor or om.next. In contrary to them, I'll try to explain my throughts about
state management in clojurescript web applications.


## Global state management ##

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

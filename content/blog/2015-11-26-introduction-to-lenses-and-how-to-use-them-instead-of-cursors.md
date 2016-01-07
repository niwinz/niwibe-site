Title: Introduction to lenses and how to use them instead of cursors
Tags: clojurescript, state management, state, cursors, reactjs

The cursors abstraction is so far the most used approach for delimit the vision
of the global state for react components in ClojureScript applications. But that
also has a great amount of downsides that should be considered before using it.

Here is a little list of the most important for me:

- Only works with plain data. That makes worse working with own types defined with
  **defrecord** and exploit polymorphism using **protocols**.
- Only allows visions of the tree behind the current root node.

All that downsides and surelly other that I have not mentioned here I think
can be solved replacing cursors with lenses.


### First steps with lenses ###

Lenses are in fact the generalization of the get, put and data mapping to
particular part of the data structure. The concept is very similar to the
cursors but without the main limitation of them.

The following examples we will use the latest version of [cats][1] and
if you are in repl just evaluate the following require expression:

```clojure
(require '[cats.labs.lens :as l])
```

Let see a simple example using lenses:

```clojure
(l/focus l/fst [1 2 3])
;; => 1
```

The **fst** is a predefined lense that just get the first element of the data
structure. Additionaly to simple focus operation, you can apply some operation
in place or just put a new value into that position:

```clojure
(l/over l/fst inc [1 2 3])
;; => [2 2 3]

(l/put l/fst 42 [1 2 3])
;; => [42 2 3]
```

Also, you can focus some descendent nodes of the associative data structure
in a similar way as you are doing with cursors:

```clojure
(l/focus (l/in [:a :b]) {:a {:b {:c 1 :d 2}}})
;; => {:c 1 :d 2}

(l/over (l/in [:a :b :c]) inc {:a {:b {:c 1 :d 2}}})
;; => {:a {:b {:c 2, :d 2}}}
```

Or just select some keys:

```clojure
(def lens (l/select-keys [:a :b]))

(l/focus lens {:a 1 :b 2 :c 3 :d 4})
;; => {:a 1, :b 2}

(l/over lens #(update % :a inc) {:a 1 :b 2 :c 3 :d 4})
;; => {:c 3, :d 4, :a 2, :b 2}
```

The most nice thing of the lenses implementation in [cats library][1] is that
them are implemented just using plain functions and them can be composed in the
same way as [transducers][2] using **comp**:

```clojure
(def xlens (comp l/fst (l/nth 2)))

(l/focus xlens [[1 2 3 4] [5 6 7]])
;; => 3

(l/over xlens inc [[1 2 3 4] [5 6 7]])
;; => [[1 2 4 4] [5 6 7]]
```

### Lenses as cursors replacement ###

The clojurescript applications usually uses a unique global state atom for store
the entire app state and use cursors for provide a limited vision of the tree.

The [cats library][1] also comes with facilities to create a focused atoms with
lenses. Imagine you have this state:

```clojure
(defrecord A [v])

(def state
  (atom {:items [#user.A{:v 2}
                 #user.A{:v 5}]}))
```

And then, let create a two different focused atoms from the state:

```clojure
(def l1 (l/focus-atom (l/in [:items 0]) state))
(def l2 (l/focus-atom (l/in [:items 0 :v]) state))

@l2
;; => 2

@l1
;; => #user.A{:v 2}
```

The focused atom satisfies the atom interface so you can use them like normal
atoms. The main difference between them is that watchers are not triggered if
focused value is not changed.

Here is an example on how you can apply transformations over focused atoms:

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

If you want to see them in action, you can see the source code of my
[playground project][3] using [rum][4] as react wrapper.

[1]: https://github.com/funcool/cats
[2]: http://clojure.org/transducers
[3]: https://github.com/niwinz/rum-playground/tree/m1
[4]: https://github.com/tonsky/rum

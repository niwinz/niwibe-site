Title: Why GraphQL uses string based templates for queries?
Tags: graphql, rant, clojure
Author: Andrey Antukh

I've followed the graphql development from its public announcement
and at first I had my doubts about it, but over time I found the main
idea very interesting. However I could not stop asking myself: **why
string based templates are still used for representing the query language?**

Since the usage of SQL, is well known that strings are not composable
or easily transformable. As much as I try to reason about it, it
doesn't make sense for me. The SQL already suffers from that and there
are many SQL-DSL libraries trying to solve it in some manner.

**Why again we made a new language that has exactly the same
problems that SQL?**

Additionally to that, we have a new templating language that we need
to learn and deal with its idiosyncrasies. I'm not pretty convinced if
that brings something of value.

But in the end, is just **yet another** very limited template
language that has string interpolation and
some [strange way to include conditionals][1].

[1]: http://graphql.org/learn/queries/#directives

Please don't get me wrong, GraphQL is full of very very good ideas, it
is just that the implementation is not so good as the main idea. And
to be a little bit constructive I'll try to expose my ideas around
the main idea of the GraphQL.

In my vision of that, I think that the query should be represented by
something more composable and transformable. A great example would be
just using the plain data structures that the programming lenguage can
offer.

Let see a graphql query (as string) that I will use as reference in
following examples:


```clojure
"{
  human(id: $id) {
    name
    height(unit: FOOT)
    friends {
      name
    }
  }
  hero(id: $heroId) {
    name
  }
}"
```

And this is an example of a possible representation of the same query
but using clojure plain data structures:

```clojure
[[:human {:id "1000"}
  [:name
   [:height {:unit :foot}]
   [:friends [:name]]]]
 [:hero {:id "2000"}
  [:name]]]
```

Obviously it is not to be clojure coupled, and can be easy represented
with plain javascript plain data structures:

```js
[["human" {id: 1000}
  ["name"
   ["height" {unit: "FOOT"}]
   ["friends" ["name"]]]]
 ["hero" {id: "2000"}
  ["name"]]]
```

The main advantage of using something like this is that we neither need to
learn any new language nor additional directives to perform
conditionals. We just need the same (already familiar) tools that the
language offers for data transformation.

This is not rocket science and nothing new, **React** already uses the
same idea, replacing templates with javascript for create virtual dom
data structures. **There is no magic.**

On the server side we can still use the same logic to interpret those
queries as with graphql with the exception that we don't need
implement a new parser, we just need to use the language tools to
interpret that queries **this time, without the not necessary parsing step**.

In conclusion, I think we can learn a lot from GraphQL, it has a lot
of new and refreshing ideas but we need to thing to solve the current
pains instead just repeating them. Probably, on the near future I'll
try take some time for create a prototype of something like what I
have explained.

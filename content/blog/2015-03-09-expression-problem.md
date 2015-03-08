Title: The expression problem
Tags: clojure
Status: draft

The *Expression problem* is a new name to an old problem.

In my opinon, you probably do not care about it until kwnow it and kwnow how you can solve that
situations (problems) with much better approaches using more expressive languages.

Instead try explain the problem defintion, let's go to see an concrete and real example and how we
can solve it in most expressive way.

## A little introduction ##

We are developing an xmpp client, using third party XMPP library for connect to xmpp server. XMPP
has different entities, but for out example we will use that two: `RosterItem` and `Jid`.

Here a little description of these two types:

- The `RosterItem` represents an entry in the address book.
- The `Jid` represents a user identity.

Both them shares almost all fields and represents a User entity. In the XMPP terminology they have
different semantics but for out purposes is a simply `User` and we use it in interchangeably way.

Here a hypothetical data type (class) that represents a `RosterItem`

```groovy
public class RosterItem {
  public String name // "niwi"
  public String domain // "niwi.be"
  public SubscriptionType subscriptionType
}
```

Here a hypothetical data type (class) that represents a `Jid`

```groovy
public class Jid {
  public String local // "niwi"
  public String domain // "niwi.be"
  public String resource // "mypc"
}
```

And there are our constraints:

- We need treat that data types like a User data type in almost all out code base.
- We need interact in a simply way with the third party library.
- We need a common abstraction for access in a "polymorphic way" to properties.
- We can not change the source code, because is a third party library.

## Potential solutions ##

### Inheritance from common superclass ###

The traditional object-oriented solution to problems of this sort is to leverage subtype
polymorphism — that is, inheritance.

We need that our user can be represented in two different ways: bare and full. For it,
ideally, both classes would implement an interface like this:

```groovy
public interface IUser {
  public String getName()
  public String getBare()
  public String getFull()
}
```

But it is not an option because we need modify the source code of third party library.


### Multiple inheritance ###

Another approach to the Expression Problem is multiple inheritance, in which one subclass can extend
many superclasses.

Here a pseudocode:

```groovy
public User extends RosterItem, Jid implements IUser {
  public String getName() { /* implementation */ }
  public String getBare() { /* implementation */ }
  public String getFull() { /* implementation */ }
}
```

But we known that multiple inheritance has its own problems. It leads to complex and sometimes
unpredictable class hierarchies, and in my opinion should be avoided. Additionally, is not very
common feature in programming languages, that limits a lot the usage of that technique.

Concretelly, java and jvm languages does not support for multiple inheritance. Because of it,
this is also not an solution for out problem.


### Wrappers ###

This is a one of the most popular solutions for handle the expression problem in object oriented
languages and sometimes is treated as "the solution".

Let see an example using groovy language:

```groovy
// MyRosterItem.groovy
public class MyRosterItem implements IUser {
  final private RosterItem rosterItem
  public MyRosterItem(final RosterItem rosterItem) { this.rosterItem = rosterItem }
  public String getName() { /* implementation */ }
  public String getBare() { /* implementation */ }
  public String getFull() { /* implementation */ }
}
// MyJid.groovy
public class MyJid implements IUser {
  final private Jid jid
  public MyJid(final Jid jid) { this.jid = jid }
  public String getName() { /* implementation */ }
  public String getBare() { /* implementation */ }
  public String getFull() { /* implementation */ }
}
```

But this solution has a huge number of inconveniences:

- *It breaks the identity*. You can not use an instance of your roster item as parameter to the third
  party library that you are using for connect with XMPP. You should constanctly wrapping and
  unwrapping, and this adds a lot of additional axidental complexity.
- You can't compare a `MyJid` with `Jid` with `==` operator.
- You can't use `Object.equals` because it should be symetric. If you want compate an MyJid instance
  with some other `Jid` instance, you should explicitly wrap the second one for make the compatation.
- If you want that you `MyJid` type behaves exactly that `Jid`, you should implement a proxy
  for all public methods of `Jid` class. That can be very tedious if `Jid` implements something
  like `List` interface (or any other with huge number of methods).

In my opinion, wrappers is not good solution for expression problem and requires a lot of unnecesary
work.

### Open Classes ###

Consists in that a class can be reopened by anyone and at any time to add new methods.

This approach is popularized mainly by Ruby and JavaScript languages and it has similar problems that
multiple inheritance: not all languages supports it.

Example of open classes using ruby language:

```ruby
class String
  def write_size
    self.size
  end
end
puts "hello".write_size
```

This approach also solves the problem, but in my opinion adds more problems that solves:

- It breaks namespacing (like any other solution exposed previously)
- Easy name clashing. You have no way of knowing that some other user of that class won't define
  a different and incompatible method with same name.

This technique is also known as "Monkey patching" and is well known that is not a good design pattern
for your software.

### Traits ###

This is very very similar to openclasses, the unique difference is that is more safe. Because
if name clashing is happens, the compiller will notify about it and will abort the compilation.

Here an example of traits usage using rust language:

```rust
struct Dog { name: &'static str }

trait Animal {
    fn noise(&self) -> &'static str;
}

impl Animal for Dog {
    fn noise(&self) -> &'static str {
        "woof!"
    }
}
```

### Static methods with conditionals ###

This is other most common approaches to the expression problem. It consists in create a helper
class with static methods that uses conditionals (on type).

```groovy
public class Utils {
  public static String getName(final Object data) {
    if (source instanceof RosterItem) { /* implementation */ }
    else if (source instanceof Jid) { /* implementation */ }
    else { throw IllegalArgumentException("Invalid source."); }
  }
}
```

But in this case, we are not extending the type. We simply create a simple static funcion that
works on concrete type. This approach tends to grow into not maintainable code and obliges
modify the defined func in case you want extend it with new cases.

Additionally, it not performs very well.


### Static methods with overloading ###

This is an improvement over the previous case. Consists on using overloads instead of conditionals.

```groovy
public class Utils {
  public static String getName(final RosterItem data) { /* implementation */ }
  public static String getName(final Jid data) { /* implementation */ }
}
```

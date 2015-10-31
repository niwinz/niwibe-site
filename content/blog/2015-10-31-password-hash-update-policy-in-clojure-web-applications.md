Title: Password hash update policy in Clojure web applications
Tags: clojure, security, auth

Choice a strong password hasher for the modern web application is not very
complicated thing. At this moment the two most used algorithms are [**pbkdf2**][2]
and [**bcrypt**][3], so probably you should use one of them or any of its variants
such as **bcrypt+sha512** (buddy's default) or **pbkdf2+sha256**.

The both algorithms works in a similar way: iterate the algoritm N times for make
it slower. The security mainly consists on increase the iteration number over
time for make it slower acordly to the current security standart. For example on
the moment of write this article, 20000 is the recommeded iteration number for
pbkdf2 and 12 for bcrypt.

Choice a strong algorithm is important thing, but have a good update password
hashes policy is also very important and usually completelly forgotten. The
password generated 3 years ago is weaker that one generated today...

In recent work on [buddy-hashers][1] (version 0.8.0), this kind of problem can be
easily solved in clojure applications using a special hook that will be called
in the password check process when the password is correct but its configuration
is weaker that the current one.

Let see some code:

```clojure
(require '[buddy.hashers :as hs])

(letfn [(password-setter [password]
          (let [newpwd (hs/encrypt password)]
            (update-password-in-db newpwd)))]
  (hs/check "incoming-password" password-from-db {:setter password-setter}))
```

This kind of code can be placed in the login part of your web application
and every time the users are logged their passwords are checked. If the password
passed the validation but it looks weaker the hook will be called; enabling a
simple entry point for properly rehash the password and store it again in the
database.

In reality, this is a very small and insignificant feature, but it makes the things
much easier for maintain the passwords of your application users updated with the
stongest password hasher configuration.

[1]: https://github.com/funcool/buddy-hashers
[2]: https://en.wikipedia.org/wiki/PBKDF2
[3]: https://en.wikipedia.org/wiki/Bcrypt

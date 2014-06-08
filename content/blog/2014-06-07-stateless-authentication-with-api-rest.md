Title: Stateless Authentication with api rest.
Tags: authentication, api, rest, clojure, python
Status: draft

When we talk about authentication for api rest, almost everyone think about oauth1 or oauth2 and
their variants defined by service providers. Also, exists other authentication system, such
as: token, openid, etc..., but them are not widely used in comparison with oauth.

That do you thing about all them? Are all them truly stateless?


## How authentication works?

Before continue, I want to explain how standard (http session) works and compare it to oauth2.


### Basic steps on how standard http session authentication works:

1. Client sends its credentials to server.
2. Server authenticates them and generates fixed length token.
3. Server stores previously generated token in some one storage with user identifier.
4. Server sends previously generated token to client with new Cookie "sessionid=here-the-random-token".
5. Now, client, in each request, sends that token in each request using cookies header.
6. Server in each request, extract session id token from incoming cookie, lookup user identifier
   on its key/value and query database for obtain user information.

### Basic steps on how oauth2 works:

1. Client sends its credentials to server.
2. Server authenticates them and generates fixed length token.
3. Server stores previously generated token in some one storage with user identifier.
4. Server sends previously generated token to client in a body of response (usually in json format).
5. Now, client send that token in each request in "Authorization" header.
6. Server, in each request, extract the token from authorization header and lookup user identifier
   on its storage and query database for obtain user information.


This is a very superficial overview of oauth2 steps, but if you want know more about it, see this article:
[OAuth2 Simplified](http://aaronparecki.com/articles/2012/07/29/1/oauth2-simplified)


## They are truly stateless?

Now, having viewed the comparison, you can view that oauth2 not differs much from standard
http session authentication. The big difference is that token is sended in an other header.
If you are thinking that any of previously mentioned authentication are stateless, you are wrong.

Stateless means without state, but as we having viewed, http session, oauth, etc... have
small state: the token storage. Obviously is not a bad solution, but it has several disadvantages:

- requires shared storage if you want scale the number of your servers.
- with hundreds of thousands clients, you are forced to maintain hundreds of thousands tokens.
- with hundreds of thousands clients (when each client can have more than one token) token storage
  can be expensive.


## What is stateless authentication?

Stateless means without state. But, how we can identify a user from token without having any state
on server? In fact, very easy! Simplifying, send all the data to the client.

So what would you store/send (send to client/network)? The most trivial example is an access token.
Access tokens usually have a unique ID, an expiration date and the ID of the client
that created it. To store this, you would just put this data into a JSON object, base64 encode it.

Now having self contained token, you will need to make sure that nobody can manipulate the data. For this
you should simple sign it using [MAC algotithm](http://en.wikipedia.org/wiki/Message_authentication_code) or
any other digital signature methods.

This approach has huge advantages:

- the biggest one is that your storage is unbounded, because you actually don't store anything.
- an application that forgets about it's access token will just no longer remember it and the data
  automatically expires.
- systems can be entirely decoupled from each other, no more shared token storage.


## How I can use it with my language?

This is a simplest step, because almost all modern languages has good cryptographic signature libraries
and utils for work with json and base64.

In case of Python, you can use [itsdangerous](http://pythonhosted.org/itsdangerous/).

```pycon
>>> from itsdangerous import JSONWebSignatureSerializer
>>> s = JSONWebSignatureSerializer('secret-key')
>>> s.dumps({'x': 42})
'eyJhbGciOiJIUzI1NiJ9.eyJ4Ijo0Mn0.ZdTn1YyGz9Yx5B5wNpWRL221G1WpVE5fPCPKNuc6UAo'
```

In case of Clojure, you can use [buddy](https://github.com/niwibe/buddy).

```clojure
user=> (require '[buddy.sign.jws :as jws])
user=> (jws/sign {:x 1} "secret-key")
"eyJ0eXAiOiJKV1MiLCJhbGciOiJIUzI1NiJ9.eyJ4IjoxfQ.-hx2Os6uDC12kEqm2IDnKG0jWlq3wLmqgMHjtulRqr0"
```

## Myths of security flaws

Before having written this article, I have talked to several people about this, and in almost all
situations I have come to have this kind of comments:

_"I don't trust it, because it send data to the client"_

If you do not trust the purposed approach, you are not trust the heavy used mac algorithms (that are used
in almost all security software). This affirmation is unfounded.

_It's vulnerable to main-in-the-middle attack_

Yes, it is. As any other mentioned authentication system here.

The most standard way of authentication is also vulnerable to that attack. For prevent it you should
use ssl connections. This affirmation is also unfounded, because the purposed approach has the same
security flaws as the rest of authentication systems.


## Summary

Signed self contained token is a nice way to avoid use database. It allows decoupling and better scalling
your systems and have written different parts of your system in different languages.

It's nothing new, people have been doing this for ages.

Related article: [My Favorite Database is the Network](http://lucumr.pocoo.org/2013/11/17/my-favorite-database/)

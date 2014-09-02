Title: Stateless Authentication with api rest.
Tags: authentication, api, rest, clojure, python

When we talk about authentication for api rest, almost everyone tends to think about oauth1 or oauth2 and their variants defined by service providers. It’s true that there also other auth systems such as token, openid, etc, but they are not as widely used in comparison with oauth.

What do you think about them? Are they all truly stateless?


## How authentication works?

Before I start, I’d like to explain how standard (http session) works and compare it to oauth2.

### Basic steps on how standard http session authentication works:

1. Client sends its credentials to server.
2. Server authenticates them and generates fixed length token.
3. Server stores previously generated token in some one storage with user identifier.
4. Server sends previously generated token to client with new Cookie "sessionid=here-the-random-token".
5. Now, client, in each request, sends that token in each request using cookies header.
6. Server in each request, extract session id token from incoming cookie, looks up the user identifier
   on its key/value and query database for obtain user information.

### Basic steps on how oauth2 works:

1. Client sends its credentials to server.
2. Server authenticates them and generates fixed length token.
3. Server stores previously generated token in some one storage with user identifier.
4. Server sends previously generated token to client in a response body (usually in json format).
5. Now, client sends that token in each request using the "Authorization" header.
6. Server, in each request, extract the token from authorization header and looks up the user identifier
   on its storage and query database for obtain the user information.


This is a very superficial overview of oauth2 steps so if you want know more about it please check this article: [OAuth2 Simplified](http://aaronparecki.com/articles/2012/07/29/1/oauth2-simplified)

## Are they truly stateless?

Now, having viewed the comparison, you can easily see that oauth2 does not differ that much from standard http session authentication. The big difference is that the token is sent using a different header. If you are of the opinion that both methods are stateless, you are wrong, here is why.

Stateless means without state, but as we already saw, http session, oauth, etc… have a (small) state: the token storage. This is not a bad solution per se, but it poses several disadvantages:

- It requires shared storage if you want to scale the number of your servers.
- With hundreds of thousands clients, you are forced to maintain hundreds of thousands tokens.
- With hundreds of thousands clients (and each client allowed to have more than one token) token storage can be very expensive.


## What is stateless authentication?


Again, stateless means without state. But, how can we identify a user from a token without having any state on the server? Surprisingly, it’s very easy! just send all the data to the client.

So what would you store/send (send to client/network)? The most trivial example is an access token. Access tokens usually have a unique ID, an expiration date and the ID of the client that created it. To store this, you would just put this data into a JSON object, and encode it using base64.

Now, having a self-contained token, you will need to make sure that nobody can manipulate the data. For this you should sign it using [MAC algorithm](http://en.wikipedia.org/wiki/Message_authentication_code) or any other digital signature method available.

This approach has great advantages:

- The biggest one is that your storage needs are zero, because you are not storing anything.
- An application that forgets about its access token will simply no longer remember it and the data will automatically expire.
- Systems can be entirely decoupled from each other, thanks to no more shared token storage.

## How I can use it with my language?

This is a simplest step, because almost all modern languages have good cryptographic signature libraries
and utils to work with both json and base64.

Lets see an example in Python. You can use [itsdangerous](http://pythonhosted.org/itsdangerous/).

```pycon
>>> from itsdangerous import JSONWebSignatureSerializer
>>> s = JSONWebSignatureSerializer('secret-key')
>>> s.dumps({'x': 42})
'eyJhbGciOiJIUzI1NiJ9.eyJ4Ijo0Mn0.ZdTn1YyGz9Yx5B5wNpWRL221G1WpVE5fPCPKNuc6UAo'
```

Or even more compact using Clojure, you can use [buddy](https://github.com/niwibe/buddy).

```clojure
user=> (require '[buddy.sign.jws :as jws])
user=> (jws/sign {:x 1} "secret-key")
"eyJ0eXAiOiJKV1MiLCJhbGciOiJIUzI1NiJ9.eyJ4IjoxfQ.-hx2Os6uDC12kEqm2IDnKG0jWlq3wLmqgMHjtulRqr0"
```

## Myths of security flaws

Before writing this short article, I went to several people and talked about this. In almost all situations I ended up receiving this comment:

_"I don't trust it, because it send data to the client"_

If you do not trust the proposed approach, you are indirectly stating that you don’t trust the widely used MAC algorithms (they are used in almost every security piece of software). This criticism lacks broader knowledge.

_It's vulnerable to man-in-the-middle attack_

This a different type of criticism. Yes, it is vulnerable… as any other authentication system mentioned here. The most standard ways of authentication are also vulnerable to that attack. SSL should be used to prevent it. This criticism is also very weak in the sense that is not particular to a stateless authentication system.

## Summary

Signed self contained token is a nice way to avoid using databases/storage. It allows decoupling, better system scaling and allows you to write different parts of your system in different programming languages.

It’s nothing new, people have been doing this for ages.

- Related article: [My Favorite Database is the Network](http://lucumr.pocoo.org/2013/11/17/my-favorite-database/)
- [Original article](http://www.kaleidos.net/blog/295/stateless-authentication-with-api-rest/)

Title: Fetching and aggregating data from remote sources with Urania
Tags: clojure, clojurescript, remote data
Author: Alejandro Gómez

## The problem ##

Oftentimes, our software relies on fetching and aggregating data from remote sources. Be it a database,
an API exposed via HTTP or another protocol, the filesystem, or a cache. Remote data sources often have
latency associated to them, and there may be unavailable due to network conditions.

When implementing business logic relying on remote data sources, we often have to complect many concerns:

- The actual data transformation and aggregation
- Fetching the data optimally for minimizing latency
    * Deduplication
    * Caching
    * Batching
- Detecting and handling errors
    * Performing retries
    * Using timeouts for aborting fetches

All of this can make us trade code clarity for performance, and our business logic gets buried in low-level
details.

### Enter Urania ###

[Urania][1] makes your business logic relying on remote data sources efficient and free of the minutiae of optimization
and error handling. It achieves this goals with two core ideas:

 - Using the Promise type available in [Promesa][2] for conveying asynchronous values which can fail
 - Separating the declaration of a fetch from its interpretation and applying optimizations when interpreted

## Case study ##

We'll be using a few Clojure libraries for the example, you can use the following `project.clj` if you want to run
the code:

```clojure
(defproject hello-urania "0.1.0"
  :dependencies [[org.clojure/clojure "1.7.0"]
                 [funcool/urania "0.1.0"]
                 [funcool/promesa "0.8.1"]
                 [funcool/httpurr "0.5.0-SNAPSHOT"]
                 [org.clojure/data.json "0.2.6"]
                 [aleph "0.4.1-beta4"]
                 [funcool/suricatta "0.8.1"]
                 [org.postgresql/postgresql "9.4-1204-jdbc42"]])
```

Imagine that we are running a website which has a relational database and stores the information about its users in
there. We are exposing an API for asking several questions about our users, for example their GitHub username. These
queries will have to fetch data from our relational DB, as well as from GitHub and potentially other sources.

We want to make these queries composable, efficient, and free of the details of asynchronous data fetching and we'll use
Urania to achieve that. First of all, we are going to create our relational database. We'll be using the [suricatta][3] library
for running SQL queries against a PostgreSQL db:

```clojure
(require '[suricatta.core :as sc])

(def dbspec {:subprotocol "postgresql"
             :subname "//localhost:5432/urania"})

(def db (sc/context dbspec))
```

We create and populate our only table: users.

```clojure
(sc/execute db
            "CREATE TABLE users (
               id BIGSERIAL PRIMARY KEY,
               githubid VARCHAR(255) UNIQUE NOT NULL
             )")
;; => 0

(sc/execute db
            "INSERT INTO users (githubid) VALUES ('dialelo');")
;; => 1
```

And now we can fetch users from the DB:

```clojure
(sc/fetch-one db
              ["SELECT * from users where id = ?" 1])
;; => {:id 1, :githubid "dialelo"}
```

We now have a way to fetch a user given its id, which is very nice, but it will return `nil` if the user is not
found thus limiting its composability. Also, the query is executed synchronously, and we may want to perform it
in a separate thread.

Let's define a data source for the users of our database. When the user is not found, it will return a rejected
promise and if its found it will simply resolve the promise with the user data:

```clojure
(require '[promesa.core :as prom])
(require '[urania.core :as u])

(defn print!
  [thing]
  (print (str (pr-str thing) \newline)))

(deftype User [id]
  u/DataSource
  (-identity [_] id)
  (-fetch [_ {:keys [db]}]
    (print! [:->user id])
    (prom/promise
      (fn [resolve reject]
        (if-let [usr (sc/fetch-one db
                                 ["SELECT * from users where id = ?" id])]
         (do
           (print! [:<-user usr])
           (resolve usr))
         (reject (ex-info "User not found" {:id id})))))))

(defn user
  [id]
  (User. id))
```

Now, we can ask for users given their id. Notice how we inject the db connection when running a fetch:

```clojure
(u/run!! (user 1) {:env {:db db}})
;; [:->user 1]
;; [:<-user {:id 1, :githubid dialelo}]
;; => {:id 1, :githubid "dialelo"}
```

If we try to fetch a user that doesn't exist, we get back a rejected promise. Lets take a look:

```clojure
(def fetch (u/run! (user 99) {:env {:db db}}))

(deref
  (prom/catch fetch
              (fn [err]
                {:msg (.getMessage err)
                 :data (ex-data err)})))
;; [:->user 99]
;; => {:msg "User not found", :data {:id 99}}
```

In the above example, we use promesa's `catch` combinator to transform an exception thrown inside a rejected promise
to a resolved promise which contains a data strutcture with information about the error.

We can ask the first question about our users: given a user id, give me its GitHub username.

```clojure
(defn github-username-by-id
  [id]
  (u/map :githubid (user id)))

(u/run!! (github-username-by-id 1) {:env {:db db}})
;; [:->user 1]
;; [:<-user {:id 1, :githubid dialelo}]
;; => "dialelo"
```

We can now fetch our users but we want to ask questions about their GitHub activity so we'll need a way to fetch GitHub
user information. For that we use GitHub's API, you'll need a GitHub OAuth token for running these examples. We'll use
the [httpurr][4] Clojure(Script) HTTP client to communicate with GitHub. First of all, let's define the headers we are going to
use and the response parsing code:

```clojure
(require '[clojure.data.json :as json])

(def github-token "bring-your-own-token")

(def github-headers {"User-Agent" "httpurr"
                     "Content-Type" "application/json"
                     "Authorization" (str "token " github-token)})

(defn parse-response
  [response]
  (-> response
    :body
    slurp
   (json/read-str :key-fn keyword)))
```

Now we're able to define a data source for github users:

```clojure
(require '[httpurr.client :as http])

(defn github-user-url
  [username]
  (str "https://api.github.com/users/" username))

(deftype GitHubUser [username]
  u/DataSource
  (-identity [_] username)
  (-fetch [_ {:keys [http]}]
    (print! [:->github-user username])
    (let [req (http/send! http
                          {:method :get
                           :url (github-user-url username)
                           :headers github-headers})]
       (prom/then req #(do
                         (print! [:<-github-user username])
                         (parse-response %))))))

(defn github-user
  [username]
  (GitHubUser. username))
```

Now that we have two data sources we can start asking more interesting questions about our data, let's give it a spin. We'll
start with a simple query: given a user ID from our database, give me its GitHub user information. Note how we build this
query on top of a previous one: `github-username-by-id`:

```clojure
(require '[httpurr.client.aleph :refer [client]])

(defn github-user-by-id
  [id]
  (u/mapcat github-user (github-username-by-id id)))

(u/run!! (github-user-by-id 1) {:env {:db db, :http client}})
;; [:->user 1]
;; [:<-user {:id 1, :githubid dialelo}]
;; [:->github-user dialelo]
;; [:<-github-user dialelo]
;; => {:html_url "https://github.com/dialelo", :disk_usage 604079, ... }
```

Since our `github-user` returns a fetch to perform we have used `urania.core/mapcat` instead of `urania.core/map`.

We can now start asking questions about the GitHub account of our users, for example how many followers they have:

```clojure
(defn github-follower-count-by-id
  [id]
  (u/map :followers (github-user-by-id id)))

(u/run!! (github-follower-count-by-id 1) {:env {:db db, :http client}})
;; [:->user 1]
;; [:<-user {:id 1, :githubid dialelo}]
;; [:->github-user dialelo]
;; [:<-github-user dialelo]
;; => 186
```

Or we can even merge the data from our database with the account info on GitHub.

```clojure
(defn db-and-github-user
  [id]
  (u/map #(merge %1 %2)
         (user id)
         (github-user-by-id id)))

(u/run!! (db-and-github-user 1) {:env {:db db, :http client}})
;; [:->user 1]
;; [:<-user {:id 1, :githubid dialelo}]
;; [:->github-user dialelo]
;; [:<-github-user dialelo]
;; => {:html_url "https://github.com/dialelo", :githubid "dialelo", ... }
```

Notice that we call `(user id)` both in `db-and-github-user` function's body and inside `github-user-by-id` but is
only fetched once. This deduplication that urania does for you alows you to write code like the remote data is residing
in memory.

Now that we are going to ask questions about the organization a user belongs to, so we need to define another data source
for fetching a user's organizations:

```clojure
(def github-user-orgs-url "https://api.github.com/user/orgs")

(deftype UserOrgs [username]
  u/DataSource
  (-identity [_] username)
  (-fetch [_ {:keys [http]}]
    (print! [:->github-user-orgs username])
    (let [req (http/send! http
                          {:method :get
                           :url github-user-orgs-url
                           :headers github-headers})]
      (prom/then req #(do
                       (print! [:<-github-user-orgs username])
                       (parse-response %))))))

(defn github-user-orgs
  [username]
  (UserOrgs. username))
```

Let's ask for the organizations of a certain user now:

```clojure
(defn github-orgs-by-user-id
  [id]
  (u/mapcat github-user-orgs (github-username-by-id id)))

(u/run!! (u/map count (github-orgs-by-user-id 1))
         {:env {:db db, :http client}})
;; [:->user 1]
;; [:<-user {:id 1, :githubid dialelo}]
;; [:->github-user-orgs dialelo]
;; [:<-github-user-orgs dialelo]
;; => 14
```

Or augment a GitHub user's data with their organizations:

```clojure
(defn github-user-with-orgs-by-id
  [id]
  (u/map #(assoc %1 :orgs %2)
         (github-user-by-id id)
         (github-orgs-by-user-id id)))

(u/run!! (github-user-with-orgs-by-id 1)
         {:env {:db db, :http client}})
;; [:<-user {:id 1, :githubid "dialelo"}]
;; [:->github-user "dialelo"]
;; [:->github-user-orgs "dialelo"]
;; [:<-github-user "dialelo"]
;; [:<-github-user-orgs "dialelo"]
;; => {:html_url "https://github.com/dialelo", :disk_usage 604079 ... }
```

Notice how both the GitHub user and its organizations are fetched concurrently.

In the age of microservices, many utility function have been refactored to microservices. It's the case of our Uppercase
microservice, which takes a word and returns it uppercased. In the first iteration of our uppercase microservice it is
only available to uppercase one word at a time, let's define a data source for it:

```clojure
(defrecord Uppercase [string]
  u/DataSource
  (-identity [_] string)
  (-fetch [_ _]
    (print! [:->uppercase-string string])
    (let [uppercased (.toUpperCase string)]
      (print! [:<-uppercase-string uppercased])
      (prom/resolved uppercased))))

(defn uppercase
  [str]
  (Uppercase. str))
```

We now want to know the uppercased name of every GitHub organization a user belongs to, so let's write that query:

```clojure
(defn uppercased-github-org-names
  [id]
  (u/traverse (fn [org]
                (uppercase (:login org)))
              (github-orgs-by-user-id id)))

(u/run!! (uppercased-github-org-names 1)
         {:env {:db db, :http client}})
;; [:->user 1]
;; [:<-user {:id 1, :githubid "dialelo"}]
;; [:->github-user-orgs "dialelo"]
;; [:<-github-user-orgs "dialelo"]
;; [:->uppercase-string "kaleidos"]
;; [:->uppercase-string "Front-Guerrilla"]
;; [:<-uppercase-string "FRONT-GUERRILLA"]
;; [:<-uppercase-string "KALEIDOS"]
;; [:->uppercase-string "wikimaps"]
;; [:->uppercase-string "uxbox"]
;; [:->uppercase-string "47deg"]
;; [:<-uppercase-string "UXBOX"]
;; [:<-uppercase-string "47DEG"]
;; [:->uppercase-string "sloth"]
;; [:<-uppercase-string "WIKIMAPS"]
;; [:<-uppercase-string "SLOTH"]
;; [:->uppercase-string "thefinalcountapp"]
;; [:->uppercase-string "taigaio"]
;; [:->uppercase-string "mammutdb"]
;; [:<-uppercase-string "TAIGAIO"]
;; [:<-uppercase-string "THEFINALCOUNTAPP"]
;; [:->uppercase-string "funcool"]
;; [:->uppercase-string "Emacs-Madrid"]
;; [:<-uppercase-string "FUNCOOL"]
;; [:<-uppercase-string "EMACS-MADRID"]
;; [:->uppercase-string "clojurecup2014"]
;; [:->uppercase-string "opensourcedesign"]
;; [:<-uppercase-string "CLOJURECUP2014"]
;; [:<-uppercase-string "OPENSOURCEDESIGN"]
;; [:->uppercase-string "PIWEEK"]
;; [:<-uppercase-string "PIWEEK"]
;; [:<-uppercase-string "MAMMUTDB"]
;; => ["47DEG" "KALEIDOS" "WIKIMAPS" "OPENSOURCEDESIGN" "PIWEEK" "FRONT-GUERRILLA" "EMACS-MADRID" "TAIGAIO" "MAMMUTDB" "CLOJURECUP2014" "THEFINALCOUNTAPP" "FUNCOOL" "SLOTH" "UXBOX"]
```

Whoa, that's a lot of requests to our uppercase microservice. Since we are having problems scaling it we have implemented
a batch API, we can now uppercase words in batches! We update our data source to take advantage of the batch API:

```clojure
(extend-type Uppercase
  u/BatchedSource
  (-fetch-multi [up ups _]
    (let [all-strs (cons (:string up) (map :string ups))
          uppercased (mapv #(.toUpperCase %) all-strs)]
      (print! [:->uppercase-strings all-strs])
      (print! [:<-uppercase-strings uppercased])
      (prom/resolved (zipmap all-strs uppercased)))))
```

And notice how re-runing the query takes advantage of the batch API:

```clojure
(u/run!! (uppercased-github-org-names 1)
         {:env {:db db, :http client}})
;; [:->user 1]
;; [:<-user {:id 1, :githubid "dialelo"}]
;; [:->github-user-orgs "dialelo"]
;; [:<-github-user-orgs "dialelo"]
;; [:->uppercase-strings ("kaleidos" "Front-Guerrilla" "wikimaps" "uxbox" "47deg" "sloth" "thefinalcountapp" "mammutdb" "taigaio" "funcool" "Emacs-Madrid" "clojurecup2014" "opensourcedesign" "PIWEEK")]
;; [:<-uppercase-strings ["KALEIDOS" "FRONT-GUERRILLA" "WIKIMAPS" "UXBOX" "47DEG" "SLOTH" "THEFINALCOUNTAPP" "MAMMUTDB" "TAIGAIO" "FUNCOOL" "EMACS-MADRID" "CLOJURECUP2014" "OPENSOURCEDESIGN" "PIWEEK"]]
;; => ["KALEIDOS" "FRONT-GUERRILLA" "WIKIMAPS" "UXBOX" "47DEG" "SLOTH" "THEFINALCOUNTAPP" "MAMMUTDB" "TAIGAIO" "FUNCOOL" "EMACS-MADRID" "CLOJURECUP2014" "OPENSOURCEDESIGN" "PIWEEK"]
```

## Conclusion

Urania helps keep your business logic relying on remote data source elegant and composable, while executing it
efficiently without you having to specify any coordination, deduplication or cahing. It can aggregate data from
a variety of remote data sources, signal and recover from failures, and make your code elegant and efficient.

[1]: https://github.com/funcool/urania
[2]: https://github.com/funcool/promesa
[3]: https://github.com/funcool/suricatta
[4]: https://github.com/funcool/httpurr

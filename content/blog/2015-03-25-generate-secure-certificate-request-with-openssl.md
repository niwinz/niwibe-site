Title: Generating a secure certificate request with OpenSSL
Tags: security, ssl

This is a little cheat sheet for personal use on how generate a secure certificate
request using openssl.

The first step is creating a strong private key. At this moment the 2048bits is the recommended
key lenght. Security experts are projecting that 2048 bits will be sufficient for commercial use
until around the year 2030 ([Reference1](http://security.stackexchange.com/questions/65174/4096-bit-rsa-encryption-keys-vs-2048)
and [Reference2 pdf](http://csrc.nist.gov/publications/nistpubs/800-57/sp800-57_part1_rev3_general.pdf))

```bash
openssl genrsa -out ~/niwi.be.key 2048
```

And the second step is create a proper csr (certificate request). I said proper because
you should expliclitly specify the secure hash algorith to use for sign. In this
case it should never be *sha1* ([Reference1](https://konklone.com/post/why-google-is-hurrying-the-web-to-kill-sha-1) and
[Reference2](https://shaaaaaaaaaaaaa.com/))

The recommended hash algorithm today is *sha256*:

```bash
openssl req -new -sha256 -key ~/niwi.be.key -out ~/niwi.be.csr
```

Here a little guide to different fields that you will found when creating the CSR:

- *Common Name*: If you intend to secure the URL https://www.niwi.be, then your CSR's common name must be
  `www.niwi.be`. If you plan on getting a wildcard certificate make sure to prefix your domain with an
  asterisk, example: `*.niwi.be`.
- *Organization*: The exact legal name of your organization. Example: `niwi.be`.
- *Organization unit*: The section of your organization. Example: `IT`.
- *City or Locality*: The legal city of your organization. Example: `Madrid`.
- *State or Provice*: The legal province of your organization. Example: `Madrid`.
- *Country*: The legal country of your organizationin ISO format: `ES`. (Full list [here](http://www.vas.com/Tnotes/Country%20Codes.htm))

And the last step, you may verify your csr:

```shell
openssl req -noout -text -in ~/niwi.be.csr
```

This is a possible striped output with relevant information:

```text
Certificate Request:
    Data:
        Version: 0 (0x0)
        Subject: C=ES, ST=Madrid, L=Madrid, O=niwi.be, OU=IT, CN=*.niwi.be/emailAddress=niwi@niwi.be
        [...]
    Signature Algorithm: sha256WithRSAEncryption
        [...]
```


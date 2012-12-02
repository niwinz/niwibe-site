#!/bin/sh
(cd _gen; s3cmd sync -P . s3://www.niwi.be/;)

#!/bin/sh
(cd output; s3cmd sync -P . s3://www.niwi.be/;)

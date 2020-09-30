# podcatcher

Simple podcast downloader

## Running

1. Create config.ini and add feeds
2. build docker image - ONE TIME ONLY:
   1. docker build --tag {DOCKER IMAGE TAG} {PATH TO DOCKERFILE}
3. Every time you want it to run
   1. docker run --rm -v {PATH TO CODE}:/code -v {PATH TO DOWNLOAD TO}:/pods {DOCKER IMAGE TAG}

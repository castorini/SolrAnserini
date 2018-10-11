FROM solr:7.4-alpine

# Do some setup as root.
USER root

# Install curl.
RUN apk update && apk add curl

# Work as the solr user.
USER solr

# Work from the base dir of the Solr install.
WORKDIR /opt/solr/

# Anserini JAR for TwitterAnalyzer.
COPY --chown=solr anserini.jar lib/

# Copy the configsets.
COPY --chown=solr configsets/. server/solr/configsets

# Create cores
RUN precreate-core core17 server/solr/configsets/core17
RUN precreate-core mb11 server/solr/configsets/mb11

# Start the server.
CMD solr-foreground

# Solr Integration

Anserini, using `IndexCollection`, generates Lucene index files that we can load into [Solr](http://lucene.apache.org/solr/). Solr is a search engine build on Lucene that has desirable tools such as an interface to perform queries on Lucene (Anserini) indices.

Docker
======

In order to integrate Anserini and Solr, we'll be using [Docker](https://www.docker.com/) - make sure this is setup on your machine before continuing.

Additionally, ensure that the Docker SDK for Python is installed via `pip install docker`

Overview
========

Loading a Lucene index into Solr is fairly straightforward as Solr is built on top of Lucene. In a nutshell, the following needs to happen:

1. Create the Solr core (index) that will hold our data.
2. Copy the Lucene index files into the `<my_core>/data/index/` directory of the Solr server.
3. Update the schema (`<my_core>/conf/managed-schema`) file to match the fields in our index.
4. Reload the core.

This has been automated through a number of scripts to automatically load `core17` and `mb11` collection indices into Solr.

Instructions
============

Build Anserini and copy the fatjar (important) artifact into the root directory of the SolrAnserini repo, changing the name to `anserini.jar`.

1. Edit the `config.json` file to point to the index and config locations on the host machine.
2. Run the Python script to build the Docker image with index and config volumes mounted.
    - `python run.py` (optionally specifying `--config <config_location>`)
3. Wait about 20 seconds and reload each core from the admin UI (`http://localhost:8983`).

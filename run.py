import argparse
import json
import os
import time

import docker
from docker.errors import NotFound


def run(config_path):
    # Load config file
    with open(config_path) as file:
        config = json.load(file)

    # Docker API client
    client = docker.from_env()

    # Remove any existing image
    remove_existing(client, config)

    # Build the container
    build_container(client, config)

    # Run the container
    container = run_container(client, config)

    print("Sleeping for 10 seconds while Solr starts...")
    time.sleep(10)

    for index in config["indexes"]:
        # Remove the lock file, if exists.
        container.exec_run("rm -f %s" % os.path.join(config["index_mount"], index["name"], "write.lock"), user='solr')

        # Remove Solr generated index data.
        container.exec_run("rm -rf %s" % os.path.join("/opt/solr/server/solr/mycores", index["name"], "data/index"),
                           user='solr')

        # Create link to data volume
        container.exec_run("ln -s %s %s" % (os.path.join(config["index_mount"], index["name"]),
                                            os.path.join("/opt/solr/server/solr/mycores", index["name"], "data/index")),
                           user='solr')


# Remove any existing containers
def remove_existing(client, config):
    try:
        container = client.containers.get(config["image_name"])
        container.stop()
        container.remove()
    except NotFound:
        pass


# Build the container
def build_container(client, config):
    for line in client.api.build(path=".", tag=config["image_name"]):
        print(line)


def get_volumes(config):
    volumes = {}

    for index in config["indexes"]:
        # Path on host for index
        index_path_host = os.path.join(os.getcwd(), index["index_path"])

        # Path in container for index
        index_path_container = os.path.join(config["index_mount"], index["name"])

        # Path on host for configs
        config_path_host = os.path.join(os.getcwd(), index["config_path"])

        # Path in container for configs
        config_path_container = os.path.join("/opt/solr/server/solr/configsets", index["name"])

        # Add the binding for index paths
        volumes[index_path_host] = {
            "bind": index_path_container,
            "mode": "rw"
        }

        # Add the binding for config paths
        volumes[config_path_host] = {
            "bind": config_path_container,
            "mode": "ro"
        }

    return volumes


def run_container(client, config):
    volumes = get_volumes(config)
    return client.containers.run(config["image_name"],
                                 detach=True,
                                 name=config["image_name"],
                                 ports={"8983": "8983"},
                                 user="solr",
                                 volumes=volumes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json", type=str, help="The config file location.")

    args = parser.parse_args()

    run(args.config)

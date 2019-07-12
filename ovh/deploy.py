import argparse
import logging
import time
import uuid

import openstack
import requests

# FIXME: change prefix to voila-gallery- or make this configurable
GALLERY_PREFIX = "voici-gallery-"
IMAGE = "Ubuntu 19.04"
# FIXME: switch to b2-30
FLAVOR = "b2-7"
USER_DATA_FILE = "./user-data.sh"
POLL_TIMEOUT = 20 * 60
POLL_INTERVAL = 30

logger = logging.getLogger(__name__)


def list_servers(cloud):
    logger.info("List existing servers")
    servers = cloud.list_servers()
    return [server for server in servers if server.name.startswith(GALLERY_PREFIX)]


def poll_server(cloud, server_id):
    tries = POLL_TIMEOUT // POLL_INTERVAL
    for i in range(tries):
        try:
            logger.info("Check server is ACTIVE: %s", server_id)
            server = cloud.get_server_by_id(server_id)
            addr_ipv4 = next(
                (addr for addr in server.addresses["Ext-Net"] if addr["version"] == 4)
            )
            addr = addr_ipv4["addr"]
            url = f"http://{addr}/api"
            logger.info("Poll %s", url)
            requests.get(url, timeout=10, verify=False)
        except Exception as e:
            time.sleep(POLL_INTERVAL)
        else:
            break


def create_server(cloud, tag):
    with open(USER_DATA_FILE) as f:
        user_data = f.read()

    instance_suffix = uuid.uuid4().hex[:6]
    name = f"{GALLERY_PREFIX}{tag}-{instance_suffix}"
    logger.info("Create server %s...", name)
    server = cloud.create_server(
        image=IMAGE, flavor=FLAVOR, userdata=user_data.format(ref=tag), name=name
    )
    logger.info("Server created: %s", server.id)
    return server


def stop_servers(cloud, servers):
    for server in servers:
        logger.info("Stopping server: %s...", server.name)
        cloud.delete_server(server.name, wait=True)
        logger.info("Stopped")


def setup_logger():
    stderr_logger = logging.StreamHandler()
    stderr_logger.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    stderr_logger.setLevel(logging.INFO)
    logger.addHandler(stderr_logger)
    logger.setLevel(logging.INFO)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--tag",
        help="Suffix to add to the instance name (git commit hash)",
        required=True,
    )
    args = argparser.parse_args()

    setup_logger()
    logger.info("Connect...")
    cloud = openstack.connect()
    logger.info("Connected")

    galleries = list_servers(cloud)

    server = create_server(cloud, args.tag)
    poll_server(cloud, server.id)
    # FIXME: add to an existing floating ip
    stop_servers(cloud, galleries)


if __name__ == "__main__":
    main()

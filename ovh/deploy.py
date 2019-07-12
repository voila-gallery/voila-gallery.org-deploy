import argparse
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


def poll_server(cloud, server_id):
    tries = POLL_TIMEOUT // POLL_INTERVAL
    for i in range(tries):
        try:
            server = cloud.get_server_by_id(server_id)
            addr_ipv4 = next(
                (addr for addr in server.addresses["Ext-Net"] if addr["version"] == 4)
            )
            addr = addr_ipv4["addr"]
            url = f"http://{addr}/api"
            requests.get(url, timeout=10, verify=False)
        except Exception as e:
            print("sleep", POLL_INTERVAL)
            time.sleep(POLL_INTERVAL)
        else:
            break


def create_server(cloud, tag):
    with open(USER_DATA_FILE) as f:
        user_data = f.read()

    instance_suffix = uuid.uuid4().hex[:6]
    server = cloud.create_server(
        image=IMAGE,
        flavor=FLAVOR,
        userdata=user_data.format(ref=tag),
        name=f"{GALLERY_PREFIX}{tag}-{instance_suffix}",
    )

    poll_server(cloud, server.id)

    # FIXME: add to an existing floating ip


def stop_servers(cloud, servers):
    for server in servers:
        cloud.delete_server(server.name, wait=True)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--tag",
        help="Suffix to add to the instance name (git commit hash)",
        required=True,
    )
    args = argparser.parse_args()

    cloud = openstack.connect()

    servers = cloud.list_servers()
    galleries = [server for server in servers if server.name.startswith(GALLERY_PREFIX)]

    # setup a new voila-gallery instance
    create_server(cloud, args.tag)

    # Shutdown old servers
    stop_servers(cloud, galleries)


if __name__ == "__main__":
    main()

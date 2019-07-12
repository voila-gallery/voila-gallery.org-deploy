import argparse
import uuid

import openstack

# FIXME: change prefix to voila-gallery- or make this configurable
GALLERY_PREFIX = "voici-gallery-"
IMAGE = "Ubuntu 19.04"
# FIXME: switch to b2-30
FLAVOR = "b2-7"
USER_DATA_FILE = "./user-data.sh"


def create_server(cloud, tag):
    with open(USER_DATA_FILE) as f:
        user_data = f.read()

    instance_suffix = uuid.uuid4().hex[:6]
    cloud.create_server(
        image=IMAGE,
        flavor=FLAVOR,
        userdata=user_data.format(ref=tag),
        name=f"{GALLERY_PREFIX}{tag}-{instance_suffix}",
    )

    # FIXME: poll /api until ready

    # FIXME: add to an existing floating ip


def stop_servers(cloud, servers):
    for server in servers:
        cloud.delete_server(server.name, wait=True)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--tag',
        help='Suffix to add to the instance name (git commit hash)',
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

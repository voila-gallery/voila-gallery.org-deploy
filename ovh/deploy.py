import argparse
import uuid

import openstack

# FIXME: change prefix to voila-gallery- or make this configurable
GALLERY_PREFIX = "voici-gallery-"
IMAGE = "Ubuntu 19.04"
# FIXME: switch to b2-30
FLAVOR = "b2-7"

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

# Create the new instance
with open('./user-data.sh') as f:
    user_data = f.read()

instance_suffix = uuid.uuid4().hex[:6]
cloud.create_server(
    image=IMAGE,
    flavor=FLAVOR,
    userdata=user_data.format(ref=args.tag),
    name=f"{GALLERY_PREFIX}{args.tag}-{instance_suffix}",
)

# FIXME: poll /api until ready

# FIXME: add to an existing floating ip

# Shutdown old servers
for gallery in galleries:
    cloud.delete_server(gallery.name, wait=True)

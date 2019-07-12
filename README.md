# voila-gallery.org-deploy

Configuration and deployment files for [voila-gallery.org](https://voila-gallery.org)

At the moment the gallery is deployed as a plugin for [The Littlest JupyterHub](https://tljh.jupyter.org), running on a single [OVH](https://ovh.com) instance.

## Initial setup

Retrieve the `openrc.sh` file for the `voila-gallery-deploy` user.

```bash
source openrc.sh
cd ovh/
./setup.sh
```

## Deploy a new version of the gallery

The tag should correspond to a git hash for the [gallery repo](https://github.com/voila-gallery/gallery).

```bash
source openrc.sh
cd ovh/
python deploy.py --tag c0ab38a
```

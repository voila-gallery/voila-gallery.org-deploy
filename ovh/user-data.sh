#!/bin/bash
curl https://raw.githubusercontent.com/jupyterhub/the-littlest-jupyterhub/master/bootstrap/bootstrap.py \
 | sudo python3 - \
   --plugin git+https://github.com/voila-gallery/gallery@{ref}#"egg=tljh-voila-gallery&subdirectory=tljh-voila-gallery"


sudo tljh-config set https.enabled true
sudo tljh-config set https.letsencrypt.email contact@voila-gallery.org
sudo tljh-config add-item https.letsencrypt.domains voila-gallery.org

sudo tljh-config reload proxy

#!/bin/bash

cd ~/program/HTML_CSS/natsuzora_portal
python add.py
git add .
git commit -m "動画の追加・更新"
git push

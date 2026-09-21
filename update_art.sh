#!/bin/bash

cd ~/program/HTML_CSS/natsuzora_portal
python art_add.py
git add .
git commit -m "ファンアートの追加・更新"
git push

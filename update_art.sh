#!/bin/bash

cd ~/program/HTML_CSS/natsuzora_portal
source .venv/bin/activate 
python art_add.py
deactivate
git add .
git commit -m "ファンアートの追加・更新"
git push

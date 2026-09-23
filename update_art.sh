#!/bin/bash

cd ~/program/HTML_CSS/natsuzora_portal
source .venv/bin/activate 
python art_add.py
deactivate
echo "ファンアートの追加・更新"

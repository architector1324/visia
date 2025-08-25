#!/bin/bash

mkdir -p build

python -m venv ./build/venv
source ./build/venv/bin/activate

pip install --upgrade pip
pip install pillow ollama pyperclip pyperclipimg pyinstaller

cp ./visia.py -t build/
cd build

pyinstaller --onefile visia.py

mv dist/visia ../visia

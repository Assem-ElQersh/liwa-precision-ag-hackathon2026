#!/bin/bash
git init
git add .
git commit -m "Initial commit for Green Liwa PoC"
git branch -M main
git remote add origin https://github.com/Assem-ElQersh/liwa-precision-ag-hackathon2026.git
git remote set-url origin https://github.com/Assem-ElQersh/liwa-precision-ag-hackathon2026.git # In case it was already added
git push -u origin main

#!/usr/bin/env bash
ver=$(awk -F= '/version/ {print $2}' NnpaReporting/metadata.txt)
fname="nnpa-reporting-v${ver}.zip"
zip -r $fname NnpaReporting --exclude **__pycache__/* **.idea/* && echo -e "\n\n$fname packaged successfuly"

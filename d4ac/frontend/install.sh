#!/bin/bash

rm -rf ../d4ac_main/templates
rm -rf ../d4ac_main/static
mkdir ../d4ac_main/templates
cp dist/index.html ../d4ac_main/templates
cp -r dist/static ../d4ac_main/static
cp -r dist/images ../d4ac_main/static/images

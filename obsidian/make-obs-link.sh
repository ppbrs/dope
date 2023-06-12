#!/bin/bash

# ls -l /opt

OBSIDIAN_PATH=/opt/Obsidian-1.4.14.AppImage

rm ~/.local/bin/obs
echo rm returned $?

ln -s $OBSIDIAN_PATH ~/.local/bin/obs
echo ln returned $?

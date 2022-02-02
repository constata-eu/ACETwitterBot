#!/usr/bin/bash

echo "Stopping ace-tw-bot" &&
systemctl stop ace-tw-bot &&
echo "Updating repository..." &&
git pull &&
echo "Starting ace-tw-bot" &&
systemctl start ace-tw-bot && systemctl status ace-tw-bot'

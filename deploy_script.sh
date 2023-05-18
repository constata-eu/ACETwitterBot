#!/usr/bin/bash

if [ $1 == "production" ]
then
    echo "Stopping ace-tw-bot" &&
    systemctl stop ace-tw-bot &&
    echo "Updating repository..." &&
    git pull &&
    echo "Starting ace-tw-bot" &&
    systemctl start ace-tw-bot &&
    systemctl status ace-tw-bot
elif [ $1 == "staging" ]
then
    echo "Stopping staging-ace-tw-bot" &&
    systemctl stop staging-ace-tw-bot &&
    echo "Updating repository..." &&
    git pull &&
    echo "Starting staging-ace-tw-bot" &&
    systemctl start staging-ace-tw-bot &&
    systemctl status staging-ace-tw-bot
else
    echo "Must indicate production or staging:"
    echo "./deploy_script.sh staging/production"
fi
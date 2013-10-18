#!/bin/bash

if [[ "$(id -u)" -ne 0 ]]; then
    echo "[-] You need to be root,since we call apt-get"
    exit 1
fi
    echo "[x] Installing dependencies geoip psutil and pyglet"
    
    if hash apt-get 2>/dev/null; then

        apt-get install python-geoip python-psutil python-pyglet
    else
        aptitude install python-geoip python-psutil python-pyglet
    fi
    
    echo "[x] Downloading GeoLite Datatbase"
    wget  -P data/ http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz 
    echo  "[x] Unzipping GeoLite Database"
    gunzip data/GeoLiteCity.dat.gz


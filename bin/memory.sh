#!/usr/bin/env bash
FREE=`xl info | grep free_memory | awk '{print $3}'`
FREE_G=$(($FREE / 1024))
TOTAL=`xl info | grep total_memory | awk '{print $3}'`
TOTAL=$((TOTAL / 1024))

echo "Free Memory : $FREE Mb"
echo "Free Memory : $FREE_G Gb"
echo "Total Memory : $TOTAL Gb"

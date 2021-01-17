#!/bin/bash
/usr/sbin/xl list | awk 'NR>2 {print $1}'

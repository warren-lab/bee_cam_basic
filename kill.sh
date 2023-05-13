#!/bin/bash

pidfile="/home/pi/Field_Trap/Software/Image_Acquisition/kill.pid"

if [ -f $pidfile ]; then
   kill $(cat $pidfile)
fi


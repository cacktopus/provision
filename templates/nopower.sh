#!/bin/sh
echo 0x0 > /sys/devices/platform/soc/3f980000.usb/buspower
/usr/bin/tvservice -o

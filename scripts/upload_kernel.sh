#!/bin/bash

echo "Mounting..."
mount /dev/sdb1 mnt/
sleep 0.5
echo "Copying kernel..."
cp cmake-build-debug/Rpi/Top/kernel8.img mnt/
sleep 0.5
echo "Unmounting..."
umount mnt/
sleep 0.5



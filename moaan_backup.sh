#!/bin/bash

set -x

./rkdeveloptool read 0 4194304 0-8192.img 
./rkdeveloptool read-partition security security.img
./rkdeveloptool read-partition uboot_a uboot_a.img
./rkdeveloptool read-partition uboot_b uboot_b.img
./rkdeveloptool read-partition waveform waveform.img
./rkdeveloptool read-partition trust_a trust_a.img
./rkdeveloptool read-partition trust_b trust_b.img
./rkdeveloptool read-partition misc misc.img
./rkdeveloptool read-partition dtbo_a dtbo_a.img
./rkdeveloptool read-partition dtbo_b dtbo_b.img
./rkdeveloptool read-partition vbmeta_a vbmeta_a.img
./rkdeveloptool read-partition vbmeta_b vbmeta_b.img
./rkdeveloptool read-partition boot_a boot_a.img
./rkdeveloptool read-partition boot_b boot_b.img
./rkdeveloptool read-partition backup backup.img
./rkdeveloptool read-partition cache cache.img
./rkdeveloptool read-partition metadata metadata.img
./rkdeveloptool read-partition baseparameter baseparameter.img
./rkdeveloptool read-partition super super.img
./rkdeveloptool read-partition logo_a logo_a.img
./rkdeveloptool read-partition logo_b logo_b.img
read -p "Back up user data? (This maybe a waste of space) Y|N" userdata
userdata=$(echo $userdata | tr y Y)
if [[ ${userdata} = "Y" ]]; then
	./rkdeveloptool read-partition userdata userdata.img
fi


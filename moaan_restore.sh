#!/bin/bash

set -x

#./rkdeveloptool write 0 4194304 0-8192.img 
./rkdeveloptool write-partition security security.img
./rkdeveloptool write-partition uboot_a uboot_a.img
./rkdeveloptool write-partition uboot_b uboot_b.img
./rkdeveloptool write-partition waveform waveform.img
./rkdeveloptool write-partition trust_a trust_a.img
./rkdeveloptool write-partition trust_b trust_b.img
./rkdeveloptool write-partition misc misc.img
./rkdeveloptool write-partition dtbo_a dtbo_a.img
./rkdeveloptool write-partition dtbo_b dtbo_b.img
./rkdeveloptool write-partition vbmeta_a vbmeta_a.img
./rkdeveloptool write-partition vbmeta_b vbmeta_b.img
./rkdeveloptool write-partition boot_a boot_a.img
./rkdeveloptool write-partition boot_b boot_b.img
./rkdeveloptool write-partition backup backup.img
./rkdeveloptool write-partition cache cache.img
./rkdeveloptool write-partition metadata metadata.img
./rkdeveloptool write-partition baseparameter baseparameter.img
./rkdeveloptool write-partition super super.img
./rkdeveloptool write-partition logo_a logo_a.img
./rkdeveloptool write-partition logo_b logo_b.img
#./rkdeveloptool write-partition userdata userdata.img


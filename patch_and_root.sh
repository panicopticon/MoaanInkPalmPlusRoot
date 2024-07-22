#!/bin/bash

set -x

#if rkdeveloptool is in some other directory, uncomment the below and adjust as needed
#PATH=$PATH:/where/rkdeveloptool/is

UBOOT_MD5=0f68e6e1f944bdafc62241c356dd4d04
PATCH_UBOOT_MD5=4d523d84e2bdb07da72e00927960a394
BOOT_IMAGE_MD5=ae4c07ebc10feccfdaa0fcde9b0a003c
MAGISK_BOOT_IMAGE_MD5=11c381fe546aa3d838120329cd32217b

echo "Using adb to reboot to Rockchip loader"
adb reboot loader

echo "Backing up existing uboot_a and uboot_b"
rkdeveloptool read-partition uboot_a uboot_a.img
rkdeveloptool read-partition uboot_b uboot_b.img
if [[ !( $(md5sum uboot_a.img | cut -d ' ' -f 1) == ${UBOOT_MD5} && $(md5sum uboot_b.img | cut -d ' ' -f 1) == ${UBOOT_MD5} ) ]]; then
	echo "uboot_a.img || uboot_b.img do not match expected md5sum"
	exit 1
fi

if [[ !( $(md5sum panic_uboot_patched.img | cut -d ' ' -f 1) == ${PATCH_UBOOT_MD5} ) ]]; then
	echo "panic_uboot_patched.img does not match expected md5sum"
	exit 1
fi

echo "Flashing patched uboot to boot_a"
rkdeveloptool write-partition uboot_a panic_uboot_patched.img
rkdeveloptool read-partition uboot_a uboot_a_test.img

if [[ !( $(md5sum uboot_a_test.img | cut -d ' ' -f 1) == ${PATCH_UBOOT_MD5} ) ]]; then
	echo "uboot_a_test.img does not match expected md5sum"
	echo "this is bad, you probably want to write the backup back." 
	exit 1
fi

echo "Attempting to reboot phone"
rkdeveloptool reboot

read -p "Press enter when Android has booted to issue a reboot back to Rockchip loader"
adb reboot loader

read -p "Consider pausing and backing up your entire device, press enter to continue"

if [[ !( $(md5sum panic_magisk_boot.img | cut -d ' ' -f 1) == ${MAGISK_BOOT_IMAGE_MD5} ) ]]; then
	echo "panic_magisk_boot.img does not match expected md5sum"
	exit 1
fi

rkdeveloptool read-partition boot_a boot_a.img
rkdeveloptool read-partition boot_b boot_b.img
if [[ !( $(md5sum boot_a.img | cut -d ' ' -f 1) == ${BOOT_IMAGE_MD5} && $(md5sum boot_b.img | cut -d ' ' -f 1) == ${BOOT_IMAGE_MD5} ) ]]; then
	echo "boot_a.img || boot_b.img do not match expected md5sum"
	exit 1
fi

rkdeveloptool write-partition boot_a panic_magisk_boot.img
rkdeveloptool read-partition boot_a boot_a_test.img

if [[ !( $(md5sum boot_a_test.img | cut -d ' ' -f 1) == ${MAGISK_BOOT_IMAGE_MD5} ) ]]; then
	echo "boot_a_test.img does not match expected md5sum"
	echo "this is bad, you probably want to write the backup back." 
	exit 1
fi

rkdeveloptool reboot

echo "Great success?"
echo "Hopefully you're booting into Android now. When that's done, install Magisk, run it and it it do its things."

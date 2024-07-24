# Moaan (Moan) inkPalm Plus
The Moaan inkPalm Plus (墨案迷你阅 Plus) is a  phone sized Android 11 eInk tablet. Hardware wise it is quite similar to the [PineNote](https://wiki.pine64.org/wiki/PineNote) but has a smaller screen, less ram and less ROM. The fact that this is the same platform as the PineNote is excellent, as they're already done most of the work and we have an extensive base to work from. 

## Device Specs
- Rockchip RK3566 (4x ARM Cortex-A55 1.8GHz)
- 2 GB of RAM
- 64 GB of flash
- Wifi, Bluetooth
- 5.84-inch eInk display (1440 x 720)
- Customized Android 11

# Root Technique
I was unable to locate a root technique for this device, however my ability to search in Chinese is limited to what Google Translate is able to assist with so its probable I missed something. After some playing around I was able to more or less directly adapt the [PineNote u-Boot Fix/Root](https://github.com/DorianRudolph/pinenotes/blob/main/README.md#fix-uboot) approach.

## Overview
As detailed in the PineNote documentation, as well as a variety of other places, the RockChip loader used by these devices either has a bug or an intentional limit that prevents RockChip's loader from reading data past the first 32MB (`0x2000000`) of flash. Bytes past this limit are replaced by `0xCC`. This is a problem as the `boot_a` and `boot_b` partitions both sit beyond that boundary. Once we have a copy of those partitions rooting using [Magisk](https://github.com/topjohnwu/Magisk) is straight forward. When unable to extract the boot partition using `fastboot` or other manufacturer tools, the fallback is to extract the image from a full update file (differential updates may not work), unfortunately as at the time of writing no updates were available or able to be located.

## Requirements
This was done on a modern Linux, if that's not what you're using, good luck.
- [rkdeveloptool](https://github.com/rockchip-linux/rkdeveloptool) to read and write the partitions from `loader` mode
-- Other RockChip loader utilities may work, but  are untested
- [adb (Android Debug Bridge)](https://developer.android.com/tools/adb), binary copies can be downloaded [here](https://developer.android.com/tools/releases/platform-tools)
- Device in `loader` mode

### Entering loader Mode
`loader` mode can be accessed by doing one of the following 
- From Android `adb reboot loader`
- From Android `adb reboot fastboot` select `bootloader` from interactive menu
- Maybe some magic button presses at power on? I didn't have any luck with this

### Exiting loader Mode
- `rkdeveloptool reboot`
- Hold the power button for ~20 seconds, the backlight should turn off, release the power button, hold the power button until the screen refreshes, the device should now boot normally

## Partitions
```
    LBA start (sectors)  LBA end (sectors)  Size (bytes)       Name                
00                 8192              16383       4194304       security
01                16384              24575       4194304       uboot_a
02                24576              32767       4194304       uboot_b
03                32768              36863       2097152       waveform
04                36864              45055       4194304       trust_a
05                45056              53247       4194304       trust_b
06                53248              61439       4194304       misc
07                61440              69631       4194304       dtbo_a
08                69632              77823       4194304       dtbo_b
09                77824              79871       1048576       vbmeta_a
10                79872              81919       1048576       vbmeta_b
11                81920             278527     100663296       boot_a
12               278528             475135     100663296       boot_b
13               475136            1261567     402653184       backup
14              1261568            2047999     402653184       cache
15              2048000            2080767      16777216       metadata
16              2080768            2082815       1048576       baseparameter
17              2082816           12568575    5368709120       super
18             12568576           12601343      16777216       logo_a
19             12601344           12634111      16777216       logo_b
20             12634112          122142655   56068374528       userdata
```
 As you can see, we will be unable to correctly dump data beyond `dtb_a`, the last partition below the 32MB boundary, data beyond the 32M boundary is replaced with `0xCC` bytes. 

## Prepatched images for rooting
If you don't implicitly trust randos on the internet or want to know how this was done, see the Manual Approach section below. The provided rooted  `boot` image was created using `Magisk-v27.0.apk`.

Download the images from the release section, run the steps below by hand, or use `patch_and_root.sh` to execute the steps automatically.

 - Enter `loader` mode as described above
 - Read `boot_a` by running `rkdeveloptool read-partition uboot_a uboot_a.img`
 - Read `boot_b` by running`rkdeveloptool read-partition uboot_b uboot_b.img`
 - `md5sum uboot_a.img uboot_b.img` both should be `0f68e6e1f944bdafc62241c356dd4d04`, if not **STOP AND DO NOT CONTINUE**, you have a different `uboot` than mine and this will break your device, see the Manual Approach to create a patch that matches your device.
 - Write `boot_a` by running `rkdeveloptool write-partition uboot_a panic_uboot_patched.img
` **Only do one partition at this time, as if something goes wrong we can boot the fallback b side!!**
- Read `boot_a` by running `rkdeveloptool read-partition uboot_a uboot_a_test.img`
- Run `md5sum panic_uboot_patched.img uboot_a_test.img` and ensure that the md5s match, should be (`4d523d84e2bdb07da72e00927960a394`), if not something has gone badly wrong 
- Reboot the device by running `rkdeveloptool reboot`, or failing that holding the power button as described above
- The device should reboot into Android, if so the patch was likely successful
- Enter `loader` mode as described above
- Consider pausing and backing up your entire device, 
- Run `rkdeveloptool read-partition boot_a boot_a.img`
- Run `rkdeveloptool read-partition boot_b boot_b.img`
 - `md5sum boot_a.img boot_b.img` both should be `ae4c07ebc10feccfdaa0fcde9b0a003c` if not **STOP AND DO NOT CONTINUE**, you have a different `boot` than mine and this will break your device, see the Manual Approach to create a `boot` that matches your device.
- Run `rkdeveloptool write-partition boot_a panic_magisk_boot.img`
- Run `rkdeveloptool read-partition boot_a boot_a_test.img`
- Run `md5sum panic_magisk_boot.img boot_a_test.img` and ensure that the md5s match, if not something has gone badly wrong
- Reboot the device by running `rkdeveloptool reboot`, or failing that holding the power button as described above
- The device should reboot into Android, if so the root was likely successful. Install Magisk (if you haven't already) and start it, it should indicate that the device is rooted, but needs additional setup, let it complete this a device reboot will be required.

Assuming that all worked, you may wish to also replace the `uboot-b` partition.

## Manual Approach
 - Enter `loader` mode as described above
 - Read `boot_a` by running `rkdeveloptool read-partition uboot_a uboot_a.img`
 - Read `boot_b` by running`rkdeveloptool read-partition uboot_b uboot_b.img`
 - `md5sum uboot_a.img uboot_b.img` both should be the same (likely `0f68e6e1f944bdafc62241c356dd4d04`), if they aren't you'll need to do some additional sanity checking for the location and patch
 - Extract the `uboot.bin` using the python script, saving off a copy of the output
 - Patch the `uboot.bin`
 - Create a`uboot_patched.img` using the `moaan_uboot_img.py` script
 -- `moaan_uboot_img.py d uboot_a uboot.bin`
 -- Try the automatic (?) patcher `/moaan_uboot_patcher.py uboot.bin uboot_patched.bin` or do it yourself
 --`moaan_uboot_img.py p uboot_a uboot_patched.bin uboot_patched.img`
 - Write `boot_a` by running `rkdeveloptool write-partition uboot_a uboot_patched.img
` **Only do one partition at this time, as if something goes wrong we can boot the fallback b side!!**
- Read `boot_a` by running `rkdeveloptool read-partition uboot_a uboot_a_test.img`
- Run `md5sum uboot_patched.img uboot_a_test.img` and ensure that the md5s match, should be (`4d523d84e2bdb07da72e00927960a394`), if not something has gone badly wrong 
- Reboot the device by running `rkdeveloptool reboot`, or failing that holding the power button as described above
- The device should reboot into Android, if so the patch was likely successful
- Enter `loader` mode as described above
- Run `rkdeveloptool read-partition boot_a boot_a.img`
- Run `rkdeveloptool read-partition boot_b boot_b.img`
 - `md5sum boot_a.img boot_b.img` both should be the same (likely `ae4c07ebc10feccfdaa0fcde9b0a003c`), if that's not the md5 do some addition checking to make sure your backups aren't full of `0xCC`s (hexdump, etc).
 - Patch one of boot images using Magisk
- Run `rkdeveloptool write-partition boot_a magisk_boot.img`
- Run `rkdeveloptool read-partition boot_a boot_a_test.img`
- Run `md5sum magisk_boot.img boot_a_test.img` and ensure that the md5s match, if not something has gone badly wrong
- Reboot the device by running `rkdeveloptool reboot`, or failing that holding the power button as described above
- The device should reboot into Android, if so the root was likely successful. Install Magisk (if you haven't already) and start it, it should indicate that the device is rooted, but needs additional setup, let it complete this a device reboot will be required.

Assuming that all worked, you may wish to also replace the `uboot-b` partition.
 
### uboot patch details
Based on the work detailed [here](https://github.com/DorianRudolph/pinenotes/blob/main/README.md#fix-uboot), we will do the same patch in a different location, this changes a `b.ls` (`49 01 00 54`) into a `b` (`0A 00 00 14`) for this device that's at offset `0x12B74`in the `uboot.bin` extracted from the `boot_{a|b}` image using `moaan_uboot_img.py`. This patching is automated can be done automatically using `moaan_uboot_patcher.py`.

Original:
 ```
 04 18 40 B9  F3 0B 00 F9  81 00 01 8B  24 00 02 8B
9F 40 40 F1 [49 01 00 54] F3 03 02 AA  81 19 80 52
42 D8 77 D3  E0 03 03 AA  B3 96 02 94  E0 03 13 2A
```
Patched:
```
04 18 40 B9  F3 0B 00 F9  81 00 01 8B  24 00 02 8B
9F 40 40 F1 [0A 00 00 14] F3 03 02 AA  81 19 80 52
42 D8 77 D3  E0 03 03 AA  B3 96 02 94  E0 03 13 2A
```
If you want to confirm that the patch is correct, you can import the in Ghidra and compare the before and after results. The Ghidra processor type is `AARCH64 v8A 64 little default`, accept the defaults and allow it process the file. `Search -> Program Text`, `Selected Feilds` check only `Instruction Operands`, Search for `#0x10, LSL #12` filter for`cmp`s, alternatively do the same search but for `0xCC` and then filter for `mov`s; either way there should only be a handful of results to check. The decompiled source should look more or less as follows:
```c
ulong FUN_00012b58(long param_1,long param_2,ulong param_3,undefined8 param_4)

{
  if ((ulong)*(uint *)(param_1 + 0x18) + param_2 + param_3 < 0x10001) {
    param_3 = FUN_00046db4(param_1 + 0x28);
  }
  else {
    FUN_000b8654(param_4,0xcc,param_3 << 9);
    param_3 = param_3 & 0xffffffff;
  }
  return param_3;
}
```
You can then right click on the `b.ls` instruction and select `Patch Instruction` and change it to a `b`, then copy new opcode out. I suspect that this set of techniques will generalize to a bunch of different Rockchip `uboot`s as discussion on various [threads](https://xdaforums.com/t/tool-rkdumper-utility-for-backup-firmware-of-rockchips-devices.2915363/) show folks having this exact issue.

# If things go wrong
- Hopefully you made a backup, you should be able to restore the images you messed up
- If you didn't there will be a copy of the dumps on archive.org, if its not there yet, poke me

# Box Copy
To aid people in finding this information
| Chinese  | English |
|--|--|
| 墨案迷你阅 Plus | InkPalm Plus |
| 产品名称:电子书阅读器(平板电脑) | Product name: e-book reader (tablet) |
| 产品型号:inkPalm Plus |  Product model: inkPalm Plus |
| CMIIT ID: 2022AP4963 | CMIIT ID: 2022AP4963 |
| 产品尺寸:158.9 x 78.6 x 6.9mm | Product size: 158.9 x 78.6 x 6.9mm |
| 显 示:E Ink 5.84英寸276ppi | Display: E Ink 5.84 inches 276ppi |
| 无线连接:WiFi 2.4G&5G,蓝牙5.0 | Wireless connection: WiFi 2.4G&5G, Bluetooth 5.0 |
| 输 入:5V 1.5A | Input: 5V 1.5A |
| 包装内含:主机、USB充电线、说明书 | Package includes: host, USB charging cable, manual |
| 执行标准:GB17625.1-2022,GB 4943.1-2022 | Implementation standard: GB17625.1-2022, GB 4943.1-2022 |
| GB/T 9254.1-2021 |  GB/T 9254.1-2021 |
| 操作系统:Android 11 | Operating system: Android 11 |
| 生产者:上海墨案智能科技有限公司 | Manufacturer: Shanghai Moan (Moaan) Intelligent Technology Co., Ltd. |
| 地址:上海市闵行区紫星路588号2幢1197室 | Address: Room 1197, Building 2, No. 588 Zixing Road, Minhang District, Shanghai |
| 服务电话:400-071-0880 | Service phone: 400-071-0880 |
| 生产企业:惠州嘉尚电子科技有限公司 | Manufacturer: Huizhou Jiashang Electronic Technology Co., Ltd. |
| 地址:惠州市小金口镇小铁区山子村(侨兴工业园)3#厂房 | Address: Factory 3#, Shanzi Village, Xiaotie District, Xiaojinkou Town, Huizhou City (Qiaoxing Industrial Park) |


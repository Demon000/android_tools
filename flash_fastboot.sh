ADB_STASTE=$(adb get-state)

if [ "$ADB_STASTE" = "device" ]; then
	BOOTLOADER_PARTS="boot vendor_boot dtbo recovery"
	CAN_REBOOT_TO_BL=1

	for part in "$@"
	do
		echo "$BOOTLOADER_PARTS" | grep -w -q "$part"
		if [ $? -ne 0 ]; then
			CAN_REBOOT_TO_BL=0
		fi
	done

	if [ "$CAN_REBOOT_TO_BL" = "1" ]; then
		adb reboot bootloader
	else
		adb reboot fastboot
	fi
fi

for part in "$@"
do
	fastboot flash "$part" "$part.img"
done

fastboot reboot

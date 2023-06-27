ADB_STASTE=$(adb get-state)

get_part_i() {
	name="$1"
	index="$2"
	parts=(${name//:/ })
	echo "${parts[$index]}"
}

get_real_part() {
	get_part_i "$1" 0
}

get_img_part() {
	get_part_i "$1" 1
}

if [ "$ADB_STASTE" = "device" ]; then
	BOOTLOADER_PARTS="boot vendor_boot dtbo recovery"
	CAN_REBOOT_TO_BL=1

	for part in "$@"
	do
		real_part=$(get_real_part "$part")
		echo "$BOOTLOADER_PARTS" | grep -w -q "$real_part"
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
	real_part=$(get_real_part "$part")
	img_part=$(get_img_part "$part")
	if [ -z "$img_part" ]; then
		img_part="$real_part.img"
	fi
	fastboot flash "$real_part" "$img_part"
done

fastboot reboot

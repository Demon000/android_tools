#!/usr/bin/env python3

import bisect
import subprocess
import time

from threading import Thread


def run_shell_cmd(*args):
    return subprocess.check_output(["adb", "shell"] + [*args])


def get_shell_cmd_int(*args):
    output = run_shell_cmd(*args)
    return int(output)


def set_shell_cmd_int(value, *args):
    run_shell_cmd("echo", str(value), " > ", *args)


PANEL0_BACKLIGHT_PATH = "/sys/class/backlight/panel0-backlight/"
MAX_BRIGHTNESS_PATH = PANEL0_BACKLIGHT_PATH + "max_brightness"
BRIGHTNESS_PATH = PANEL0_BACKLIGHT_PATH + "brightness"

DISPLAY_PATH = "/sys/devices/platform/soc/soc:qcom,dsi-display-primary/"
DIM_ALPHA_PATH = DISPLAY_PATH + "fod_dim_alpha"
FORCE_FOD_UI_PATH = DISPLAY_PATH + "force_fod_ui"


def get_max_brightness():
    return get_shell_cmd_int("cat", MAX_BRIGHTNESS_PATH)


def get_min_brightness():
    return 1


def set_brightness(brightness):
    set_shell_cmd_int(brightness, BRIGHTNESS_PATH)


def set_dim_alpha(alpha):
    set_shell_cmd_int(alpha, DIM_ALPHA_PATH)


def get_dim_alpha():
    return get_shell_cmd_int("cat", DIM_ALPHA_PATH)


def set_force_fod_ui(status):
    set_shell_cmd_int(status, FORCE_FOD_UI_PATH)


FORCE_FOD_UI_SWITCH_TIME = 1 / 10

exit_worker_thread = False
switch_fod_ui = False
dim_alpha = 0


def worker_thread_target():
    global exit_worker_thread
    global switch_fod_ui
    global dim_alpha

    while not exit_worker_thread:
        if switch_fod_ui:
            set_dim_alpha(dim_alpha)
            set_force_fod_ui(1)

        time.sleep(FORCE_FOD_UI_SWITCH_TIME)

        if switch_fod_ui:
            set_force_fod_ui(0)
            set_dim_alpha(-1)

        time.sleep(FORCE_FOD_UI_SWITCH_TIME)


worker_thread = Thread(target=worker_thread_target)
worker_thread.start()

brightness_alpha_pairs = []


def print_help():
    print("""Commands:
		quit, q: Quit
		print, p: Print LUT
		fill, f: Create a LUT based on current values
		calibrate, c: Calibrate LUT
	""")


def print_pair(pair):
    print("{}: {}".format(pair[0], pair[1]))


def print_pairs():
    print("{} pairs".format(len(brightness_alpha_pairs)))
    for pair in brightness_alpha_pairs:
        print_pair(pair)


def add_pair(pair):
    bisect.bisect(brightness_alpha_pairs, pair, key=lambda p: p[0])


def fill_pairs(length):
    global brightness_alpha_pairs

    brightness_alpha_pairs = []

    max_brightness = get_max_brightness()
    min_brightness = get_min_brightness()

    print("Max brightness: {}".format(max_brightness))

    set_force_fod_ui(0)
    set_dim_alpha(-1)

    for i in range(length):
        brightness = (
            i * (max_brightness - min_brightness) // (length - 1) + min_brightness
        )
        set_brightness(brightness)
        alpha = get_dim_alpha()
        pair = [brightness, alpha]
        brightness_alpha_pairs.append(pair)
        print_pair(pair)


def calibrate_one(pair):
    global dim_alpha
    global switch_fod_ui

    switch_fod_ui = True
    exit = False

    set_brightness(pair[0])

    print("""Commands:
		q: Quit
		n: Next LUT value
		+: Add 1 to the dimming alpha
		+x: Add x to the dimming alpha
		-: Substract one from the dimming alpha
		-x: Substract x from the dimming alpha
		=x: Set the dimming value to x
	""")

    while True:
        print_pair(pair)

        dim_alpha = pair[1]
        mod = input("Modifier: ")
        new_dim_alpha = dim_alpha
        mod_int = 0

        if len(mod) == 0:
            continue

        if mod == "q":
            exit = True
            break
        elif mod == "n":
            break
        elif mod[0] == "+":
            try:
                mod_int = int(mod[1:])
            except:
                mod_int = +1

            new_dim_alpha = new_dim_alpha + mod_int
        elif mod[0] == "-":
            try:
                mod_int = int(mod[1:])
            except:
                mod_int = 1

            new_dim_alpha = new_dim_alpha - mod_int
        elif mod[0] == "=":
            try:
                new_dim_alpha = int(mod[1:])
            except:
                pass

        if new_dim_alpha > 255:
            new_dim_alpha = 255

        if new_dim_alpha < 0:
            new_dim_alpha = 0

        pair[1] = dim_alpha = new_dim_alpha

    switch_fod_ui = False

    return exit


def calibrate():
    for pair in brightness_alpha_pairs:
        exit = calibrate_one(pair)
        if exit:
            break


while True:
    print_help()

    command = input("Command: ")

    if command == "quit" or command == "q":
        break
    elif command == "print" or command == "p":
        print_pairs()
    elif command == "fill" or command == "f":
        try:
            length = int(input("Length: "))
            fill_pairs(length)
        except:
            pass
    elif command == "calibrate" or command == "c":
        calibrate()
    else:
        print("Invalid command")
        print_help()

exit_worker_thread = True
worker_thread.join()

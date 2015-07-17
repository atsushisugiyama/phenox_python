#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
import phenox as px

if __name__ == "__main__":
    led_target = 0
    led_is_on = False

    while True:
        sleep(1)
        px.set_led(led_target, led_is_on)
        led_is_on = not led_is_on

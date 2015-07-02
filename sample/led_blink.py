#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
import phenox as px

if __name__ == "__main__":
    led_target = 0
    led = 0
    px.init_chain()

    while not px.get_cpu1ready():
        pass

    try:
        while True:
            sleep(1)
            if led:
                px.set_led(led_target, 1)
                led = 0
            else:
                px.set_led(led_target, 0)
                led = 1                
    finally:
        """if using C language, close_chain is needed.

        but in the case of Python, garbage collection runs
        in the end of the program and memory will be free,
        so "close_chain" is not needed.

        rather, calling "close_chain" causes Segmentation Fault because 
        1. "close_chain()" explicitly frees memory
        2. program ends
        3. Python interpreter tries to free memory including
            where "close_chain()" already freed.
        """
        #px.close_chain()
        pass


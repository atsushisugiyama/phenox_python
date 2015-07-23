#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time 

import phenox as px

def main():
    duration = 3.0
    filename = "testsound.raw"

    print("sound record({0} sec) starts after press ENTER".format(duration))
    raw_input()
    print("now recording...")

    started = px.set_sound_recordquery(3.0)
    if not started:
        print("some problem occurred for sound recording. program ends.")
        return

    time.sleep(duration)
    print("recording ended: start save raw sound file")
    while True:
        sound = px.get_sound(duration, restype='str')
        if not sound:
            continue
        with open(filename, "wb") as f:
            f.write(sound)
        break
    print("raw sound was saved to '{0}'".format(filename))

if __name__ == "__main__":
    main()

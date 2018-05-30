#!/usr/bin/python
# -*- encoding: utf-8 -*-
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DIR_ASSETS = 'assets'
DIR_COSTUMES = os.path.join(BASE_DIR, DIR_ASSETS, 'costumes')
DIR_BACKDROPS = os.path.join(BASE_DIR, DIR_ASSETS, 'backdrops')
DIR_SOUNDS = os.path.join(BASE_DIR, DIR_ASSETS, 'sounds')

COSTUME_KEYS = ('name', 'md5', 'type', 'tags', 'info')
BACKDROP_KEYS = ('name', 'md5', 'type', 'tags', 'info')
SOUND_KEYS = ('name', 'md5', 'sampleCount', 'rate', 'format', 'tags')

def generate_backdrop():
    for (path, i in os.walk(DIR_BACKDROPS):


if __name__ == '__main__':
    pass

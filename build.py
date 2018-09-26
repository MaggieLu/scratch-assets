#!/usr/bin/python
# -*- encoding: utf-8 -*-
import os, hashlib, json, re, zipfile 
from shutil import copyfile
from PIL import Image
from xml.dom import minidom
# import wave
# from scipy.io.wavfile import read
import audioread

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DIR_ASSETS = 'assets'
DIR_COSTUMES = os.path.join(BASE_DIR, DIR_ASSETS, '角色库')
DIR_BACKDROPS = os.path.join(BASE_DIR, DIR_ASSETS, '背景库')
DIR_SOUNDS = os.path.join(BASE_DIR, DIR_ASSETS, '声音库')

DIR_BUILD = 'build'
DIR_JSON = 'json'
DIR_BACKDROPS_MD5 = os.path.join(BASE_DIR, DIR_BUILD, DIR_ASSETS, 'backdrops')
DIR_COSTUMES_MD5 = os.path.join(BASE_DIR, DIR_BUILD, DIR_ASSETS, 'costumes')
DIR_SOUNDS_MD5 = os.path.join(BASE_DIR, DIR_BUILD, DIR_ASSETS, 'sounds')
# DIR_SPRITES_MD5 = os.path.join(BASE_DIR, DIR_BUILD, DIR_ASSETS, 'sprites')
DIR_EXTRACT = os.path.join(BASE_DIR, DIR_BUILD, DIR_ASSETS, 'extracted_costumes')

COSTUME_KEYS = ('name', 'md5', 'type', 'tags', 'info')
BACKDROP_KEYS = ('name', 'md5', 'type', 'tags', 'info')
SOUND_KEYS = ('name', 'md5', 'sampleCount', 'rate', 'format', 'tags')
URL = 'https://codepku.cdn.....'

def generate_backdrops():
    '''
    create brackdrops.json
    create md5 backdrop files
    '''
    backdrops = []
    for root, dirs, files in os.walk(DIR_BACKDROPS):
        for filename in files:
            full_path = os.path.join(root, filename)
            with open(full_path, "r") as f:
                data = f.read()
                md5name = hashlib.md5(data).hexdigest() + "." + filename.split(".")[1]
            current_dir = re.sub(r"(\S*/assets/)", "", full_path)
            tags = current_dir.split("/")[:-1]
            extension = os.path.splitext(full_path)[1]
            if extension == '.png':
                im = Image.open(full_path)
                width, height = im.size
                # width = 960 
                # height = 720
                info = [width, height, 2]
            elif extension == '.svg':
                doc = minidom.parse(full_path)
                view_box = [path.getAttribute('viewBox') for path in doc.getElementsByTagName('svg')]
                view_box = str(view_box[0]) # unicode of viewbox
                view_box_list = view_box.split(" ");
                width, height = view_box_list[2], view_box_list[3] # width = 480 height = 360
                info = [width, height, 1]
                doc.unlink()
            md5path = os.path.join(DIR_BACKDROPS_MD5, md5name)
            if not os.path.exists(md5path):
                copyfile(full_path, md5path) 
            backdrops.append({
               'name': filename.split('.')[0],
               'md5': md5name,
               'type': 'backdrop',
               'tags': tags,
               'info': info
               })
    json_path = os.path.join(BASE_DIR, DIR_BUILD, DIR_JSON, 'backdrops.json')
    with open(json_path, 'w') as outfile:
        json.dump(backdrops, outfile)

def generate_sounds():
    '''
    create sounds.json
    create md5 sound files
    '''
    sounds = []
    for root, dirs, files in os.walk(DIR_SOUNDS):
        for filename in files:
            full_path = os.path.join(root, filename)
            with open(full_path, 'r') as f:
                data = f.read()
                md5name = hashlib.md5(data).hexdigest() + "." + filename.split(".")[1]
            current_dir = re.sub(r"(\S*/assets/)", "", full_path)
            tags = current_dir.split("/")[1:-1]
            md5path = os.path.join(DIR_SOUNDS_MD5, md5name)
            with audioread.audio_open(full_path) as f:
                sample_rate = f.samplerate
                sample_count = int(f.channels * f.samplerate * f.duration)
            if not os.path.exists(md5path):
                copyfile(full_path, md5path) 
            sounds.append({
               "name": filename.split(".")[0],
               "md5": md5name,
               "sampleCount": sample_count,
               "rate": sample_rate,
               "format": "",
               "tags": tags
               })

    json_path = os.path.join(BASE_DIR, DIR_BUILD, DIR_JSON, 'sounds.json')
    with open(json_path, 'w') as outfile:
        json.dump(sounds, outfile)

def generate_costumes():
    '''
    create costumes.json
    create md5 costumes files
    '''
    costumes = []
    sprites = []
    # extract sprite2 files
    for root, dirs, files in os.walk(DIR_COSTUMES):
        for filename in files:
            full_path = os.path.join(root, filename)
            current_dir = re.sub(r"(\S*/assets/)", "", full_path)
            tags = current_dir.split("/")[:-1]
            extension = os.path.splitext(full_path)[1]
            extracted_path = os.path.join(DIR_EXTRACT, current_dir.split('.')[0])
            if extension == '.sprite2' and (not os.path.exists(extracted_path)):
                os.makedirs(extracted_path)
                with zipfile.ZipFile(full_path, 'r') as zip_file:
                    zip_file.extractall(extracted_path)
    
    # create json, md5 files
    for root, dirs, files in os.walk(DIR_EXTRACT):
        for filename in files:    
            full_path = os.path.join(root, filename)
            # origin_imgs.append(filename)
            if filename == "sprite.json":
                current_dir = re.sub(r"(\S*/assets/)", "", full_path)
                tags = current_dir.split("/")[2:-1]
                with open(os.path.join(root, filename)) as sprite:
                    cur_costumes = json.load(sprite)
                for costume in cur_costumes['costumes']:
                    costumes.append({
                        "name": costume['costumeName'],
                        "md5": costume['baseLayerMD5'],
                        "type": "costume",
                        "tags": tags,
                        "info": [costume['rotationCenterX'], costume['rotationCenterY'], costume['bitmapResolution']]
                        })
                    md5path = os.path.join(DIR_COSTUMES_MD5, costume['baseLayerMD5'])            
                    cur_img = str(costume['baseLayerID']) + '.' + costume['baseLayerMD5'].encode('utf8').split('.')[1]
                    for img in files:
                        if (img == cur_img) and (not os.path.exists(md5path)):
                            copyfile(os.path.join(root, img), md5path)

                if "sounds" in cur_costumes.keys():
                    sounds_len = len(cur_costumes["sounds"])
                else:
                    sounds_len = 0
                if "costumes" in cur_costumes.keys():
                    costumes_len = len(cur_costumes["costumes"])
                else:
                    costumes_len = 0
                sprites.append({
                    "name": cur_costumes["objName"],
                    "md5": cur_costumes["costumes"][0]["baseLayerMD5"],
                    "type": "sprite",
                    "tags": tags,
                    "info": [0, costumes_len, sounds_len],
                    "json": cur_costumes
                    })
            extension = os.path.splitext(full_path)[1]
            if extension == (".wav" or ".mp3"):
                with open(full_path, "r") as f:
                    data = f.read()
                    md5name = hashlib.md5(data).hexdigest() + "." + filename.split(".")[1]
                    md5path = os.path.join(DIR_SOUNDS_MD5, md5name)
                    with audioread.audio_open(full_path) as f:
                        if not os.path.exists(md5path):
                            copyfile(full_path, md5path) 
    costumes_path = os.path.join(BASE_DIR, DIR_BUILD, DIR_JSON, 'costumes.json')
    with open(costumes_path, 'w') as outfile:
        json.dump(costumes, outfile)
    
    sprites_path = os.path.join(BASE_DIR, DIR_BUILD, DIR_JSON, 'sprites.json')
    with open(sprites_path, 'w') as outfile:
        json.dump(sprites, outfile)

if __name__ == '__main__':
    generate_backdrops()
    generate_sounds()
    generate_costumes()

# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Name:        TextKeywordImage.py
# Purpose:     Generation of Images from Lines or Keywords in a Text
#
# Author:      Bradley Baker # BBradT at {gmail} dot com
#
# Created:     2018/05/26 (May 26 2018)
# Copyright:   (c) 2018 Bradley Baker
# License:     Please see License.txt for the terms under which this
#              software is distributed.
#-----------------------------------------------------------------------------

import os
import shutil
import string
from google_images_download import google_images_download
import cv2
from util import slugify, chunks
import numpy as np
import sys
import getopt
import configparser

def main(argv):
    global inputfile
    global outdir
    global outfile
    global img_limit
    global img_format
    global img_usage
    global size
    global sepchar
    global img_ctype
    global img_groups

    try:
        opts, args = getopt.getopt(argv,"hi:o:x:y:t:s:k:",["od=","ifile=","ofile=","odir=","res=","sepchar=","usage=","color=","groups="])
    except getopt.GetoptError:
        print('USAGE: TextKeywordImage.py -i <InputText> -o <OutputFileName>')
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print('TextKeywordImage.py -i <InputImage> [-o <OutputFile> -od <OutputDirectory>  -g <# Groups of Images> -r <Size> -l <Limit of Images> -u <Usage rights> -c <Color Type> -f <Image Format>]')
        elif opt in ("-i","--ifile"):
            inputfile = arg
        elif opt in ("-o","--ofile"):
            outfile = arg
        elif opt in ("-od","--odir"):
            outdir = arg
        elif opt in ("-r","--res"):
            size = int(arg)
        elif opt in ("-l","--limit"):
            img_limit = int(arg)
        elif opt in("-f","--format"):
            img_format = arg
        elif opt in("-s","--sepchar"):
            sepchar = arg
        elif opt in("-u","--usage"):
            img_usage = arg
        elif opt in("-c","--color"):
            img_ctype = arg
        elif opt in("-g","--groups"):
            img_groups = int(arg)

    response = google_images_download.googleimagesdownload()
    exclude=set(string.punctuation)
    title = inputfile.replace('.txt','')
    text = open(inputfile, 'r').read()
    print("Working on %s" % title)
    dir_name = os.path.join(outdir,title.replace(' ',sepchar)) + os.sep
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    imgs = []
    for i, line in enumerate(text.split('\n')):
        line_stripped = ''.join(ch for ch in line.strip() if ch not in exclude)
        if line_stripped == '':
            continue
        abs_image_paths = response.download({'keywords':line_stripped,
                                             'limit':img_limit,
                                             'format':img_format,
                                             'color-type':img_ctype,
                                             'usage_rights':img_usage,
                                             'output_directory':dir_name,
                                             'no_directory':True})
        for keyword, imgpath in abs_image_paths.items():
            if imgpath == []:
                continue
            _, ext = os.path.splitext(imgpath[0])
            if imgpath[0] == '':
                continue
            kw = slugify(keyword)
            if len(kw) > 50:
                kw = kw[:50]
            new =  dir_name + 'line_%d_%s' % ((i+1), kw)
            new += ext
            try:
                shutil.copyfile(imgpath[0],  new)
            except Exception:
                pass
            os.remove(imgpath[0])
            img = cv2.imread(new)
            img = cv2.resize(img, (size, size))
            try:
                cv2.imwrite(new, img)
                imgs.append(cv2.imread(new))
            except Exception:
                pass
    if imgs==[]:
        return
    imgs_groups = chunks(imgs, min(img_groups, len(imgs)))
    album = np.mean(np.array(imgs_groups[0], dtype=np.uint8),0)
    for i in range(len(imgs_groups)-1):
        if type(imgs[i+1]) is not np.ndarray:
            continue
        album += np.mean(np.array(imgs_groups[i+1], dtype=np.uint8), 0)
    album=cv2.resize(album, (512, 512))
    album=np.array(album,dtype=np.uint8)
    cv2.imwrite(dir_name+os.sep+outfile, album)

if __name__ == '__main__':
    global inputfile
    global outdir
    global outfile
    global img_limit
    global img_format
    global img_usage
    global size
    global sepchar
    global img_ctype
    global img_groups
    config = configparser.ConfigParser()
    config.readfp(open("config.cfg"))

    #Read Default values from config file prior to argument parsing
    inputfile = config.get("io","default_tki_infile")
    outfile = config.get("io","default_tki_outfile")
    outdir = config.get("io","default_outdir")
    img_limit = config.getint("tki", "default_img_limit")
    img_format = config.get("tki", "default_img_format")
    img_usage = config.get("tki", "default_img_usage")
    size = config.getint("tki", "default_size")
    img_ctype = config.get("tki", "default_img_ctype")
    img_groups = config.getint("tki", "default_img_groups")
    sepchar = config.get("tki", "default_sepchar")
    main(sys.argv[1:])   
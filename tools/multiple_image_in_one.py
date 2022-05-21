import argparse
from PIL import Image
import numpy as np
import os
import pathlib


# referring to https://note.nkmk.me/python-pillow-concat-images/
def get_concat_h_multi_resize(im_list, resample=Image.BICUBIC):
    min_height = min(im.height for im in im_list)
    im_list_resize = [im.resize((int(im.width * min_height / im.height), min_height),resample=resample)
                      for im in im_list]
    total_width = sum(im.width for im in im_list_resize)
    dst = Image.new('RGB', (total_width, min_height))
    pos_x = 0
    for im in im_list_resize:
        dst.paste(im, (pos_x, 0))
        pos_x += im.width
    return dst


def get_concat_v_multi_resize(im_list, resample=Image.BICUBIC):
    min_width = min(im.width for im in im_list)
    im_list_resize = [im.resize((min_width, int(im.height * min_width / im.width)),resample=resample)
                      for im in im_list]
    total_height = sum(im.height for im in im_list_resize)
    dst = Image.new('RGB', (min_width, total_height))
    pos_y = 0
    for im in im_list_resize:
        dst.paste(im, (0, pos_y))
        pos_y += im.height
    return dst


def get_concat_tile_resize(im_list_2d, resample=Image.BICUBIC):
    im_list_v = [get_concat_h_multi_resize(im_list_h, resample=resample) for im_list_h in im_list_2d]
    return get_concat_v_multi_resize(im_list_v, resample=resample)


def main(args):
    img_dir = args.img_dir

    MIN_FRAME_W = 140
    RESIZE_RESOLUTION = (int(MIN_FRAME_W), int(MIN_FRAME_W * 3 / 4))

    img_list = []
    for root, _, files in os.walk(img_dir):
        for file in files:
            i_file = os.path.join(root,file)
            print(i_file)
            if i_file.split('.')[-1] != "jpg":
                continue
            img = Image.open(i_file)
            width, height = img.size
            img_crop = img.crop((0, 0, width, width * 3 / 4))
            img_resize = img_crop.resize(RESIZE_RESOLUTION)
            img_list.append(img_resize)


    import pdb; pdb.set_trace()
    get_concat_tile_resize([img_list[0:10],
                            img_list[10:20],
                            img_list[20:30],
                            img_list[30:40],
                            img_list[40:50],
                            img_list[50:60],
                            img_list[60:70]]).save('out.jpg')
    print('end')

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_dir', type=str, default= pathlib.Path.home() / 'Pictures/btoss/img/seikon_images/before_trimming')
    args = parser.parse_args()
    main(args)

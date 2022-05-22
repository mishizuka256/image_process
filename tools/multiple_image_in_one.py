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

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                        (img_height - crop_height) // 2,
                        (img_width + crop_width) // 2,
                        (img_height + crop_height) // 2))

def main(args):
    img_dir = args.img_dir

    # MIN_FRAME_W = 180
    MIN_FRAME_W = 128
    RESIZE_RESOLUTION = (int(MIN_FRAME_W), int(MIN_FRAME_W * 3 / 4))
    # TARGET_RESOLUTION = (1150, 650)
    TARGET_RESOLUTION = (700, 400)

    img_list = []
    for root, _, files in os.walk(img_dir):
        for file in files:
            i_file = os.path.join(root,file)
            print(i_file)
            if i_file.split('.')[-1] != "jpg":
                continue
            img = Image.open(i_file)
            width, height = img.size
            if height > width * 3 / 4:
                img_crop = img.crop((0, 0, width, width * 3 / 4))
            else:
                img_crop = img.crop((0, 0, height * 4 / 3, height))
            img_resize = img_crop.resize(RESIZE_RESOLUTION)
            img_list.append(img_resize)

    NUM_HORIZON_FRAMES = int(TARGET_RESOLUTION[0] / MIN_FRAME_W + 1)
    img_new = get_concat_tile_resize([img_list[0:NUM_HORIZON_FRAMES],
                            img_list[NUM_HORIZON_FRAMES*1:NUM_HORIZON_FRAMES*2],
                            img_list[NUM_HORIZON_FRAMES*2:NUM_HORIZON_FRAMES*3],
                            img_list[NUM_HORIZON_FRAMES*3:NUM_HORIZON_FRAMES*4],
                            img_list[NUM_HORIZON_FRAMES*4:NUM_HORIZON_FRAMES*5],
                            img_list[NUM_HORIZON_FRAMES*5:NUM_HORIZON_FRAMES*6]])
    img_new_crop = crop_center(img_new, TARGET_RESOLUTION[0], TARGET_RESOLUTION[1])
    img_new_crop.save('out.jpg', quality=100)

    img_rgba = img_new_crop.copy()
    img_rgba.putalpha(128)
    img_rgba.save('alpha.png')
    
    print('end')

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_dir', type=str, default= pathlib.Path.home() / 'Pictures/btoss/img/seikon_images/before_trimming')
    args = parser.parse_args()
    main(args)

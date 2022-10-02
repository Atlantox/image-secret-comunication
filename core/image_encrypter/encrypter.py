from PIL import Image
import os.path
from os import path
import math
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import base64
from colorama import init
from termcolor import cprint 
from pyfiglet import figlet_format
from rich import print
from rich.console import Console
from rich.table import Table
import os
import getpass
from rich.progress import track
import sys



checkpoint = '1A10x20R22'

def main():
    path = 'prueba.png'
    message = checkpoint + 'mensajito'
    secret = ''
    for letter in message:
        secret += format(ord(letter), '08b')

    encrpytImage(path, secret)
    


   




def convertToRGB(image):
    try:
        rgba_image = image
        rgba_image.load()
        background = Image.new("RGB", rgba_image.size)
        background.paste(rgba_image, mask = rgba_image.split()[3])
        print("[yellow]Converted image to RGB [/yellow]")
        return background
    except Exception as e:
        print("[red]Couldn't convert image to RGB [/red]- %s"%e)




def encrpytImage(path, secret):
    splited_s = [secret[i:i+8] for i in range(0, len(secret), 8)]
    #  Splitting the secret message of 3 in 3
    pixels_to_modify = len(splited_s)*3
    print(f'pixels to modify: {pixels_to_modify}')

    with Image.open(path) as im:
        width, height = im.size
        if im.mode != 'RGB':
            im = convertToRGB(im)
        x = 0
        y = 0
        groups_ready = 0
        new_row = False

        for bit_group in splited_s:
            p1 = {
                'coord': (x,y),
                'value': im.getpixel((x,y))
                }

            if x + 1 >= width:
                x = -1
                y += 1
                new_row = True

            p2 = {
                'coord': (x + 1,y),
                'value': im.getpixel((x + 1,y))
                }

            if new_row:
                x = 0
                new_row = False

            if x + 2 >= width:
                x = - 2
                y += 1
                new_row = True            

            p3 = {
                'coord': (x + 2,y),
                'value': im.getpixel((x + 2,y))
                }

            if new_row:
                x = 0
                new_row = False

            pixel_list = [p1, p2, p3]
            pixel_count = 0
            pixel_band = 0
            #print(pixel_list)
            new_band_list = []
            new_pixel_list = []

            for i in range(0,8):
                current_band = pixel_list[pixel_count]['value'][pixel_band]
                current_coord = pixel_list[pixel_count]['coord']
                if bit_group[i] == '0':
                    if current_band % 2 != 0:
                        if current_band == 255:
                            current_band -= 1
                        else:
                            current_band += 1
                    
                elif bit_group[i] == '1':
                    if current_band % 2 == 0:
                        current_band += 1
                
                pixel_band += 1
                
                new_band_list.append(current_band)
                
                if i == 7:
                    if pixels_to_modify / 3 == groups_ready + 1:
                        new_band_list.append(0)
                    if len(new_band_list) == 2:
                        new_band_list.append(0)
                    new_pixel_list.append({
                        'coord': current_coord,
                        'value': new_band_list
                    })
                    #break

                if pixel_band == 3:
                    new_pixel_list.append({
                        'coord': current_coord,
                        'value': new_band_list
                    })

                    new_band_list = []
                    pixel_band = 0
                    pixel_count += 1


            if x == width - 1:
                x = 0
                y += 1
            else:
                x += 3
                if x >= width:
                    x = 0
                    y+= 1
        
            groups_ready += 1

            # add 0 to stop or 1 to continue
            aux = pixel_list[2]['value'][2]
            if pixels_to_modify / 3 == groups_ready:
                if aux % 2 == 0:
                    new_pixel_list[2]['value'][2] = aux + 1
            else:
                if aux % 2 != 0:
                    if aux == 255:
                        new_pixel_list[2]['value'][2] = aux - 1
                    else:
                        new_pixel_list[2]['value'][2] = aux + 1
            
            #print(new_pixel_list)

            print(pixel_list)
            print(new_pixel_list)

            for pixel in new_pixel_list:
                coord = pixel['coord'][0], pixel['coord'][1]

                im.putpixel(coord, tuple(pixel['value']))

        im.save('listo.png')


def decrpytImage():
    pass

if __name__ == '__main__':
    main()

''' This code was inspired by https://github.com/teja156/imghide '''

import os
from PIL import Image
from cryptocode import decrypt, encrypt

mark = '1A10x20R22'
DEBUG = False  # Set to True if you want to get aditional info during process
clear = lambda: os.system('cls')  # Using clear() clear the console

def encode_image(path, message, password):
    result = {'ok':False}
    if(os.path.exists(path)):
        if password != '':
            message = encrypt(message, password)

        message = mark + message

        if img_size_is_ok(path, message):
            try:
                new_path = crypt_image(path,message)

                if new_path == None:
                    return result | {'message': 'Error converting image to RGB'}

                result['ok'] = True
                return result | {'message': 'Image encode success in: ' + new_path}

            except Exception as e:
                return result | {'message': f'An error has ocurred: {e}'}
        else:
            return result | {'message': 'Message too big'}
    else:
        return result | {'message': 'Image not found'}


def decode_image(path, password):
    return decrpyt_image(path, password)

def img_size_is_ok(path, message):
    ''' Check if the image size can contain the message'''

    with Image.open(path) as img:
        width, height = img.size
        img_pixels = width * height
        message_pixels = len(message) * 3

        if img_pixels > message_pixels:
            return True

        return (img_pixels, message_pixels)

def convertToRGB(image):
    ''' Convert the image to RGB format '''
    try:
        rgba_image = image
        rgba_image.load()
        background = Image.new("RGB", rgba_image.size)
        background.paste(rgba_image, mask = rgba_image.split()[3])
        return background
    except Exception as e:
        return None

def checkXY(w, x, y):
    ''' Checks if the x axis has arrived to the las pixel in row '''
    if x >= w:
        x = 0
        y += 1
    return x, y


def crypt_image(path, message):
    ''' Write the message in the image '''
    secretmsg = ''
    for letter in message:
        secretmsg += format(ord(letter), '08b')
    
    splited_s = [secretmsg[i:i+8] for i in range(0, len(secretmsg), 8)]
    # Splitting the secret message of 8 in 8

    pixels_to_modify = len(splited_s)*3
    # Each group of 8 bits consumes 3 pixels

    colors = ['red', 'green', 'blue']  # Colors of the RGB bands if DEBUG = True

    with Image.open(path) as img:
        width,height = img.size
        if img.mode != 'RGB':
            img = convertToRGB(img)
            if img == None:
                return None
        x = 0
        y = 0
        bits_writed = 0  # 0's or 1's writed
        pixel_count = 1

        while (bits_writed < pixels_to_modify / 3):

            pixels = [None, None, None]
            coords = list()  # Contain the respective x, y coordinates of each pixel

            pixels[0] = img.getpixel((x, y))
            coords.append((x,y))

            x, y = checkXY(width, x + 1, y)
            coords.append((x,y))
            pixels[1] = img.getpixel((x, y))

            x, y = checkXY(width, x + 1, y)
            coords.append((x,y))
            pixels[2] = img.getpixel((x, y))

            new_pixels = list()  # Pixels modified

            to_write = splited_s[bits_writed]
            to_write_splited = [to_write[i:i+3] for i in range(0, len(to_write), 3)]
            for pixel in range(3): # For each pixel in pixels
                new_bands = list()

                current_to_write = to_write_splited[pixel]
                for band in range(3): # For each band (R,G,B) in each pixel
                    try:
                        new_bands.append(get_new_band_value(current_to_write[band], pixels[pixel][band], colors[band]))
                        if len(new_bands) == 3:
                            new_pixels.append(new_bands)
                            pixel_count += 1
                    except IndexError:
                        pixel_count += 1
                        if bits_writed + 1 == pixels_to_modify / 3:
                            new_bands.append(get_new_band_value('1', pixels[pixel][band], colors[band]))

                        else:
                            new_bands.append(get_new_band_value('0', pixels[pixel][band], colors[band]))

                        new_pixels.append(new_bands)
                        if len(new_pixels) == 3:
                            for i in range(len(coords)):
                                img.putpixel((coords[i][0], coords[i][1]), tuple(new_pixels[i]))
            
            x, y = checkXY(width, x + 1, y)  # Go to next pixel
            
            bits_writed += 1
            if (bits_writed == pixels_to_modify / 3):
                break

        #  Getting the image name wihtouth extension
        new_imagename = path.split('/')[-1].split('.')[0]
        new_imagename = f'./encoded_images/{new_imagename}-crp.png'

        img.save(new_imagename)
        return new_imagename

def get_new_band_value(bit, band, color):
    ''' Returns the new RGB values of a pixel '''
    old_band = band
    if bit == '1':
        if band % 2 == 0:
            band += 1
    
    elif bit == '0':
        if band % 2 != 0:
            if band == 255:
                band -= 1
            else:
                band += 1
    return band

def decrpyt_image(path, password):
    ''' Read a secret message in image '''

    result = {'ok': False}
    with Image.open(path) as img:
        image_mark = get_decrpyed_content(img, True)
        # Checks if the image have the mark, then the image has a secret message

        if image_mark == mark:  # If the image has a secret message
        
            message = get_decrpyed_content(img)

            if password != '':
                message = decrypt(message, password)

            if message == False:
                return result | {'message': 'Wrong password'}
            else:
                result['ok'] = True
                return result | {'message': message}

        else:
            return result | {'message': "The image don't has a secret message, at least not in our encoding"}

def get_decrpyed_content(img, is_mark = False):
    ''' Return the result of the decrpyt '''
    width, height = img.size
    #  If you are searching for the mark, search from the first pixel
    x, y = 0, 0
    pixel_counter = 0

    if not is_mark:
        # If you are decrypting a message, jump the mark pixels
        for letter in mark:
            for i in range(3):
                x, y = checkXY(width, x + 1, y)

    result = ''
    while True:
        pixels = [None, None, None]
        crypted_letter = ''

        pixels[0] = img.getpixel((x, y))

        x, y = checkXY(width, x + 1, y)
        pixels[1] = img.getpixel((x, y))

        x, y = checkXY(width, x + 1, y)
        pixels[2] = img.getpixel((x, y))

        for pixel in pixels:
            for band in pixel:
                if band % 2 == 0:
                    crypted_letter += '0'
                else:
                    crypted_letter += '1'
        pixel_counter += 1

        # Setting x, y to the next pixel before next cicle
        x, y = checkXY(width, x + 1, y)

        decimal_value = int(crypted_letter[:8], 2)
        letter = chr(decimal_value)
        result += letter

        if is_mark:
            if len(mark) == len(result):
                break
        else:
            if crypted_letter[-1] == '1':
                break
    
    return result
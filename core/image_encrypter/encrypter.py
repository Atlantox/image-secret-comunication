''' This code was inspired by https://github.com/teja156/imghide '''

from PIL import Image
from rich import print
import os
from getpass import getpass
from cryptocode import decrypt, encrypt

mark = '1A10x20R22'
DEBUG = False  # Set to True if you want to get aditional info during process
clear = lambda: os.system('cls')  # Using clear() clear the console

def process_image(path:str, password, option):
    ''' Process the user option and ask for the necesarry data '''
    image_name = path.split('/')[-1]
    if option == '1':  # Crypt message
        print("[yellow]Now write the secret message, don't worry I will close my eyes[/yellow]")
        message = input('')

        if password != '':
            message = encrypt(message, password)
        
        message = mark + message
        clear()
        size_ok = img_size_is_ok(path,message)
        if (type(size_ok) == bool):
            print(f'[yellow]Perfect!, crypting message in [cyan]{image_name}[/cyan][/yellow]')
            crypt_image(path, message)
        else:
            print(f'[red]Oops! looks like the message does not fits in the image[/red]')
            print(f'[yellow]Image pixels:[/yellow] [cyan]{size_ok[0]}[/cyan]')
            print(f'[yellow]Message pixels:[/yellow] [cyan]{size_ok[1]}[/cyan]')

    elif option == '2':  # Decrypt message
        clear()
        print(f'[yellow]Perfect!, decrypting message of [cyan]{image_name}[/cyan][/yellow]')
        decrpyt_image(path, password)

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
        print("[green]Image converted to RGB[/green]")
        return background
    except Exception as e:
        print("[red]Couldn't convert image to RGB[/red]")
        print(f'[red]Error:[/red] {e}')

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
    print(f'Pixels to modify: [cyan]{pixels_to_modify}[/cyan]')
    print('\n[yellow]### BEGINNING ENCRYPTION ###[/yellow]\n')

    colors = ['red', 'green', 'blue']  # Colors of the RGB bands if DEBUG = True

    with Image.open(path) as img:
        width,height = img.size
        if img.mode != 'RGB':
            img = convertToRGB(img)
        x = 0
        y = 0
        bits_writed = 0  # 0's or 1's writed
        pixel_count = 1

        while (bits_writed < pixels_to_modify / 3):
            if(DEBUG):
                print(f'Current letter: [cyan]{message[bits_writed]}[/cyan]')
                print(f'Binary value: [cyan]{splited_s[bits_writed]}[/cyan]')

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

                if DEBUG:
                    print(f'Pixel [cyan]{pixel_count}[/cyan]')

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
                            if DEBUG:
                                print('[green]The message ends[/green]\n')
                        else:
                            new_bands.append(get_new_band_value('0', pixels[pixel][band], colors[band]))
                            if DEBUG:
                                print('[yellow]The message continue[/yellow]\n')
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
        new_imagename += '-crp.png'

        print('[green]Crypt succesfull![/green]')
        print(f'Image saved as [cyan]{new_imagename}[/cyan]')
        img.save(new_imagename)
      

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
    if DEBUG:
        print(f'[cyan]{bit}[/cyan]: [{color}]{old_band}->{band}[/{color}]')
    return band

def decrpyt_image(path, password):
    ''' Read a secret message in image '''
    with Image.open(path) as img:
        image_mark = get_decrpyed_content(img, True)
        # Checks if the image have the mark, then the image has a secret message

        if image_mark == mark:  # If the image has a secret message
            print('[green]The image has a secret message![/green]')
        
            message = get_decrpyed_content(img)

            if password != '':
                message = decrypt(message, password)

            if message == False:
                print(f'[red]Incorrect password[/red]')
            else:
                print(f'[green]Message decrypted![/green]')
                print(f'[yellow]{message}[/yellow]')

        else:
            print("[red]The image don't has a secret message, at least not in our encoding[/red]")

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

        if DEBUG:
                print(f'[yellow]### Pixels trio nº {pixel_counter} ###[/yellow]')
                print(f'Binary value: [cyan]{crypted_letter}[/cyan]')
                print(f'Control digit: [cyan]{crypted_letter[-1]}[/cyan]')
                print(f'Decimal value: [cyan]{decimal_value}[/cyan]')
                print(f'Letter: [cyan]{letter}[/cyan]')
                print('')

        if is_mark:
            if len(mark) == len(result):
                break
        else:
            if crypted_letter[-1] == '1':
                break
    
    return result

if __name__ == '__main__':
    clear()
    print('\n[cyan]Welcome to the image secret messages crypter made by Atlantox[cyan]\n')
    print('[yellow]What do you want to do?[/yellow]')
    print('[cyan][1] Crypt a message[/cyan]')
    print('[cyan][2] Decrpyt a message[/cyan]')
    option = input('')
    if option != '1' or option != '2':
        print('[yellow]Excellent!, please be sure to put the image in de images folder[/yellow]')
        print('[yellow]Now tell me the image name with extension[/yellow]')
        path = input('')

        new_path = f'./images/{path}'
        if(os.path.exists(new_path)):
            print('[yellow]Image found![/yellow]')
            print("[yellow]Now tell me the password of the message (press enter key if the message don't have password)[/yellow]")
            password = getpass('Pass:')
            process_image(new_path, password, option)
        else:
            print(f"[red]Oh... looks like the image {path} not exists, please be sure the image is in the 'images' folder[/red]")
    else:
        print('[red]Wrong command, try again[/red]')
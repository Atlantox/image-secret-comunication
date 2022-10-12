from PIL import Image
from rich import print

checkpoint = '1A10x20R22'
DEBUG = True

def main():
    path = 'prueba.png'
    message = checkpoint + 'mensajito largo'
    secret = ''
    password = ''

    crpyt_image(path, message, password)
    

def convertToRGB(image):
    try:
        rgba_image = image
        rgba_image.load()
        background = Image.new("RGB", rgba_image.size)
        background.paste(rgba_image, mask = rgba_image.split()[3])
        print("[green]Image converted to RGB[/green]")
        return background
    except Exception as e:
        print("[red]Couldn't convert image to RGB[/red]- %s"%e)


def crpyt_image(path, message, password):
    secretmsg = ''
    for letter in message:
        secretmsg += format(ord(letter), '08b')
    
    splited_s = [secretmsg[i:i+8] for i in range(0, len(secretmsg), 8)]
    #  Splitting the secret message of 8 in 8

    pixels_to_modify = len(splited_s)*3
    #  Each group of 8 bits consumes 3 pixels
    print(f'Pixels to modify: [cyan]{pixels_to_modify}[/cyan]')
    print('\n[yellow]### BEGINNING ENCRYPTION ###[/yellow]\n')

    colors = ['red', 'green', 'blue']

    with Image.open(path) as img:
        width,height = img.size
        if img.mode != 'RGB':
            img = convertToRGB(img)
        x = 0
        y = 0
        bits_writed = 0
        pixel_count = 1

        while (bits_writed < pixels_to_modify / 3):
            if(DEBUG):
                print(f'Current letter: [cyan]{message[bits_writed]}[/cyan]')
                print(f'Binary value: [cyan]{splited_s[bits_writed]}[/cyan]')

            pixels = [None, None, None]
            coords = list()

            pixels[0] = img.getpixel((x, y))
            coords.append((x,y))

            x, y = checkXY(width, x + 1, y)
            coords.append((x,y))
            pixels[1] = img.getpixel((x, y))

            x, y = checkXY(width, x + 1, y)
            coords.append((x,y))
            pixels[2] = img.getpixel((x, y))

            new_pixels = list()

            to_write = splited_s[bits_writed]
            to_write_splited = [to_write[i:i+3] for i in range(0, len(to_write), 3)]
            for pixel in range(3): #  Pixels
                new_bands = list()

                if DEBUG:
                    print(f'Pixel [cyan]{pixel_count}[/cyan]')

                current_to_write = to_write_splited[pixel]
                for band in range(3): #  Pixels bands (RGB)
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
                                print('[green]The message ends[/green]')
                        else:
                            new_bands.append(get_new_band_value('0', pixels[pixel][band], colors[band]))
                            if DEBUG:
                                print('[yellow]The message continue[/yellow]')
                        new_pixels.append(new_bands)
                        if len(new_pixels) == 3:
                            for i in range(len(coords)):
                                img.putpixel((coords[i][0], coords[i][1]), tuple(new_pixels[i]))
                print('')
            x, y = checkXY(width, x + 1, y)
            
            bits_writed += 1
            if (bits_writed == pixels_to_modify / 3):
                break
        new_filename = 'listo' + '.png'
        print('[green]Encrypt succesfull![/green]')
        print(f'Image saved as [cyan]{new_filename}[/cyan]')
        img.save(new_filename)
        

def get_new_band_value(bit, band, color):
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


def checkXY(w, x, y):
    if x >= w:
        x = 0
        y += 1
    return x, y


def decrpytImage():
    pass

if __name__ == '__main__':
    main()
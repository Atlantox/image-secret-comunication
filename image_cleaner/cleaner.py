''' Currently not ready '''
from PIL import Image

def clean_image(path, rgb):
    ''' Convert to transparent the pixels of a specific color of an image '''
    with Image.open(path) as im:
        width,height = im.size
        for x in range(0,width):
            for y in range(0,height):
                pixel = im.getpixel((x,y))
                if pixel[0] == rgb[0] and pixel[1] == rgb[1] and pixel[2] == rgb[2]:
                    im.putpixel((x,y), (0,0,0,0))
        im.save('ready.png')


if __name__ == '__main__':
    clean_image('sample.png', (255,255,255))
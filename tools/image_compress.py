
import argparse
from PIL import Image

def compress_rle(input, width, height, output,**_):

    image = Image.open(input)

    if image.mode != 'RGBA' and image.mode != 'RGB':
        raise Exception('image bands have to be RGB or RGBA')

    width = width or image.width
    height = height or image.height

    if width != image.width or height != image.height:
        image = image.resize((width, height),resample=Image.Resampling.NEAREST)

    outputBuf = bytearray()
    last_pixel = None
    count = 1

    for y in range(0, height):
        for x in range(0, width):

            pixelRGBA = image.getpixel((x, y))
            grey = int((pixelRGBA[0] + pixelRGBA[1] + pixelRGBA[2]) / 3) & 0xc0
            alpha = 0xc0
            if len(pixelRGBA) > 3:
                alpha = ~(pixelRGBA[3]) & 0xc0
            pixel = (grey >> 6) | (alpha >> 4)

            if last_pixel is None:
                last_pixel = pixel
            elif last_pixel == pixel and count < 255:
                count += 1
            else:
                outputBuf.extend([count,last_pixel])
                last_pixel = pixel
                count = 1

    outputBuf.extend([count,last_pixel])

    output.write(bytes([width,height]))
    output.write(outputBuf)
    output.write(bytes([0xFF,0xFF]))


def compress_raw(input, width, height, output, **_):

    image = Image.open(input)

    if image.mode != 'RGBA' and image.mode != 'RGB':
        raise Exception('image bands have to be RGB or RGBA')

    width = width or image.width
    height = height or image.height

    if width != height:
        raise Exception('image must be square for raw compression')

    if width != image.width or height != image.height:
        image = image.resize((width, height),resample=Image.Resampling.NEAREST)

    outputBuf = bytearray()
    shiftCounter = 0
    shiftReg = 0

    for y in reversed(range(0, height)):
        for x in reversed(range(0, width)):

            pixel = image.getpixel((x, y))
            grey = int((pixel[0] + pixel[1] + pixel[2]) / 3) & 0xc0

            shiftReg |= grey >> shiftCounter

            if (shiftCounter == 6):
                outputBuf.append(shiftReg)
                shiftReg = 0
                shiftCounter = 0
            else:
                shiftCounter += 2

    if (shiftCounter != 0):
        outputBuf.append(shiftReg)

    output.write(outputBuf)

def main():

    optParser = argparse.ArgumentParser(description="Convert image to Fossil Hybrid format",add_help=False)

    optParser.add_argument(
        "-i","--input",
        required=True,
        type=argparse.FileType('rb'),
        help="Input file (RGBA PNG)")
    optParser.add_argument(
        "-o","--output",
        required=True,
        type=argparse.FileType('wb'),
        help="Output file")
    optParser.add_argument(
        "-f","--format",
        required=False,
        default="rle",
        choices=['rle','raw'],
        help="Format of the output image, default: rle")
    optParser.add_argument(
        "-w","--width",
        required=False,
        type=int,
        help="Optional: width of the output image in pixels")
    optParser.add_argument(
        "-h","--height",
        required=False,
        type=int,
        help="Optional: height of the output image in pixels")
    optParser.add_argument(
        "--help",
        default=argparse.SUPPRESS,
        action="help",
        help="show this help message and exit")

    args = optParser.parse_args()

    if args.format == 'rle':
        compress_rle(**vars(args))
    elif args.format == 'raw':
        compress_raw(**vars(args))



if __name__ == '__main__':
    main()

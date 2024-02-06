from PIL import Image
from math import isqrt
import argparse

# scaling 2 bits to 8 bits, 0 => 0, ... , 0b11 => 0xFF
def bitscale2to8(c):
    return 0x55 * (c & 3)


def decompressRaw(input, output, **_):

    size = 0
    def rawEncoder():
        nonlocal input,size
        while b := input.read(1):     # read is buffered so no optimization is needed
            b = b[0]
            size += 1
            for _a in range(4):
                for _b in range(3):
                    yield bitscale2to8(b >> 6)
                b <<= 2

    pixels = bytes(rawEncoder())

    w = isqrt(size)
    if w*w != size:
        print("Faulty image file - wrong file size")
        exit(1)

    w <<= 1     # 4 pixels per byte, squared
    print(f'final image size: {w}x{w}')

    image = Image.frombuffer('RGB', (w, w), pixels)
    image.transpose(Image.Transpose.ROTATE_180).save(output, 'PNG')

def decompress(input, output, **_):

    try:

        (width,height) = input.read(2)      # can throw ValueError

        print(f'final image size: {width}x{height}')

        image_pixels = bytearray()
        rep = None
        byte = None

        while r := input.read(2):   # read is buffered so no optimization is needed

            if rep is not None:

                color = bitscale2to8(byte)
                alpha = bitscale2to8(~(byte >> 2))
                image_pixels.extend([color, color, color, alpha] * rep)

            (rep, byte) = r     # can throw ValueError

    except ValueError:
        print("Faulty image file - wrong file size")
        exit(1)

    if rep != 0xFF or byte != 0xFF:
        print('Faulty image file, missing 0xFF 0xFF at end')

    image = Image.frombuffer('RGBA', (width, height), image_pixels)
    image.save(output, 'PNG')

def main():

    optParser = argparse.ArgumentParser(description="Convert image from Fossil Hybrid format to PNG")

    optParser.add_argument(
        "-i","--input",
        required=True,
        type=argparse.FileType('rb'),
        help="Input file")
    optParser.add_argument(
        "-f","--iformat",
        required=False,
        default="rle",
        choices=['rle','raw'],
        help="Format of the input image, default: rle")
    optParser.add_argument(
        "-o","--output",
        required=True,
        type=argparse.FileType('wb'),
        help="Output file")

    args = optParser.parse_args()

    if args.iformat == 'rle':
        decompress(**vars(args))
    else:
        decompressRaw(**vars(args))


if __name__ == '__main__':
    main()
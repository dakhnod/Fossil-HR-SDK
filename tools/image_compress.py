import sys
import getopt
from PIL import Image


class Image_compresser:
    def __init__(self):
        pass

    def rle_encode(self, raw_bytes):
        output = bytearray()
        last_byte = raw_bytes[0]
        current_count = 1
        current_byte = -1

        for i in range(1, raw_bytes.__len__()):
            current_byte = raw_bytes[i]

            if current_byte != last_byte or current_count >= 255:
                output.append(current_count)
                output.append(raw_bytes[i - 1])
                current_count = 1
                last_byte = raw_bytes[i]
            else:
                current_count += 1

        output.append(current_count)
        output.append(current_byte)

        return output

    def compress_rle(self, input_file, width, height, output_file):
        image = Image.open(input_file)
        if image.getbands() != tuple(['R', 'G', 'B', 'A']):
            raise Exception('image bands have to be RGBA')
        image = image.resize((width, height))
        pixels = bytearray()
        for y in range(0, height):
            for x in range(0, width):
                pixel = image.getpixel((x, y))
                grey = (pixel[0] + pixel[1] + pixel[2]) / 3
                pixel_bits = (int(grey) & 0xFF) >> 6
                pixel_bits |= (~(pixel[3]) >> 4) & 0b00001100
                pixels.append(pixel_bits)

        compressed = self.rle_encode(pixels)
        output = bytearray()
        output.append(width)
        output.append(height)
        output.extend(compressed)
        output.extend([0xFF, 0xFF])

        with open(output_file, 'wb') as output_file:
            output_file.write(output)

    def compress_raw(self, input_file, width, height, output_file):
        image = Image.open(input_file)
        pixels = bytearray(width * height)
        jumpX = image.width / width
        jumpY = image.height / height

        for y in range(0, height):
            for x in range(0, width):
                pixel = image.getpixel((x * jumpX, y * jumpY))
                grey = (pixel[0] + pixel[1] + pixel[2]) / 3
                pixels[len(pixels) - 1 - (y * width + x)] = int(grey)

        output = bytearray(int(len(pixels) / 4))
        for i in range(0, len(pixels)):
            resultPixelIndex = int(i / 4)
            shiftIndex = 6 - i % 4 * 2
            output[resultPixelIndex] |= ((int(pixels[i]) & 0xFF) >> 6) << shiftIndex

        with open(output_file, 'wb') as output_file:
            output_file.write(output)


def usage():
    print('Usage: ' + sys.argv[0] + ' [options]')
    print('Available options are:')
    print('  -i,  --input=FILE      input file (RGBA PNG)')
    print('  -o,  --output=FILE     output file')
    print('  -w,  --width=PIXELS    width of the output image in pixels')
    print('  -h,  --height=PIXELS   height of the output image in pixels')
    print('  -f,  --format=FORMAT   format of the output image (rle or raw)')

def main():
    input_file = None
    output_file = None
    width = -1
    height = -1
    output_format = None

    if len(sys.argv) < 11:
        usage()
        sys.exit(2)

    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'i:w:h:o:f:', ['input=', 'width=', 'height=', 'output=', 'format='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for key, value in options:
        if key in ['-i', '--input']:
            input_file = value
        elif key in ['-o', '--output']:
            output_file = value
        elif key in ['-w', '--width']:
            width = int(value)
        elif key in ['-h', '--height']:
            height = int(value)
        elif key in ['-f', '--format']:
            output_format = value
            if output_format not in ['rle', 'raw']:
                usage()
                sys.exit(2)

    compresser = Image_compresser()
    if output_format == 'rle':
        compresser.compress_rle(
            input_file,
            width,
            height,
            output_file
        )
    elif output_format == 'raw':
        compresser.compress_raw(
            input_file,
            width,
            height,
            output_file
        )


if __name__ == '__main__':
    main()

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

    def compress(self, input_file, width, height, output_file):
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


def main():
    input_file = None
    output_file = None
    width = -1
    height = -1

    options, remainder = getopt.getopt(sys.argv[1:], 'i:w:h:o:', ['input=', 'width=', 'height=', 'output='])

    for key, value in options:
        if key in ['-i', '--input']:
            input_file = value
        elif key in ['-o', '--output']:
            output_file = value
        elif key in ['-w', '--width']:
            width = int(value)
        elif key in ['-h', '--height']:
            height = int(value)

    compresser = Image_compresser()
    compresser.compress(
        input_file,
        width,
        height,
        output_file
    )


if __name__ == '__main__':
    main()

from PIL import Image
import sys
import os.path
import getopt

class Decompresser:
    def __init__(self):
        pass

    def decompress(self, input_file_path, output_file_path):
        image_pixels = []

        if not os.path.isfile(input_file_path):
            raise Exception('first parameter needs to be compressed image file')

        with open(input_file_path, 'rb') as image_file:
            width = image_file.read(1)[0]
            height = image_file.read(1)[0]

            print('final image size: %dx%d' % (width, height))

            image_file.seek(0, 2)

            image_data_end = image_file.tell() - 2

            image_file.seek(2)

            while image_file.tell() < image_data_end:
                repititions = image_file.read(1)[0]
                byte = image_file.read(1)[0]

                color = (byte << 6) & 0b11000000
                alpha = ~(byte << 4) & 0b11000000

                image_pixels.extend([color, color, color, alpha] * repititions)

            if image_file.read(2) != b'\xFF\xFF':
                print('faulty image file, missing 0xFF 0xFF at end')

        image = Image.frombuffer('RGBA', (width, height), bytearray(image_pixels))
        image.save(output_file_path, 'PNG')


if __name__ == '__main__':
    decompresser = Decompresser()
    input_file_path = None
    output_file_path = None
    args, remainder = getopt.getopt(sys.argv[1:], 'i:o:', ['input=', 'output='])
    for key, value in args:
        if key in ['-i', '--input']:
            input_file_path = value
        elif key in ['-o', '--output']:
            output_file_path = value

    decompresser.decompress(input_file_path, output_file_path)


from PIL import Image
import sys
import os.path

class Decompresser:
    def __init__(self, image_path):
        self.image_path = image_path

    def decompress(self):
        image_pixels = []

        if not os.path.isfile(sys.argv[1]):
            raise Exception('first parameter needs to be compressed image file')

        with open(self.image_path, 'rb') as image_file:
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
        image.save(sys.argv[2], 'PNG')


if __name__ == '__main__':
    decompresser = Decompresser(sys.argv[1])
    decompresser.decompress()


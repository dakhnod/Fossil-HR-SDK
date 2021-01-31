import sys
import json
import os


class Unpacker:
    def read_int(self, size):
        bts = self.file.read(size)
        return int.from_bytes(bts, 'little')

    def __init__(self, file_path):
        self.file = open(file_path, 'rb')

    def read_file_meta(self):
        handle = self.read_int(2)
        file_version = self.read_int(2)
        wtf = self.read_int(4)
        size = self.read_int(4)

        return {
            'handle': handle,
            'file_version': file_version,
            'wtf': wtf,
            'size': size,
        }

    def read_str(self, length):
        return self.file.read(length)[:-1].decode('utf-8')

    def read_file(self, cut_trailing_null):
        file_name_length = self.read_int(1)
        file_name = self.read_str(file_name_length)
        file_contents_length = self.read_int(2)

        if cut_trailing_null:
            file_contents_length = file_contents_length - 1

        file_contents = self.file.read(file_contents_length)

        if cut_trailing_null:
            self.file.read(1)

        return {
            'filename': file_name,
            'size': file_contents_length,
            'contents': file_contents
        }

    def read_file_sequence(self, limit, cut_trailing_null):
        files = []
        while self.file.tell() < limit:
            files.append(self.read_file(cut_trailing_null))

        return files

    def unpack(self):
        meta = self.read_file_meta()
        print(meta)

        app_version = self.file.read(4)

        self.file.read(8)  # null bytes dunno

        jerry_start = self.read_int(4)
        app_icon_start = self.read_int(4)
        layout_start = self.read_int(4)
        display_name_start = self.read_int(4)
        display_name_start_2 = self.read_int(4)
        file_end = self.read_int(4)

        self.file.seek(jerry_start)

        files = {
            'code': self.read_file_sequence(app_icon_start, False),
            'icons': self.read_file_sequence(layout_start, False),
            'layout': self.read_file_sequence(display_name_start, True),
            'display_name': self.read_file_sequence(file_end, True),
        }

        identifier = files['code'][0]['filename']
        app_meta = {
            'version': '%i.%i.%i.%i' % tuple(app_version),
            'identifier': identifier
        }

        try:
            os.mkdir(identifier)
        except:
            print('cannot create empty dir %s' % identifier)
            exit()


        os.chdir(identifier)
        os.mkdir('files')
        os.chdir('files')

        def dump_files(directory, files_):
            os.mkdir(directory)
            os.chdir(directory)
            for file in files_:
                f = open(file['filename'], 'wb')
                f.write(file['contents'])
                f.close()
            os.chdir(os.pardir)

        for f in files.keys():
            dump_files(f, files[f])

        os.chdir('..')
        meta = open('app.json', 'w')
        meta.write(json.dumps(app_meta))
        meta.close()


def main():
    unpacker = Unpacker(sys.argv[1])
    unpacker.unpack()


if __name__ == '__main__':
    main()

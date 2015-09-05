from subprocess import check_output
from pathlib import Path
from io import StringIO
import re

MKV = Path("C:\\Program Files\\MKVToolNix\\")

def quote_path(path):
    """Return an absolute, quoted path made from Path obejct `path`"""
    return '"' + str(path.absolute()) + '"'

class Info:
    def pprint(self):
        """Pretty print this Info object"""
        print(self.title)
        print(quote_path(self.path))
        for track in self.tracks:
            track.pprint()

    def __str__(self):
        return "<Info obejct: {}>".format(self.title)

    def __init__(self, file):
        """Create Info object by calling mkvinfo on `file`.

        arguments: `file` as Path
        """
        self.path = file
        args = [MKV / 'mkvinfo.exe', self.path]
        args = [quote_path(x) for x in args]
        result = check_output(' '.join(args)).decode()

        self.tracks = []
        buf = result
        while True:
            pos = buf.find('\n')
            if pos == -1:
                break
            line = buf[:pos].strip()
            buf = buf[pos+1:].strip()

            if line.startswith('| + Title:'):
                match = re.search(r': (.+)$', line)
                self.title = match.group(1).strip()
            elif line.startswith('|+ EbmlVoid'):
                # We've passed all useful information
                break
            elif line.startswith('| + A track'):
                pos = buf.find('| + A track')
                if pos == -1:
                    self.tracks.append( self.Track(buf) )
                    break
                else:
                    self.tracks.append( self.Track(buf[:pos]) )
                    buf = buf[pos+1:]

    class Track:
        def pprint(self):
            print("{type} track {name}:".format(self))
            print("  Codec:    {codec}".format(self))
            print("  Language: {language}".format(self))
            print("  Track ID: {id}".format(self))

        def __init__(self, buf):
            while True:
                """arguments: `buf` as string from mkvinfo output"""
                pos = buf.find('\n')
                if pos == -1:
                    break
                line = buf[:pos].strip()
                buf = buf[pos+1].strip()

                if "Track number:" in line:
                    match = re.search(r': ([\d]+)\)\s*$', line)
                    self.id = int(match.group(1))
                elif "Track type:" in line:
                    match = re.search(r': (\w+)$', line)
                    self.type = match.group(1)
                elif "Codec ID:" in line:
                    match = re.search(r': (\w+)$', line)
                    self.codec = match.group(1)
                elif "Language:" in line:
                    match = re.search(r': (\w+)$', line)
                    self.language = match.group(1)
                elif "Name:" in line:
                    match = re.search(r': (.*)$', line)
                    self.name = match.group(1).strip()

if __name__ == "__main__":
    path = Path("E:/torrents")
    path /= "[denpa] Kyoukai no Kanata - Vol.5 [BD 720p AAC]"
    path /= "[denpa] Kyoukai no Kanata - 09 [BD 720p AAC][3D01D0CE].mkv"
    result = Info(path)

    result.pprint()

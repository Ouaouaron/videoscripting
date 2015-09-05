from subprocess import check_output
from pathlib import Path
from io import StringIO
import re

MKV = Path("C:\\Program Files\\MKVToolNix\\")

def quote_path(path):
    """Return an absolute, quoted path made from Path obejct `path`"""
    return '"' + str(path.absolute()) + '"'

class Info:
    """Holds relevant info from mkvinfo"""

    titleregex = re.compile(r'\| \+ Title: (\S*)')

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

        match = Info.titleregex.search(result)
        self.title = match.group(1).strip()

        # Split into tracks and trim excess
        sections = result.split("| + A track")[1:]
        sections[-1] = sections[-1].split("|+")[0]
        self.tracks = []
        for group in sections:
            self.tracks.append(self.Track(group.strip()))


    class Track:
        def pprint(self):
            print("{0.type} -- {0.name}:".format(self))
            print("  Codec:    {0.codec}".format(self))
            print("  Language: {0.language}".format(self))
            print("  Track ID: {0.id}".format(self))

        def __init__(self, buf):
            self.name = 'undefined'
            self.language = 'undefined'
            # Other fields shouldn't be blank
            while True:
                """arguments: `buf` as string from mkvinfo output"""
                pos = buf.find('\n')
                if pos == -1:
                    break
                line = buf[:pos].strip()
                buf = buf[pos+1:].strip()
                

                if "Track number:" in line:
                    match = re.search(r': ([\d]+)\)\s*$', line)
                    self.id = int(match.group(1))
                elif "Track type:" in line:
                    match = re.search(r': (\S+)$', line)
                    self.type = match.group(1)
                elif "Codec ID:" in line:
                    match = re.search(r': (\S+)$', line)
                    self.codec = match.group(1)
                elif "Language:" in line:
                    match = re.search(r': (\S+)$', line)
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

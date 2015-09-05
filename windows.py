from subprocess import check_output, call
from pathlib import Path
from io import StringIO
import re

MKV = Path("C:\\Program Files\\MKVToolNix\\")

def quote_path(path):
    """Return an absolute, quoted path made from Path obejct `path`"""
    return '"' + str(path.absolute()) + '"'

class Info:
    """Holds relevant info from mkvinfo"""

    titleregex = re.compile(r'\| \+ Title: (.*)')

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

    def get_tracks_by_type(self, type):
        return [x for x in self.tracks if x.type == type]


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
            loop = True
            while loop:
                """arguments: `buf` as string from mkvinfo output"""
                pos = buf.find('\n')
                if pos == -1:
                    loop = False
                    line = buf.strip()
                else:
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
    pathlist = [Path("E:/torrents/[denpa] Kyoukai no Kanata - Vol.1 [BD 720p AAC]"),
                Path("E:/torrents/[denpa] Kyoukai no Kanata - Vol.2 [BD 720p AAC]"),
                Path("E:/torrents/[denpa] Kyoukai no Kanata - Vol.3 [BD 720p AAC]")]
    outpath = Path("E:/torrents/test")

    for directory in pathlist:
        for video in directory.iterdir():
            info = Info(video)
            tracks = info.get_tracks_by_type('subtitles')
            
            cmd = quote_path(MKV / 'mkvextract') + " tracks " + quote_path(video)
            for track in tracks:
                cmd += ' {2.id}:"{0!s}\\{1.stem}{2.name}.ass"'.format(outpath, video, track)
            print(cmd)

            raise "DONGER"

import re
import sys
from os import listdir, path

ogg_config_types = open("ogg_config_types.h", "r").read()
ogg_os_types = open("ogg/include/ogg/os_types.h", "r").read().replace("#  include <ogg/config_types.h>", ogg_config_types)
ogg = open("ogg/include/ogg/ogg.h", "r").read().replace("#include <ogg/os_types.h>", ogg_os_types)
ogg += open("ogg/src/bitwise.c", "r").read()
ogg += open("ogg/src/crctable.h", "r").read()
ogg += open("ogg/src/framing.c", "r").read()

vorbis_codec = open("vorbis/include/vorbis/codec.h", "r").read()
vorbis_vorbisfile = open("vorbis/include/vorbis/vorbisfile.h", "r").read().replace('#include "codec.h"', vorbis_codec)
vorbis = open("vorbis/lib/vorbisfile.c", "r").read().replace('#include "vorbis/vorbisfile.h"', vorbis_vorbisfile)

included_headers = set()
include_re = re.compile('^# *?include +?"([^/]+?)"$', re.MULTILINE)


def resolve(header: str):
    if header == "config.h":
        return ""
    if header in included_headers:
        return ""
    included_headers.add(header)
    print(f"merging {header}", file=sys.stderr)
    return include(open(path.join("vorbis/lib", header), "r").read())


def repl(match: re.Match):
    return resolve(match.group(1))


def include(contents: str):
    return re.sub(include_re, repl, contents)


headers = [f for f in listdir("vorbis/lib") if f.endswith(".h") and path.isfile(path.join("vorbis/lib", f))]
for header in headers:
    vorbis += resolve(header)

sources = [
    f for f in listdir("vorbis/lib")
    if f.endswith(".c") and f != "vorbisenc.c" and f != "vorbisfile.c" and path.isfile(path.join("vorbis/lib", f))
]
for source in sources:
    print(f"merging {source}", file=sys.stderr)
    vorbis += open(path.join("vorbis/lib", source), "r").read()

out = re.sub(r'# *?include +?(?:".+?"|<ogg/.+?>)', "", ogg + vorbis)
print(out)

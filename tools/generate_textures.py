"""Texturas PNG próprias geradas com a biblioteca padrão."""
from pathlib import Path
import random
import struct
import zlib
ROOT=Path(__file__).resolve().parents[1]/'assets'/'textures'

def png(path,size,pixel):
    def chunk(kind,data):
        return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    data=b''.join(b'\0'+bytes(v for x in range(size) for v in pixel(x,y)) for y in range(size))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(data,9))+chunk(b'IEND',b''))

def generate():
    ROOT.mkdir(parents=True,exist_ok=True)
    rng=random.Random(1031)
    def sand(x,y):
        n=rng.randrange(-16,17)
        return (214+n,199+n,160+n)
    png(ROOT/'sand.png',128,sand)
    png(ROOT/'white.png',2,lambda x,y:(255,255,255))
    png(ROOT/'hazard.png',64,lambda x,y:(36,46,48) if ((x+y)//12)%2 else (248,188,56))
    png(ROOT/'solar.png',128,lambda x,y:(143,184,202) if x%32<2 or y%24<2 else (28+(x%32)//5,66,103))

if __name__=='__main__':
    generate()

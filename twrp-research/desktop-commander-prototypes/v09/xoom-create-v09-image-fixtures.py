import struct, zlib, pathlib
base = pathlib.Path(__file__).parent
def chunk(tag, data):
    return struct.pack('!I', len(data)) + tag + data + struct.pack('!I', zlib.crc32(tag + data)&0xffffffff)
w,h=16,16
rows=b''.join(b'\x00'+bytes(v for x in range(w) for v in (x*11%256, y*13%256, 180, 255)) for y in range(h))
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b'')
(base/'v09-display-fixture.png').write_bytes(png)
(base/'v09-spoofed-image.jpg').write_bytes(png)
large_canvas=png[:16]+struct.pack('!2I',8192,8192)+png[24:29]+struct.pack('!I',zlib.crc32(b'IHDR'+struct.pack('!2I5B',8192,8192,8,6,0,0,0))&0xffffffff)+png[33:]
(base/'v09-oversized-canvas.png').write_bytes(large_canvas)
print('PNG_FIXTURE_BYTES',len(png))
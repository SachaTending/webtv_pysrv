from dataclasses import  dataclass
from socket import socket
from os import SEEK_END
from typing import Union, IO, BinaryIO, TextIO

@dataclass
class CommonHeaders:
    ssid: str
    incarnation: int
    bootrom_ver: str
    approm_ver: str
    systype: str

@dataclass
class Request:
    raw: bytes
    method: str
    path: str
    path_cleaned: str
    flags: list[str]
    opts: dict[str, str]
    headers: dict[str, str]
    data: bytes
    common_headers: CommonHeaders = None

def get_fsize(a: IO):
    g = a.tell()
    a.seek(0, SEEK_END)
    o = a.tell()
    a.seek(g)
    return o

@dataclass
class Response:
    headers: dict[str, Union[str, list[str]]]
    data: Union[bytes, bytearray, str, IO] = b''
    code: tuple[int, str] = (200, 'OK')
    def construct_response(self) -> bytes:
        out = bytearray()
        out += f"{self.code[0]} {self.code[1]}\n".encode()
        hdrs = self.headers
        d = self.data
        if isinstance(d, str):
            d = d.encode()
        elif isinstance(d, Union[TextIO, BinaryIO, IO]):
            _seek = d.tell()
            d.seek(0)
            _data = d.read()
            d.seek(_seek)
            d = _data
        if d:
            hdrs['Content-Length'] = len(d)
        else:
            hdrs['Content-Length'] = 0
        for i in hdrs.items():
            if isinstance(i[1], list):
                for g in i[1]:
                    out += f"{i[0]}: {g}\n".encode()
            else:
                out += f"{i[0]}: {i[1]}\n".encode()
        out += b"\n"
        out += d
        return bytes(out)
    def construct_response_streamed(self) -> bytes:
        out = bytearray()
        out += f"{self.code[0]} {self.code[1]}\n".encode()
        hdrs = self.headers
        if self.data:
            hdrs['Content-Length'] = get_fsize(self.data)
        else:
            hdrs['Content-Length'] = 0
        for i in hdrs.items():
            if isinstance(i[1], list):
                for g in i[1]:
                    out += f"{i[0]}: {g}\n".encode()
            else:
                out += f"{i[0]}: {i[1]}\n".encode()
        out += b"\n"
        return bytes(out)

def recv_line(sock: socket) -> bytearray:
    out = bytearray()
    c = b''
    while True:
        c = sock.recv(1)
        if c == b'\n':
            out = out.removesuffix(b"\r")
            return out
        elif c == b'':
            return None
        out += c
    # bruh
        
def parse_params(req: Request):
    p = req.path
    p = p.split("?", 1)
    req.path_cleaned = p[0]
    if len(p) > 1:
        p = p[1].split("&")
        for i in p:
            if len(i.split("=", 1)) == 1:
                req.flags.append(i)
            else:
                g = i.split("=", 1)
                req.opts[g[0]] = g[1]

def receive_request(sock: socket) -> Request:
    mp = recv_line(sock)
    d = mp + b"\r\n"
    mp = mp.decode()
    mp = mp.split(" ", 1)
    req = Request(None, mp[0], mp[1], None, [], {}, {}, None)
    hdr = None
    while True:
        hdr = recv_line(sock)
        d += hdr + b"\r\n"
        if hdr == b'':
            break
        hdr = hdr.decode().split(": ", 1)
        req.headers[hdr[0]] = hdr[1]
    t = sock.gettimeout()
    sock.settimeout(1)
    g = bytearray()
    while True:
        try:
            g += sock.recv(16384)
        except TimeoutError:
            break
    d += g
    req.data = g
    req.raw = bytes(d)
    parse_params(req)
    sock.settimeout(t)
    return req

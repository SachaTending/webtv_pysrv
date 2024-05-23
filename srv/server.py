from .wtvp import receive_request, Request, Response, CommonHeaders
from .global_storage import ssid_storage, SSID_Storage
from threading import Thread
from socket import socket, SHUT_RD, SOL_SOCKET, SO_REUSEADDR
from typing import Callable
from traceback import print_exception

def gen_400(st: str) -> bytes:
    d = f"400 {st}\n\n"
    return d.encode()

def process_stor(req: Request):
    if ssid_storage[req.common_headers.ssid].ssid == "":
        ssid_storage[req.common_headers.ssid].ssid = req.common_headers.ssid

class Service:
    svc_name: str
    funcs: dict[str, Callable[[Request], Response]] = {}
    def __init__(self, svc_name: str, trusted: bool=True):
        self.trusted = trusted
        self.svc_name = svc_name
    def route(self, path: str):
        def wrap(func: Callable[[Request], Response]):
            self.funcs[path] = func
        return wrap
    def on_404(self, req: Request, sock: socket):
        sock.send(gen_400(f"wtf is {req.path_cleaned}"))
    def handle(self, req: Request, sock: socket):
        process_stor(req)
        p = req.path_cleaned.split(":", 1)[1]
        if not p.startswith("/"):
            p = "/" + p
        func = self.funcs.get(p, None)
        if not func:
            self.on_404(req, sock)
        else:
            try:
                resp = func(req)
                if isinstance(resp, str):
                    sock.send(resp.encode())
                elif isinstance(resp, Response):
                    if resp.headers.get("wtv-trusted", None) == None:
                        trust_map = ['false', 'true']
                        resp.headers['wtv-trusted'] = trust_map[int(self.trusted)]
                    r = resp.construct_response()
                    sock.send(r)
                else:
                    sock.send(gen_400(f"handler returned unknown response type: {type(resp)}"))
            except Exception as e:
                print_exception(e)
                print(" * Returning exception to webtv so i can properly close webtv socket.")
                sock.send(gen_400(f"Server ran into problem, please try again later. Technical details: {e}"))

class FileServe:
    orig_handl: Callable[[Request, socket], None]
    def __init__(self, svc: Service, fdir: str, altname: str=None) -> None:
        self.orig_handl = svc.handle
        self.fdir = fdir
        if altname == None:
            altname = fdir
        self.altname = altname
        svc.handle = self._handle_monkey_patch
    
    def _handle_monkey_patch(self, req: Request, sock: socket):
        process_stor(req)
        p = req.path_cleaned.split(":", 1)[1]
        if not p.startswith("/"):
            p = "/" + p
        f = self.altname
        if not f.startswith("/"):
            f = "/" + f
        if p.startswith(f):
            try:
                p = p.removeprefix(f)
                p = self.fdir + p
                hdrs = {
                    "Content-Type": "application/octet-stream"
                }
                d = open(p, "rb")
                rsp = Response(hdrs, d)
                r = rsp.construct_response_streamed()
                sock.send(r)
                s = sock.sendfile(d)
                print(f" * Sent file {p}, size: {s} bytes")
            except Exception as e:
                print_exception(e)
                print(" * Returning exception to webtv so i can properly close webtv socket.")
                sock.send(gen_400(f"Server ran into problem, please try again later. Technical details: {e}"))
        else:
            self.orig_handl(req, sock) # let Service handle this request
        

def add_common_headers(req: Request):
    ssid = req.headers.get("wtv-client-serial-number")
    incr = int(req.headers.get("wtv-incarnation", "0"))
    btrm_ver = req.headers.get("wtv-client-bootrom-version", "unknown(is this is a webtv?)")
    appr_ver = req.headers.get("wtv-system-version", "unknown(is this is a webtv?)")
    rtype = req.headers.get("wtv-client-rom-type", "unknown(is this is a webtv?)")

    req.common_headers = CommonHeaders(ssid, incr, btrm_ver, appr_ver, rtype)

class MiniServer: # truly a miniserver
    host: str
    port: int
    sock: socket
    svcs: list[Service] = []

    def __init__(self, host: str="0.0.0.0", port: int=1615):
        self.host = host
        self.port = port
    def handle(self, sock: socket, addr: tuple[str, int]):
        sock.settimeout(1)
        req = receive_request(sock)
        add_common_headers(req)
        print(f" * {addr[0]}:{addr[1]}: {req.method} {req.path}")
        svc = req.path_cleaned.split(":", 1)[0]
        for i in self.svcs:
            if i.svc_name == svc:
                i.handle(req, sock)
                print(f" * Closing socker...")
                sock.close()
                print(" * Done.")
                return
        sock.send(gen_400(f"Unknown service: {svc}. Literally, this service doesn't exists, so why you want to access this?"))
        sock.close()
    def start(self):
        self.sock = socket()
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        while True:
            try:
                self.sock.bind((self.host, self.port))
                print(" * Successfully binded on socket")
                break
            except Exception as e:
                print(f" * Exception while binding: {e}, trying again...")
        self.sock.listen(10)
        self.sock.settimeout(0.5)
        print(f" * Listening on {self.host}:{self.port}")
        while True:
            try:
                conn, addr = self.sock.accept()
                th = Thread(target=self.handle, name=f"WTVP Handler for address {addr}", args=(conn, addr, ))
                th.start()
            except TimeoutError:
                pass
            except KeyboardInterrupt:
                print(" * Stopping server...")
                break
        try:
            self.sock.shutdown(SHUT_RD)
        except OSError: pass
        self.sock.close()
        print("Server stopped.")
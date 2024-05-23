from .wtvp import Request, receive_request, Response
from .server import Service, MiniServer, FileServe
from .global_storage import SSID_Storage, ssid_storage
#from .challenge import WTVNetworkSecurity # code by emac

def hide_ssid(s: str):
    l = len(s)
    g = l // 2
    s = list(s)
    l = l - g
    return "".join(s[:g]) + "*"*l

def is_warrior(req: Request): # Is client is a webtv warrior
    w = False
    if req.headers.get('wtv-system-version', '0.0') == '0.0':
        w = True
    return w
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
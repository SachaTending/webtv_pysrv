from srv import MiniServer, Service, Request, Response, ssid_storage, SSID_Storage, hide_ssid, is_warrior
from headwaiter import hdwtr
import headwaiter
from register import srv as regsrv
from home import wtvhome, wtvcenter
from wtvmail import wtvmail as mailsvc
from settings import wtvserv as wtvsett
from spotads import wtvspot
from content import content
from os import urandom
from base64 import b64encode, b64decode
from conf import fetch_conf
from challenge import gen_challenge
from json import dumps

try:
    from loguru import logger
except ImportError:
    from srv import LoguruFallback
    logger = LoguruFallback()

__name__ = "Server main"

s = Service("wtv-1800")

def gen_key():
    return b64encode(urandom(8)).decode()

def issue_challnge(req: Request) -> str:
    ssid = req.common_headers.ssid
    logger.info(f"Generating new challenge for SSID {hide_ssid(req.common_headers.ssid)}")
    ssid = req.common_headers.ssid
    ch = ssid_storage[ssid].security.IssueChallenge()
    sl = ssid_storage[ssid].security.ProcessChallenge(ch)
    ssid_storage[ssid].challenge, ssid_storage[ssid].challenge_solved = ch, sl

@s.route("/preregister")
def prereg(req: Request):
    hdrs = {
        "wtv-phone-log-url": "wtv-1800:/post-phone-log",
        "Content-Type": "text/html"
    }
    return Response(hdrs)

conf = fetch_conf()

@s.route("/post-phone-log")
def post_phone_log(req: Request):
    hdrs = {
        'Content-Type': 'text/html',
        'wtv-service': ['reset', f'host={conf["service_ip"]} port={conf["port"]} name=wtv-1800 flags=0x00000004'],
        "wtv-visit": "wtv-1800:/finish-prereg"
    }
    return Response(hdrs)

tellyList = [
    {
        'rom_type': [
            'US-LC2-disk-0MB-8MB',
            'US-LC2-disk-0MB-8MB-softmodem-CPU5230',
            'US-BPS-flashdisk-0MB-8MB-softmodem-CPU5230',
            'US-LC2-flashdisk-0MB-16MB-softmodem-CPU5230',
            'US-WEBSTAR-disk-0MB-16MB-softmodem-CPU5230'
        ],
        'oisp': 'LC2_OISP.tok',
        'normal': 'LC2_normal.tok'
    },
    {
        'rom_type': [
            'bf0app'
        ],
        'oisp': 'bf0_OISP.tok',
        'normal': 'bf0_normal.tok'
    },
    {
        'rom_type': [
            'JP-Fiji'
        ],
        'oisp': 'dc_normal.tok',
        'normal': 'dc_normal.tok'
    }
]

def is_minibrowser(req: Request):
    b1 = req.headers.get('wtv-need-upgrade', None)
    if b1 == None or b1 == 'false':
        b1 = False
    elif b1 == 'true':
        b1 = True
    b2 = req.headers.get('wtv-used-8675309', None)
    if b2 == None or b2 == 'false':
        b2 = False
    elif b2 == 'true':
        b2 = True
    return b1 or b2

def guess_telly(req: Request) -> tuple[str, str]:
    t = "text/tellyscript"
    tel = None
    if req.common_headers.systype == 'US-DTV-disk-0MB-32MB-softmodem-CPU5230':
        if is_minibrowser(req):
            if req.headers.get('wtv-open-access', None) == 'true': tel = tellyList[0]['oisp']
            else: tel = tellyList[0]['normal']
        else:
            t = "text/dialscript"
            if req.headers.get("wtv-lan", None) == 'true':
                tel = "utv_hsd.tok"
            else:
                tel = "utv_normal.tok"
    else:
        for i in tellyList:
            if req.common_headers.systype in i['rom_type']:
                tel = i['oisp']
            else:
                tel = i['normal']
    return t, tel

@s.route("/finish-prereg")
def finish_prereg(req: Request):
    ssid = req.common_headers.ssid
    ssid_storage[ssid].initial_key = gen_key()
    hdrs = {
        "wtv-service": [
            'reset',
            f'host={conf["service_ip"]} port={conf["port"]} name=wtv-head-waiter flags=0x00000001 connections=1',
        ],
        'wtv-visit': 'wtv-head-waiter:/login?',
        'wtv-boot-url': 'wtv-head-waiter:/login',
        "wtv-initial-key": ssid_storage[ssid].initial_key
    }
    logger.info(f"Headers: {dumps(hdrs, indent=4)}")
    tel = guess_telly(req)
    hdrs['Content-Type'] = tel[0]
    if tel[1] != None:
        data = open(f"tellyscripts/{tel[1]}", "rb").read()
        return Response(hdrs, data)
    return Response(hdrs)


@s.route("/fetch-svcs")
def fetch_svcs(req: Request):
    ssid = req.common_headers.ssid
    #ssid_storage[ssid].initial_key = gen_key()
    if not is_warrior(req): ch = gen_challenge(ssid_storage[ssid].initial_key)
    #print(ch, ch[2])
    if not is_warrior(req): ssid_storage[ssid].challenge = b64encode(ch[2]).decode()
    #ssid_storage[ssid].challenge_solved = check_challenge(ch[2], b64decode(ssid_storage[ssid].initial_key.encode()))
    hdrs = {
        'wtv-service': construct_wtv1800_resp(srv=srv),
        'wtv-visit': 'wtv-head-waiter:/login',
        "Content-Type": "text/html",
        #"wtv-challenge": b64encode(ch[2]).decode()
    }
    if not is_warrior(req):
        hdrs['wtv-challenge'] = b64encode(ch[2]).decode()
    else:
        logger.info("Detected WebTV Warrior, challenge-response process is disabled.")
    return Response(hdrs)

special_services_flags = {
    "wtv-1800": "0x00000004",
    "wtv-head-waiter": "0x00000001"
}

def construct_wtv1800_resp(host: str=None, port: int=None, srv: MiniServer=None):
    d = fetch_conf()
    if host == None:
        host = d['service_ip']
    if port == None:
        port = int(d['port'])
    resp = ['reset']
    form = "host={host} port={port} name={name} flags={flags} connections=10"
    for i in srv.svcs:
        resp.append(form.format(host=host, port=port, name=i.svc_name, flags=special_services_flags.get(i.svc_name, "0x00000007")))
    return resp

srv = MiniServer(port=int(fetch_conf()['port']), host=fetch_conf()['bind_host'])

services = [
    s, # wtv-1800
    hdwtr, # wtv-head-waiter
    regsrv, # wtv-register
    wtvhome, # wtv-home
    wtvcenter, # wtv-center
    content, # wtv-content
    mailsvc, # wtv-mail
    wtvsett, # wtv-settings
    wtvspot # wtv-spot
]

headwaiter.srv = srv

srv.svcs.extend(services)
srv.start()

from srv import MiniServer, Service, Request, Response, ssid_storage, SSID_Storage, hide_ssid
from headwaiter import hdwtr
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

s = Service("wtv-1800")

def gen_key():
    return b64encode(urandom(8)).decode()

def issue_challnge(req: Request) -> str:
    ssid = req.common_headers.ssid
    print(f" * Generating new challenge for SSID {hide_ssid(req.common_headers.ssid)}")
    ssid = req.common_headers.ssid
    ch = ssid_storage[ssid].security.IssueChallenge()
    sl = ssid_storage[ssid].security.ProcessChallenge(ch)
    ssid_storage[ssid].challenge, ssid_storage[ssid].challenge_solved = ch, sl

@s.route("/preregister")
def prereg(req: Request):
    ssid = req.common_headers.ssid
    ssid_storage[ssid].initial_key = gen_key()
    hdrs = {
        'wtv-visit': 'wtv-1800:/fetch-svcs',
        "Content-Type": "text/html",
        "wtv-initial-key": ssid_storage[ssid].initial_key
    }
    return Response(hdrs)

@s.route("/fetch-svcs")
def fetch_svcs(req: Request):
    ssid = req.common_headers.ssid
    #ssid_storage[ssid].initial_key = gen_key()
    ch = gen_challenge(b64decode(ssid_storage[ssid].initial_key.encode()))
    print(ch, ch[2])
    ssid_storage[ssid].challenge = b64encode(ch[2]).decode()
    #ssid_storage[ssid].challenge_solved = check_challenge(ch[2], b64decode(ssid_storage[ssid].initial_key.encode()))
    hdrs = {
        'wtv-service': construct_wtv1800_resp(srv=srv),
        'wtv-visit': 'wtv-head-waiter:/login',
        "Content-Type": "text/html",
        "wtv-challenge": b64encode(ch[2]).decode()
    }
    return Response(hdrs)

special_services_flags = {
    "wtv-1800": "0x00000001",
    "wtv-head-waiter": "0x00000004"
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

srv = MiniServer()

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

srv.svcs.extend(services)
srv.start()

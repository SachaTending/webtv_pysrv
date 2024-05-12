from srv import MiniServer, Service, Request, Response, ssid_storage, SSID_Storage, hide_ssid
from headwaiter import hdwtr
from register import srv as regsrv
from os import urandom
from base64 import b64encode

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
        'wtv-visit': 'wtv-1800:/fetch_svcs',
        "Content-Type": "text/html",
        "wtv-initial-key": ssid_storage[ssid].initial_key,
    }
    return Response(hdrs)

@s.route("/fetch_svcs")
def fetch_svcs(req: Request):
    ssid = req.common_headers.ssid
    ssid_storage[ssid].initial_key = gen_key()
    hdrs = {
        'wtv-service': construct_wtv1800_resp(srv=srv),
        'wtv-visit': 'wtv-head-waiter:/login',
        "Content-Type": "text/html",
        "wtv-initial-key": ssid_storage[ssid].initial_key,
    }
    return Response(hdrs)

special_services_flags = {
    "wtv-1800": "0x00000001",
    "wtv-head-waiter": "0x00000004"
}

def construct_wtv1800_resp(host: str="localhost", port: int=1615, srv: MiniServer=None):
    resp = ['reset']
    form = "host={host} port={port} name={name} flags={flags} connections=1"
    for i in srv.svcs:
        resp.append(form.format(host=host, port=port, name=i.svc_name, flags=special_services_flags.get(i.svc_name, "0x00000007")))
    return resp

srv = MiniServer()
srv.svcs.append(s)
srv.svcs.append(hdwtr)
srv.svcs.append(regsrv)
srv.start()

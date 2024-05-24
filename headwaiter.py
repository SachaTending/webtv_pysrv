from srv import Service, Request, ssid_storage, Response, hide_ssid, FileServe, is_warrior, MiniServer
from json import dumps
from usrstor import check_ssid
from base64 import b64decode, b64encode
from challenge import check_challenge, gen_challenge
from conf import fetch_conf

try:
    from loguru import logger
except ImportError:
    from srv import LoguruFallback
    logger = LoguruFallback()

__name__ = "Headwaiter service"

hdwtr = Service("wtv-head-waiter")
fs = FileServe(hdwtr, "imgs", "images")

srv: MiniServer

@hdwtr.route("/login")
def login(req: Request): # simulate full login sequence
    ssid = req.common_headers.ssid
    #ssid_storage[ssid].initial_key = gen_key()
    if not is_warrior(req): ch = gen_challenge(ssid_storage[ssid].initial_key)
    #print(ch, ch[2])
    if not is_warrior(req): ssid_storage[ssid].challenge = b64encode(ch[2]).decode()
    hdrs = {
        "Content-Type": "text/html",
        "wtv-visit": "wtv-head-waiter:/login-stage-two?",
    }
    if not is_warrior(req): hdrs['wtv-challenge'] = ssid_storage[ssid].challenge
    print(hdrs)
    return Response(hdrs, code=(200, 'OK'))


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

@hdwtr.route("/login-stage-two")
def solve_challenge(req: Request):
    logger.info(f"Headers: {dumps(req.headers, indent=4)}")
    ssid = req.common_headers.ssid
    hdrs = {
        "Content-Type": "text/html",
        "wtv-service": construct_wtv1800_resp(srv=srv)
    }
    if not is_warrior(req):
        #if check_challenge(ssid_storage[ssid].challenge, ssid_storage[ssid].initial_key, req.headers['wtv-challenge-response']):
        if False:
            hdrs['wtv-visit'] = 'wtv-1800:/fetch-svcs'
            logger.info("Challenge is not solved, retrying...")
    else:
        logger.info("Detected WebTV Warrior, challenge-response process is disabled.")
    if True:
        hdrs['wtv-visit'] = 'wtv-head-waiter:/final-stage'
    else:
        hdrs['wtv-visit'] = 'wtv-register:/register'
    return Response(hdrs)

@hdwtr.route("/final-stage")
def final_stage(req: Request):
    hdrs = {
        "Content-Type": "text/html",
        "wtv-home-url": "wtv-home:/home",
        "wtv-boot-url": "wtv-head-waiter:/login?",
        "wtv-reconnect-url": "wtv-head-waiter:/login?",
        "wtv-settings-url": "wtv-setup:/retrieve",
        "wtv-visit": "wtv-home:/home"
    }
    return Response(hdrs)

@hdwtr.route("/technical")
def tech(req: Request):
    hdrs = {
        "Content-Type": "text/html"
    }
    t = "<p>Info: "
    t += str(req.common_headers)
    t += "</p>"
    return Response(hdrs, t)
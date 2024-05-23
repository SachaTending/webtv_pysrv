from srv import Service, Request, ssid_storage, Response, hide_ssid, FileServe, is_warrior
from json import dumps
from usrstor import check_ssid
from base64 import b64decode
from challenge import check_challenge

hdwtr = Service("wtv-head-waiter")
fs = FileServe(hdwtr, "imgs", "images")


@hdwtr.route("/login")
def login(req: Request): # simulate full login sequence
    ssid = req.common_headers.ssid
    print(f" * Headers: {dumps(req.headers, indent=4)}")
    hdrs = {
        "Content-Type": "text/html",
        "wtv-visit": "wtv-head-waiter:/login-stage-two",
    }
    if not is_warrior(req):
        if check_challenge(b64decode(ssid_storage[ssid].challenge.encode()), b64decode(ssid_storage[ssid].initial_key.encode()), b64decode(req.headers['wtv-challenge-response'].encode())):
            hdrs['wtv-visit'] = 'wtv-1800:/fetch-svcs'
            print(" * Challenge is not solved, retrying...")
    else:
        print(" * Detected WebTV Warrior, challenge-response process is disabled.")
    return Response(hdrs, code=(200, 'OK'))

@hdwtr.route("/login-stage-two")
def solve_challenge(req: Request):
    hdrs = {
        "Content-Type": "text/html"
    }
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
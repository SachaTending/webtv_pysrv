from srv import Service, Request, ssid_storage, Response, hide_ssid, FileServe
from json import dumps
from usrstor import check_ssid

hdwtr = Service("wtv-head-waiter")
fs = FileServe(hdwtr, "imgs", "images")


@hdwtr.route("/login")
def login(req: Request): # simulate full login sequence
    hdrs = {
        "Content-Type": "text/html",
        "wtv-visit": "wtv-head-waiter:/login-stage-two",
    }
    return Response(hdrs, code=(200, 'OK'))

@hdwtr.route("/login-stage-two")
def solve_challenge(req: Request):
    hdrs = {
        "Content-Type": "text/html"
    }
    if check_ssid(req):
        hdrs['wtv-visit'] = 'wtv-head-waiter:/technical'
    else:
        hdrs['wtv-visit'] = 'wtv-register:/register'
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
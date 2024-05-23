from srv import Service, Request, Response

wtvspot = Service("wtv-spot")

"""
wtv-spot-queue-add: queue=1&adID=0000001202cbda8500000000&creative=wtv-spot:/shared/ads/ZD/YIL.GIF
wtv-videoad-playid: 0000001c02cbda8500000000
wtv-videoad-playname: joinus.mpg
"""

@wtvspot.route("/test")
def test(req: Request):
    hdrs = {
        "Content-Type": "text/html",
        "wtv-spot-queue-add": "queue=1&adID=test123&creative=wtv-spot:/shared/ads/ZD/YIL.GIF",
        "wtv-videoad-playid": "test123",
        "wtv-videoad-playname": "joinus.mpg",
        "wtv-visit": "wtv-home:/home"
    }
    return Response(hdrs)
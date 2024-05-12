from srv import Request, Service, Response

srv = Service("wtv-register")

@srv.route("/register")
def register(req: Request) -> Response:
    hdrs = {
        "Content-Type": "text/html"
    }
    data = open("files/webtvhalted.html").read()
    return Response(hdrs, data)

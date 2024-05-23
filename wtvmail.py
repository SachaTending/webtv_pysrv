from srv import Service, Request, Response

wtvmail = Service("wtv-mail")

@wtvmail.route("/mailbox-image")
def mbox_icon(req: Request):
    hdrs = {
        "Content-Type": "image/gif"
    }
    data = open("content/mail.gif", "rb").read()
    return Response(hdrs, data)
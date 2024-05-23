from srv import Service, Response, Request

wtvhome = Service("wtv-home")
wtvcenter = Service("wtv-center")

@wtvhome.route("/home")
def home(req: Request):
    hdrs = {
        "Content-Type": "text/html"
    }
    return Response(hdrs,open("content/home/home.html").read())

@wtvcenter.route("/templates/en-US/CustomInfoLoadingGrunge.tmpl")
def news_center(req: Request):
    hdrs = {
        "Content-Type": "text/html"
    }
    return Response(hdrs,open("content/center/news.html").read())

@wtvcenter.route("/custom-info-teaser")
def custom_info_teaser(req: Request):
    hdrs = {
        "Content-Type": "text/html"
    }
    data = f"""<p>i don't think you want {req.opts['info']}"""
    return Response(hdrs, data)

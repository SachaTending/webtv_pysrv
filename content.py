from srv import Service, FileServe

content = Service("wtv-content")

fsrv = FileServe(content, "content/", "/")
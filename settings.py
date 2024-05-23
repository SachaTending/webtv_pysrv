from srv import Service, Request, Response

wtvserv = Service("wtv-setup")

@wtvserv.route("/retrieve")
def retrieve_settings(req: Request):
    hdrs = {
        "Content-Type": "text/html",
        "wtv-backgroundmusic-load-playlist": "wtv-setup:/get-playlist"
    }
    data = "from-server=1&setup-advanced-options=0&setup-play-bgm=1&setup-bgm-tempo=-1&setup-bgm-volume=100&setup-background-color=c6c6c6&setup-font-sizes=medium&setup-in-stereo=1&setup-keyboard=alphabetical&setup-link-color=2222bb&setup-play-songs=1&setup-play-sounds=1&setup-text-color=0&setup-visited-color=8822bb&setup-japan-keyboard=roman&setup-japan-softkeyboard=roman&setup-chat-access-level=0&setup-chat-on-nontrusted-pages=1&setup-tv-chat-level=2"
    return Response(hdrs, data)


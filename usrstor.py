from srv import Request
from typing import TypedDict
from os.path import exists

def check_ssid(req: Request):
    return exists(f"SSIDStore/{req.common_headers.ssid}.json")

def check_uname(uname: str):
    return exists(f"UserStore/{uname}")

class SSIDInfo(TypedDict):
    username: str


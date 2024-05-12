from typing import TypedDict
from configparser import ConfigParser
from os.path import exists

class Config(TypedDict):
    service_ip: str
    port: int

cparse = ConfigParser()
cparse['Config'] = {}
cparse['Config']['service_ip'] = '127.0.0.1'
cparse['Config']['port'] = "1615"

if exists("config.ini"): cparse.read_file(open("config.ini"))
else: cparse.write(open("config.ini", "w"))

def fetch_conf() -> Config:
    cfg = {
        "service_ip": cparse['Config']['service_ip'],
        "port": int(cparse['Config']['port'])
    }
    return cfg
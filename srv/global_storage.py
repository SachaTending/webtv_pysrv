from dataclasses import dataclass
from json import dumps

@dataclass
class SSID_Storage:
    ssid: str = ""
    initial_key: str = ""
    challenge: str = ""
    challenge_solved: str = ""
    counter: int = 10000000
    counter_orig: int = counter

class Storage1:
    def __init__(self, name: str="SSID") -> None:
        if globals().get(f"STORAGE_{name}", None) == None:
            globals()[f"STORAGE_{name}"] = {}
        self.name = name

    def prettify(self):
        return globals()[f"STORAGE_{self.name}"]

    def __getitem__(self, ind: str) -> SSID_Storage:
        a: dict[str, SSID_Storage] = globals()[f"STORAGE_{self.name}"]
        if a.get(ind, None) == None:
            a[ind] = SSID_Storage(ind)
            globals()[f"STORAGE_{self.name}"] = a
        return a[ind]
    def __setitem__(self, ind: str, dat: SSID_Storage):
        a: dict[str, SSID_Storage] = globals()[f"STORAGE_{self.name}"]
        a[ind] = dat
        globals()[f"STORAGE_{self.name}"] = a
    def __delitem__(self, ind: str):
        a: dict[str, SSID_Storage] = globals()[f"STORAGE_{self.name}"]
        if a.get(ind, None) != None:
            del a[ind]
        globals()[f"STORAGE_{self.name}"] = a

ssid_storage = Storage1()
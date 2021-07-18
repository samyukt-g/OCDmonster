import os
import shutil
import ctypes
import json
from ctypes import windll, wintypes
from uuid import UUID

# source [1] start
class GUID(ctypes.Structure):
    # declares native C data types being used in the class
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8)
    ]

    def __init__(self, uuidstr):
        uuid = UUID(uuidstr)
        ctypes.Structure.__init__(self)
        self.Data1, self.Data2, self.Data3, \
            self.Data4[0], self.Data4[1], rest = uuid.fields
        for i in range(2, 8):
            self.Data4[i] = rest >> (8-i-1)*8 & 0xff


SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
SHGetKnownFolderPath.argtypes = [
    ctypes.POINTER(GUID), wintypes.DWORD,
    wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
]
# source end

# uuidstr values for root dirs in uuids.json
# retrieves builtin folder path from GUID with its uuid as inp
def _get_known_folder_path(uuidstr):
    pathptr = ctypes.c_wchar_p()
    guid = GUID(uuidstr)
    if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
        raise ctypes.WinError()
    return pathptr.value  # path of the builtin folder


f = open('uuids.json',)
uuids = json.load(f)
for i in uuids["uuids"]:
    if i["dir"] == "Downloads":
        uuid_id = i["id"]
        flist = os.listdir(_get_known_folder_path(uuid_id))
        print(flist)
        for fel in flist:
            print(fel)
            fel_path_info = os.path.splitext(fel)
            # print(el_path_info[0], ": ", el_path_info[1])
            config = open('config.json')
            config_data = json.load(config)
            for conf in config_data["fileBindings"]:
                if fel_path_info[1] == conf[1]:
                    # print(conf[0])
                    for u in uuids["uuids"]:
                        print(u)
                        if u["dir"] == conf[0]:
                            src = _get_known_folder_path(uuid_id) + "\\" + fel
                            dest = _get_known_folder_path(u["id"]) + "\\" + fel
                            print(src, " => ", dest)
                            # os.rename(src, dest)
                            shutil.move(src, dest)
                            # os.replace(src, dest)
                            print("Completed...")

            config.close()
f.close()

# source [1]: https://gist.github.com/mkropat/7550097

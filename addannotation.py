import json
import os
import re
import sqlite3

fname = 'jaffpota.json'
con = sqlite3.connect('jaffpota.db')
cur = con.cursor()


trans_dict = {}


trans_data = {
    'JAFF-0024': {},
    'JAFF-0114': {69, 80, 87, 88, 89, 91, 93, 96, 99},
    'JAFF-0115': {71, 72, 73, 74, 82, 90, 92, 94, 95, 97, 98, 100, 105, 109},
    'JAFF-0024,0115': {},
    'JAFF-0114,0115': {},
    'JAFF-0024,0114,0115': {77},

    'JAFF-0094': {344, 345},
    'JAFF-0107': {772},
    'JAFF-0101': {675},
    'JAFF-0102': {674},
    'JAFF-0103': {133, 134, 135, 138, 139},
    'JAFF-0104,0105': {397},
    'JAFF-0105': {398},
    'JAFF-0106': {409, 408, 407, 406, 405, 404, 403, 402, 401, 400, 393, 392},
    'JAFF-0108': {664},
    'JAFF-0109': {202, 201, 200, 199, 198, 197, 196},
    'JAFF-0110': {1090, 1091},
    'JAFF-0111': {1110, 1111},
    'JAFF-0112': {678},
    'JAFF-0113': {187, 180, 179, 178, 177, 176, 175, 174, 173, 171, 170, 169, 168, 167, 166, 165, 164, 163, 162, 161, 160},
}

trans_name = {
    'JAFF-0094': ('JA-0013', '妙高戸隠連山国立公園')
}

for jaff in trans_data:
    for uid in trans_data[jaff]:
        trans_dict[uid] = jaff

print(trans_dict)


def jaff_replace(jaff, pota, pid, uid):
    namek = None
    try:
        newjaff = trans_dict[int(uid)]
        print("Replace:"+jaff+' to '+newjaff)
    except KeyError:
        return (jaff, pota, namek)

    try:
        (newpota, namek) = trans_name[newjaff]
        return (newjaff, newpota, namek)
    except KeyError:
        return (newjaff, pota, namek)


def setotable(jaffid, pid, uid):
    pattern = [
        'JAFF-0024', 'JAFF-0114', 'JAFF-0115', 'JAFF-0024,0115', 'JAFF-0114,0115',
        'JAFF-0024,0114,0115', 'JAFF-0104,105', 'JAFF-0106', 'JAFF-0101', 'JAFF-0102',
        'JAFF-0103', 'JAFF-0108', 'JAFF-0109', 'JAFF-0110', 'JAFF-0111',
        'JAFF-0112', 'JAFF-0113', 'JAFF-0094']
    setodict = {
        14: 12, 28: 18, 29: 18, 23: 10, 24: 9, 55: 2, 56: 1, 57: 1, 58: 2, 59: 1, 60: 1, 61: 1, 62: 2, 63: 1, 64: 2,
        65: 2, 66: 1, 67: 2, 68: 3, 69: 1, 70: 3, 71: 3, 72: 3, 73: 3, 74: 3,
        75: 1, 76: 2, 77: 3, 78: 1, 79: 1, 80: 1, 81: 3, 82: 4, 83: 2, 84: 3,
        85: 4, 86: 1, 87: 3, 88: 3, 89: 1, 90: 2, 91: 2, 92: 3, 93: 3, 95: 1,
        96: 1, 97: 1, 98: 1, 99: 3, 100: 3, 101: 3, 102: 3, 103: 3, 104: 3, 105: 3,
        106: 3, 107: 3, 108: 3, 109: 3, 110: 3, 111: 3, 112: 3, 113: 3,
        128: 17, 129: 17, 130: 17, 131: 17, 132: 17, 133: 17, 134: 17, 135: 17, 137: 17, 138: 17, 139: 17, 149: 17, 150: 17, 151: 17, 152: 17, 153: 17, 154: 17,
        1823: 17, 1824: 17, 1825: 17, 1828: 17,
        1507: 14, 1508: 14, 1520: 15, 1521: 15, 1567: 16,
        1812: 5, 1813: 3, 1814: 6,
        1797: 7, 36: 7, 41: 8, 42: 8, 43: 8, 44: 8, 1798: 8, 1799: 8, 1800: 8, 1801: 8, 1802: 8, 1803: 8, 1804: 8, 1805: 8,
        157: 13, 1817: 11, 1829: 13, 1830: 13, 1831: 13, }
    try:
        return pattern[setodict[int(uid)] - 1]
    except KeyError:
        return jaffid


with open(fname) as f:
    src = json.load(f)

for elem in src['objects']['jaffpota']['geometries']:
    jaff = elem['properties']['JAFF']
    pid = elem['properties']['PID']
    uid = elem['properties']['UID']
    res = cur.execute(f"select * from jaffpota where jaff = '{jaff}'")
    res = cur.fetchone()
    if res:
        (pota, jaff, name, location, locid, type, level, namek, lat, lng) = res
        namek = re.sub(r'\(.*\)', '', namek)
        namek = re.sub(r'（.*）', '', namek)
        (jaff_r, pota_r, namek_r) = jaff_replace(jaff, pota, pid, uid)
        if namek_r:
            namek = namek_r

        elem['properties'] = {'JAFF': jaff_r,
                              'POTA': pota_r, 'PID': pid, 'UID': uid, 'NAME': namek}
    else:
        print(f'Fatal error: {jaff}')

base = os.path.splitext(os.path.basename(fname))[0]
out = open(base + '-annotated.json', mode='w', encoding='utf8')
out.write(json.dumps(src))

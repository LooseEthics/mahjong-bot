
# open meld types
ANKAN = 0
PON = 1
CHII = 2
MINKAN = 3
SHOUMINKAN = 4
Kans = (ANKAN, MINKAN, SHOUMINKAN)
OMNames = {
    ANKAN: "Ankan",
    PON: "Pon",
    CHII: "Chii",
    MINKAN: "Minkan",
    SHOUMINKAN: "Shouminkan"
    }
WNames = ("East", "South", "West", "North")
TenhouStr = "mpsz"
KokushiTiles = (0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33)

def tilelist2tenhou(l: list[int], sort = True) -> str:
    l = sorted(l) if sort else l
    out_str = ""
    csuit = -1
    nsuit = -1
    for tile in l:
        nsuit = tile // 9
        if csuit != nsuit:
            if csuit > -1:
                out_str += TenhouStr[csuit]
            csuit = nsuit
        out_str += str((tile % 9) + 1)
    out_str += TenhouStr[csuit]
    return out_str

def onetile2tenhou(tile: int) -> str:
    return str((tile % 9) + 1) + TenhouStr[tile // 9] if tile >= 0 else "--"

def tenhou2tilelist(s: str) -> list[int]:
    l = []
    back = 0
    for x in s:
        if x >= "1" and x <= "9":
            l.append(int(x) - 1)
            back += 1
        else:
            suit_num = TenhouStr.index(x)
            for i in range(len(l) - back, len(l)):
                l[i] += suit_num * 9
            back = 0
    return l

def tenhou2onetile(tile: str) -> int:
    print("called tenhou2onetile with", tile)
    return TenhouStr.index(tile[1]) * 9 + int(tile[0]) - 1

def lstsub(lst1: list, lst2: list) -> list:
    ## difference of lists
    out = lst1[:]
    for x in lst2:
        out.remove(x)
    return out

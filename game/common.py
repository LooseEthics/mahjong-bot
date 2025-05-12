
# open meld types
INVALID_MELD = -1
ANKAN = 0
PON = 1
CHII = 2
MINKAN = 3
SHOUMINKAN = 4
PAIR = 5
Kans = (ANKAN, MINKAN, SHOUMINKAN)

TenhouStr = "mpsz"
JIHAI_OFFSET = 27
TON = 27
NAN = 28
SHAA = 29
PEI = 30
Kazehai = (TON, NAN, SHAA, PEI)
SANGEN_OFFSET = 31
HAKU = 31
HATSU = 32
CHUN = 33
Sangenpai = (HAKU, HATSU, CHUN)
Jihai = tuple(list(Kazehai) + list(Sangenpai))
Terminals = (0, 8, 9, 17, 18, 26)
KokushiTiles = tuple(list(Jihai) + list(Terminals))
RyuuiisouTiles = (10, 11, 12, 14, 16, HATSU) ## s23468z6

INVALID_PLAYER = -1
INVALID_ROUND = -1
INVALID_TILE = -1
INVALID_TURN = -1

AGARI = -1
TENPAI = 0
IISHANTEN = 1

GS_ONGOING = 0
GS_RYUUKYOKU = 1
GS_RON = 2
GS_TSUMO = 3

OMNames = {
    INVALID_MELD: "Invalid Meld",
    ANKAN: "Ankan",
    PON: "Pon",
    CHII: "Chii",
    MINKAN: "Minkan",
    SHOUMINKAN: "Shouminkan"
    }

WNames = {
    INVALID_PLAYER: "Invalid Player",
    TON - JIHAI_OFFSET: "East", 
    NAN - JIHAI_OFFSET: "South", 
    SHAA - JIHAI_OFFSET: "West", 
    PEI - JIHAI_OFFSET: "North"
    }

def tilelist2tenhou(l: list[int], sort = True) -> str:
    if len(l) == 0:
        return "[]"
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
    #print("called tenhou2onetile with", tile)
    try:
        return TenhouStr.index(tile[1]) * 9 + int(tile[0]) - 1
    except:
        return INVALID_TILE

def lstsub(lst1: list, lst2: list) -> list:
    ## difference of lists
    out = lst1[:]
    for x in lst2:
        out.remove(x)
    return out

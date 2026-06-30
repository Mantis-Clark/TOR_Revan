"""NSS -> NCS compiler wrapper (pure-Python, via PyKotor). Targets K1 or K2."""
from pykotor.resource.formats.ncs import compile_nss, bytes_ncs
from pykotor.common.misc import Game

def compile_source(source: str, game: str = "K2") -> bytes:
    g = Game.K2 if game.upper() == "K2" else Game.K1
    return bytes(bytes_ncs(compile_nss(source, g)))

def compile_file(nss_path: str, ncs_path: str, game: str = "K2") -> int:
    src = open(nss_path, encoding="utf-8", errors="replace").read()
    data = compile_source(src, game)
    open(ncs_path, "wb").write(data)
    return len(data)

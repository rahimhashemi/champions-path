"""2026/27 Europa League snapshot after Matchday 5.

Team names are ASCII-normalised to keep CSV and CLI output portable. Fixtures
and completed scores come from UEFA's official competition schedule.
"""

PRESEASON = {
    "Leverkusen": 1930, "Milan": 1875, "Bournemouth": 1860, "Juventus": 1845,
    "Benfica": 1840, "Real Sociedad": 1820, "Marseille": 1810,
    "Crystal Palace": 1810, "Hoffenheim": 1800, "Lyon": 1785, "Celta": 1780,
    "Rennes": 1765, "AZ Alkmaar": 1765, "Olympiacos": 1750,
    "Salzburg": 1745, "Sunderland": 1740, "Union SG": 1740,
    "Besiktas": 1735, "Celtic": 1725, "Anderlecht": 1715,
    "Sparta Praha": 1710, "GNK Dinamo": 1695, "Viktoria Plzen": 1690,
    "NEC": 1690, "Ferencvaros": 1685, "Sturm Graz": 1665,
    "Lech Poznan": 1645, "Jagiellonia": 1640, "Hapoel Beer-Sheva": 1600,
    "Omonia": 1600, "Levski Sofia": 1590, "OFI Crete": 1585,
    "Celje": 1580, "Lillestrom": 1570, "Torreense": 1560,
    "Ararat-Armenia": 1500,
}

COEFFICIENTS = {
    "Leverkusen": 105.000, "Benfica": 90.000, "Juventus": 72.250,
    "Milan": 66.000, "Lyon": 65.750, "AZ Alkmaar": 62.875,
    "Olympiacos": 62.250, "Real Sociedad": 57.000, "Marseille": 54.000,
    "Ferencvaros": 51.250, "Viktoria Plzen": 50.500, "Union SG": 48.000,
    "GNK Dinamo": 46.500, "Salzburg": 45.000, "Celtic": 44.000,
    "Sparta Praha": 38.250, "Rennes": 35.000, "Anderlecht": 30.750,
    "Sturm Graz": 28.000, "Lech Poznan": 27.250, "Bournemouth": 23.903,
    "Crystal Palace": 23.903, "Sunderland": 23.903, "Celje": 23.000,
    "Jagiellonia": 22.000, "Omonia": 21.250, "Celta": 19.409,
    "Hoffenheim": 18.580, "Besiktas": 15.500, "Torreense": 14.633,
    "Hapoel Beer-Sheva": 14.000, "NEC": 13.585, "OFI Crete": 9.682,
    "Lillestrom": 8.247, "Ararat-Armenia": 7.000, "Levski Sofia": 7.000,
}

_RAW_FIXTURES = """Ararat-Armenia|Sparta Praha
Omonia|Celta
Milan|Benfica
Leverkusen|Celje
Hapoel Beer-Sheva|GNK Dinamo
Olympiacos|Jagiellonia
Anderlecht|Lyon
Sturm Graz|Rennes
Sunderland|AZ Alkmaar
OFI Crete|Hoffenheim
Levski Sofia|Salzburg
Besiktas|Marseille
Celtic|Ferencvaros
Crystal Palace|Lech Poznan
Viktoria Plzen|Union SG
Juventus|NEC
Lillestrom|Torreense
Real Sociedad|Bournemouth
Sparta Praha|Lillestrom
AZ Alkmaar|Hapoel Beer-Sheva
Salzburg|Milan
Lech Poznan|Leverkusen
Celje|Omonia
Lyon|Crystal Palace
Union SG|Real Sociedad
Torreense|Sunderland
Bournemouth|Sturm Graz
Ferencvaros|Viktoria Plzen
GNK Dinamo|Anderlecht
Jagiellonia|Ararat-Armenia
NEC|Levski Sofia
Marseille|Olympiacos
Celta|Juventus
Benfica|Celtic
Rennes|OFI Crete
Hoffenheim|Besiktas
Ararat-Armenia|AZ Alkmaar
Ferencvaros|Torreense
GNK Dinamo|NEC
Juventus|Rennes
Lech Poznan|Sunderland
OFI Crete|Leverkusen
Union SG|Hapoel Beer-Sheva
Sturm Graz|Marseille
Bournemouth|Milan
Besiktas|Crystal Palace
Celtic|Celta
Viktoria Plzen|Levski Sofia
Jagiellonia|Anderlecht
Lillestrom|Real Sociedad
Celje|Salzburg
Olympiacos|Sparta Praha
Omonia|Benfica
Hoffenheim|Lyon
Rennes|Olympiacos
Milan|Ferencvaros
Sparta Praha|Bournemouth
Crystal Palace|Hoffenheim
Lillestrom|Viktoria Plzen
NEC|Omonia
Levski Sofia|Jagiellonia
Real Sociedad|Lyon
Anderlecht|Salzburg
AZ Alkmaar|Juventus
Leverkusen|Marseille
Celtic|Besiktas
Hapoel Beer-Sheva|OFI Crete
Celta|Union SG
Torreense|Ararat-Armenia
Sturm Graz|Celje
Benfica|Lech Poznan
Sunderland|GNK Dinamo
Besiktas|Hapoel Beer-Sheva
Salzburg|Ararat-Armenia
Viktoria Plzen|Benfica
GNK Dinamo|Leverkusen
Olympiacos|Milan
Marseille|Levski Sofia
Union SG|Lech Poznan
Celta|Bournemouth
Sparta Praha|AZ Alkmaar
Crystal Palace|Real Sociedad
Ferencvaros|Celje
Juventus|Omonia
NEC|Rennes
OFI Crete|Anderlecht
Lyon|Lillestrom
Torreense|Celtic
Sunderland|Jagiellonia
Hoffenheim|Sturm Graz
AZ Alkmaar|Sturm Graz
Ararat-Armenia|NEC
Hapoel Beer-Sheva|Juventus
Jagiellonia|Crystal Palace
Marseille|Celta
Omonia|Celtic
Anderlecht|Hoffenheim
Rennes|GNK Dinamo
Celje|Olympiacos
Milan|Sunderland
Bournemouth|Viktoria Plzen
Leverkusen|Besiktas
Salzburg|Sparta Praha
Lech Poznan|Ferencvaros
Lyon|Union SG
Levski Sofia|Lillestrom
Real Sociedad|Torreense
Benfica|OFI Crete
Besiktas|Union SG
Ararat-Armenia|Celje
Ferencvaros|Juventus
Jagiellonia|Lyon
Lillestrom|Bournemouth
NEC|Benfica
Olympiacos|Hoffenheim
Real Sociedad|Viktoria Plzen
Sturm Graz|OFI Crete
AZ Alkmaar|GNK Dinamo
Leverkusen|Salzburg
Celtic|Marseille
Crystal Palace|Sparta Praha
Hapoel Beer-Sheva|Celta
Lech Poznan|Torreense
Levski Sofia|Milan
Anderlecht|Sunderland
Rennes|Omonia
Milan|Ararat-Armenia
Sparta Praha|Rennes
Bournemouth|Hapoel Beer-Sheva
Salzburg|Crystal Palace
Viktoria Plzen|Jagiellonia
GNK Dinamo|Sturm Graz
Juventus|Real Sociedad
Celje|NEC
OFI Crete|Lech Poznan
Marseille|Anderlecht
Lyon|Leverkusen
Omonia|Besiktas
Union SG|Celtic
Celta|Lillestrom
Torreense|Olympiacos
Benfica|AZ Alkmaar
Sunderland|Levski Sofia
Hoffenheim|Ferencvaros"""

GAMES = [tuple(line.split("|")) for line in _RAW_FIXTURES.splitlines()]

MD1 = {
    ("Ararat-Armenia", "Sparta Praha"): (1, 4), ("Omonia", "Celta"): (1, 0),
    ("Milan", "Benfica"): (0, 2), ("Leverkusen", "Celje"): (2, 0),
    ("Hapoel Beer-Sheva", "GNK Dinamo"): (0, 0), ("Olympiacos", "Jagiellonia"): (2, 1),
    ("Anderlecht", "Lyon"): (1, 2), ("Sturm Graz", "Rennes"): (0, 0),
    ("Sunderland", "AZ Alkmaar"): (1, 0), ("OFI Crete", "Hoffenheim"): (2, 0),
    ("Levski Sofia", "Salzburg"): (0, 1), ("Besiktas", "Marseille"): (4, 1),
    ("Celtic", "Ferencvaros"): (1, 3), ("Crystal Palace", "Lech Poznan"): (4, 0),
    ("Viktoria Plzen", "Union SG"): (0, 3), ("Juventus", "NEC"): (5, 0),
    ("Lillestrom", "Torreense"): (1, 2), ("Real Sociedad", "Bournemouth"): (1, 2),
}
MD2 = {
    ("Sparta Praha", "Lillestrom"): (1, 1), ("AZ Alkmaar", "Hapoel Beer-Sheva"): (2, 1),
    ("Salzburg", "Milan"): (0, 4), ("Lech Poznan", "Leverkusen"): (0, 4),
    ("Celje", "Omonia"): (0, 3), ("Lyon", "Crystal Palace"): (3, 2),
    ("Union SG", "Real Sociedad"): (1, 1), ("Torreense", "Sunderland"): (1, 2),
    ("Bournemouth", "Sturm Graz"): (3, 0), ("Ferencvaros", "Viktoria Plzen"): (2, 1),
    ("GNK Dinamo", "Anderlecht"): (1, 0), ("Jagiellonia", "Ararat-Armenia"): (3, 1),
    ("NEC", "Levski Sofia"): (1, 1), ("Marseille", "Olympiacos"): (0, 1),
    ("Celta", "Juventus"): (1, 2), ("Benfica", "Celtic"): (4, 1),
    ("Rennes", "OFI Crete"): (2, 1), ("Hoffenheim", "Besiktas"): (2, 3),
}
MD3 = {
    ("Ararat-Armenia", "AZ Alkmaar"): (0, 4), ("Ferencvaros", "Torreense"): (4, 1),
    ("GNK Dinamo", "NEC"): (2, 4), ("Juventus", "Rennes"): (2, 2),
    ("Lech Poznan", "Sunderland"): (1, 1), ("OFI Crete", "Leverkusen"): (0, 2),
    ("Union SG", "Hapoel Beer-Sheva"): (4, 0), ("Sturm Graz", "Marseille"): (1, 0),
    ("Bournemouth", "Milan"): (3, 0), ("Besiktas", "Crystal Palace"): (2, 2),
    ("Celtic", "Celta"): (1, 2), ("Viktoria Plzen", "Levski Sofia"): (1, 2),
    ("Jagiellonia", "Anderlecht"): (0, 3), ("Lillestrom", "Real Sociedad"): (0, 6),
    ("Celje", "Salzburg"): (2, 2), ("Olympiacos", "Sparta Praha"): (1, 0),
    ("Omonia", "Benfica"): (1, 4), ("Hoffenheim", "Lyon"): (3, 0),
}
MD4 = {
    ("Rennes", "Olympiacos"): (0, 0), ("Milan", "Ferencvaros"): (0, 2),
    ("Sparta Praha", "Bournemouth"): (1, 3), ("Crystal Palace", "Hoffenheim"): (1, 1),
    ("Lillestrom", "Viktoria Plzen"): (0, 1), ("NEC", "Omonia"): (3, 1),
    ("Levski Sofia", "Jagiellonia"): (1, 0), ("Real Sociedad", "Lyon"): (1, 1),
    ("Anderlecht", "Salzburg"): (2, 0), ("AZ Alkmaar", "Juventus"): (1, 2),
    ("Leverkusen", "Marseille"): (0, 1), ("Celtic", "Besiktas"): (3, 2),
    ("Hapoel Beer-Sheva", "OFI Crete"): (0, 2), ("Celta", "Union SG"): (1, 2),
    ("Torreense", "Ararat-Armenia"): (3, 2), ("Sturm Graz", "Celje"): (2, 3),
    ("Benfica", "Lech Poznan"): (3, 1), ("Sunderland", "GNK Dinamo"): (0, 2),
}
MD5 = {
    ("Besiktas", "Hapoel Beer-Sheva"): (2, 1), ("Salzburg", "Ararat-Armenia"): (2, 0),
    ("Viktoria Plzen", "Benfica"): (4, 0), ("GNK Dinamo", "Leverkusen"): (0, 2),
    ("Olympiacos", "Milan"): (2, 4), ("Marseille", "Levski Sofia"): (1, 0),
    ("Union SG", "Lech Poznan"): (2, 2), ("Celta", "Bournemouth"): (1, 2),
    ("Sparta Praha", "AZ Alkmaar"): (2, 4), ("Crystal Palace", "Real Sociedad"): (2, 1),
    ("Ferencvaros", "Celje"): (0, 0), ("Juventus", "Omonia"): (4, 1),
    ("NEC", "Rennes"): (3, 1), ("OFI Crete", "Anderlecht"): (1, 3),
    ("Lyon", "Lillestrom"): (0, 0), ("Torreense", "Celtic"): (1, 2),
    ("Sunderland", "Jagiellonia"): (1, 1), ("Hoffenheim", "Sturm Graz"): (3, 1),
}

PLAYED_ROUNDS = (MD1, MD2, MD3, MD4, MD5)
FIXED = {match: score for round_results in PLAYED_ROUNDS for match, score in round_results.items()}

assert len(PRESEASON) == 36
assert set(PRESEASON) == set(COEFFICIENTS)
assert len(GAMES) == 144
assert len(set(GAMES)) == 144
assert all(home in PRESEASON and away in PRESEASON for home, away in GAMES)
assert len(FIXED) == 90

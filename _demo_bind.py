import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row
conn.execute("CREATE TABLE offers (id INTEGER PRIMARY KEY, external_id TEXT, title TEXT)")
conn.executemany(
    "INSERT INTO offers (external_id, title) VALUES (?, ?)",
    [("olx_1", "Kawalerka"), ("olx_2", "Dwupokojowe"), ("olx_3", "Studio")],
)
conn.commit()

ATAK = "olx_1' OR '1'='1"


def program(zapytanie):
    """Pokazuje skompilowany program, ktory baza faktycznie wykona."""
    for krok in conn.execute("EXPLAIN " + zapytanie):
        if krok["opcode"] in ("Ne", "Eq", "String8", "IdxGT", "SeekGE", "ResultRow", "Rewind", "Next", "Column", "Variable", "Integer"):
            print(f"      {krok['opcode']:<10} p1={krok['p1']:<3} p2={krok['p2']:<3} {krok['p4'] or ''}")


print("=" * 70)
print("A. WERSJA ZE SKLEJANIEM - wartosc trafia do parsera SQL")
print("=" * 70)
sklejone = f"SELECT id FROM offers WHERE external_id = '{ATAK}'"
print("  tekst zapytania:")
print("     ", sklejone)
print("  program po kompilacji:")
program(sklejone)
print("  ^ w programie jest porownanie '1'='1', ktore zawsze wychodzi prawda")
print("    napastnik ZMIENIL program, ktory baza wykona\n")

print("=" * 70)
print("B. WERSJA Z ? - wartosci NIE MA w tekscie zapytania")
print("=" * 70)
param = "SELECT id FROM offers WHERE external_id = ?"
print("  tekst zapytania:")
print("     ", param)
print("  program po kompilacji:")
program(param)
print("  ^ opcode 'Variable' to PUSTA SZUFLADKA na wartosc")
print("    program jest juz gotowy, a wartosci jeszcze nikt nie podal\n")

print("=" * 70)
print("C. TEN SAM PROGRAM, ROZNE WARTOSCI")
print("=" * 70)
for wartosc in ["olx_1", ATAK, "cokolwiek'; DROP TABLE offers; --"]:
    wynik = conn.execute(param, (wartosc,)).fetchall()
    print(f"  wartosc w szufladce: {wartosc!r}")
    print(f"    -> baza zwrocila: {[dict(r) for r in wynik]}")
print("  ^ program sie NIE ZMIENIL. Zmienila sie tylko zawartosc szufladki.\n")

print("=" * 70)
print("D. DOWOD: baza traktuje ten atak jak zwyklа nazwe")
print("=" * 70)
conn.execute("INSERT INTO offers (external_id, title) VALUES (?, ?)", (ATAK, "Oferta o dziwnej nazwie"))
conn.commit()
print(f"  dodalem do bazy oferte, ktorej external_id to doslownie {ATAK!r}")
wynik = conn.execute(param, (ATAK,)).fetchall()
print(f"  szukam jej przez ?  -> {[dict(r) for r in wynik]}")
print("  ^ znalazl DOKLADNIE JEDEN wiersz - ten o takiej nazwie.")
print("    Dla bazy to zwykly ciag znakow, jak 'Kawalerka'. Zaden rozkaz.")

EURUSD = 1.1464
FTR_USD = 2.0
# ticker: (EUR millions or None, USD millions override, source, club override, league override)
TM = 'Transfermarkt, as reported Jul–Sep 2026'
SD = 'Soccerdonna (Transfermarkt), latest published'
EST = 'Fantrade estimate: coaches have no transfer-market value'
VALS = {
 'FSAKA': (110, None, TM), 'FHLND': (220, None, TM), 'FKM7': (200, None, TM), 'FVJR': (140, None, TM),
 'FBEL': (160, None, TM), 'FPLMR': (100, None, TM), 'FYAML': (220, None, TM), 'FMUS': (100, None, TM),
 'FWRTZ': (100, None, TM), 'FRODR': (50, None, TM), 'FFODN': (80, None, TM), 'FPEDR': (150, None, TM),
 'FSALI': (100, None, TM), 'FBRN': (35, None, TM), 'FJACK': (40, None, TM),
 'FCR7': (10, None, TM), 'FLM10': (15, None, TM), 'FKANE': (60, None, TM), 'FRICE': (120, None, TM),
 'FVVD': (28, None, TM), 'FOSIM': (75, None, TM), 'FSALH': (22, None, TM), 'FLOOK': (40, None, TM), 'FCHUK': (20, None, TM),
 'FAITN': (1.6, None, SD), 'FPUTL': (1.2, None, SD), 'FRUSS': (1.3, None, SD), 'FLJMS': (0.7, None, SD),
 'FKERR': (0.5, None, SD), 'FWILM': (0.75, None, SD), 'FEARP': (0.12, None, SD), 'FSHAW': (0.725, None, SD),
 'FPAJR': (0.4, None, SD), 'FRODM': (0.35, None, SD), 'FKELY': (0.9, None, SD), 'FAJBD': (0.425, None, SD), 'FALOZ': (0.08, None, SD),
 'FARTA': (None, 22.05, EST), 'FPEP': (None, 29.6, EST), 'FMARS': (None, 18.3, EST), 'FWIEG': (None, 26.8, EST),
}
CLUBS = {'FWRTZ': ('Liverpool', 'Premier League'), 'FRODR': ('Barcelona', 'La Liga'), 'FJACK': ('Aston Villa', 'Premier League')}
def usd(t):
    e, u, _ = VALS[t]
    return round((u if u is not None else e * EURUSD) * 1e6, 2)
def share_usd(t): return usd(t) / 1e7
def share_ftr(t): return share_usd(t) / FTR_USD
if __name__ == '__main__':
    for t in VALS: print(t, f"${usd(t):,.0f}", f"${share_usd(t):.4f}", f"{share_ftr(t):.6f} FTR", f"5%={500000*share_ftr(t):,.0f} FTR")

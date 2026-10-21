import re, unicodedata

SUFFIX = re.compile(r"\s+(jr|sr|ii|iii|iv|v)\.?$", re.I)

def norm(n):
    # Canonical player key.
    # stats_week.csv and snap_counts.csv disagree about Jr./Sr. suffixes
    # in BOTH directions; Yahoo disagrees with both. Join on norm(name),
    # never on the raw string. A missed join silently reads as 0.0.
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    n = n.replace(".", "").replace("'", "").replace("-", " ")
    n = SUFFIX.sub("", n.strip())
    return " ".join(n.lower().split())

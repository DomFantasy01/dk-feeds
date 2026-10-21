"""Free-agent sweep, Fri Sep 25 2026, ~9:20 PM PT.  Yahoo 'Remaining Games (proj)',
each league's own scoring, every free agent and waiver man at QB RB WR TE K DEF
(top 50-125 per position by Yahoo's rest-of-season rank), against Dom's weakest
STARTER at the same position (flex and superflex starters count at their own position).
Gate: +2.0 points a game over that man.  Result: nobody clears, in any league.
Rows below are the three closest per league.  Values are points per game, one decimal."""
READ = "Fri Sep 25, 9:20 PM PT"
GATE = 2.0
# league: (weakest-by-position note, [(player, pos, team, status, his_ppg, your_man, your_ppg, rostered_pct, injury)])
SWEEP = {
    "DK I": [("Spencer Shrader", "K", "IND", "FA", 7.8, "Chris Boswell", 7.0, 14, ""),
             ("Harrison Mevis", "K", "LA", "FA", 7.8, "Chris Boswell", 7.0, 49, ""),
             ("Trey Smack", "K", "GB", "WAIVERS SEP 30", 7.5, "Chris Boswell", 7.0, 25, "")],
    "DK II": [("Eagles", "DEF", "PHI", "WAIVERS SEP 26", 6.6, "49ers", 5.9, 90, ""),
              ("Packers", "DEF", "GB", "WAIVERS SEP 30", 6.2, "49ers", 5.9, 33, ""),
              ("Bills", "DEF", "BUF", "FA", 6.1, "49ers", 5.9, 22, "")],
    "DK III": [("Caleb Douglas", "WR", "MIA", "WAIVERS SEP 26", 7.8, "Devaughn Vele", 6.4, 24, "Out"),
               ("Tre' Harris", "WR", "LAC", "FA", 6.7, "Devaughn Vele", 6.4, 4, ""),
               ("Jauan Jennings", "WR", "MIN", "FA", 6.5, "Devaughn Vele", 6.4, 5, "")],
    "DK IV": [("Wan'Dale Robinson", "WR", "TEN", "FA", 9.8, "Romeo Doubs", 9.0, 48, ""),
              ("Jakobi Meyers", "WR", "JAX", "FA", 9.5, "Romeo Doubs", 9.0, 44, ""),
              ("Spencer Shrader", "K", "IND", "FA", 8.7, "Tyler Loop", 8.3, 14, "")],
}
NOTE = {
    "DK I": "Closest men are all kickers, under a point a game better than Boswell.",
    "DK II": "Closest men are all defenses, under a point better than the 49ers.",
    "DK III": "Vele, 6.4 a game, is your weakest starter in any league. Douglas is out, and your standing rule is no claim on him.",
    "DK IV": "Seattle defense checked Sat: 7.4 a game. Best free defense, Denver, is 7.5 \u2014 0.1 better, nowhere near the gate.",
}

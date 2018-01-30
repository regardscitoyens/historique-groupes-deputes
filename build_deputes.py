#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, json
from pprint import pprint
from datetime import date, datetime, timedelta

leg = int(sys.argv[1])
assert leg in [13,14]

leg_start = "%d-06-20" % (int(leg)*5 + 1942)
leg_end = ("%d-06-%s" % (int(leg)*5 + 1947, 19 if leg == 13 else 20)).decode("utf-8")

def parse_date(dat):
    if not dat:
        return leg_end
    d = dat.split("/")
    return "-".join([d[2], d[1], d[0]])

def substract_day(dat, days=1):
    dat = datetime.strptime(dat, "%Y-%m-%d").date()
    d = dat - timedelta(days=days)
    return d.isoformat()

def parse_ancien_mandat(mandat):
    m = mandat.split(" / ")
    return {
      "debut": parse_date(m[0]),
      "fin": parse_date(m[1])
    }

deputes = {}
with open(os.path.join("data", "deputes-leg%s.json" % leg)) as f:
    for depute in json.load(f)["deputes"]:
        dep = depute["depute"]
        if not dep["mandat_fin"]:
            dep["mandat_fin"] = leg_end
        anciens = [
          parse_ancien_mandat(a["mandat"])
          for a in dep["anciens_mandats"]
        ]
        dep["anciens_mandats"] = sorted([
          a for a in anciens
          if a["debut"] >= leg_start
        ], key=lambda x: x["debut"])
        if not len(dep["anciens_mandats"]):
            dep["anciens_mandats"] = [{
             "debut": dep["mandat_debut"],
             "fin": dep["mandat_fin"]
            }]
        deputes["OMC_PA%s" % dep["id_an"]] = dep

siglize = {
  "Gauche démocrate et républicaine": "GDR",
  "écologiste": "ECOLO",
  "Socialiste, radical, citoyen et divers gauche": "SRC",
  "socialiste, républicain et citoyen": "SRC",
  "Socialiste, écologiste et républicain": "SER",
  "radical, républicain, démocrate et progressiste": "RRDP",
  "Nouveau Centre": "NC",
  "Union des démocrates et indépendants": "UDI",
  "Union pour un Mouvement Populaire": "UMP",
  "Rassemblement - Union pour un Mouvement Populaire": "RUMP",
  "Les Républicains": "LR",
  "Députés n'appartenant à aucun groupe": "NI",
  "députés non inscrits": "NI"
}

max_date = {
  "écologiste": "2016-05-19",
  "socialiste, républicain et citoyen": "2016-05-24",
  "Rassemblement - Union pour un Mouvement Populaire": "2013-01-15",
  "Union pour un Mouvement Populaire": "2015-06-01"
}

with open(os.path.join("data", "historique-groupes-leg%s.csv" % leg)) as f:
    curdat = None
    curgpe = None
    curdep = None
    groupe = None
    depute = None
    oldgpe = None
    olddat = None
    results = []
    for r in csv.reader(f, delimiter=";"):
        dep = r[0]
        dat = r[1]
        gpe = siglize[r[2]]
        if r[2] in max_date and dat > max_date[r[2]]:
            continue
        if dep != curdep:
            if depute:
                groupe["fin"] = depute["mandat_fin"]
                depute["groupes_historique"].append(groupe)
                results.append(depute)
            try:
                depute = deputes[dep]
            except KeyError:
                depute = None
                continue
            depute["groupes_historique"] = []
            if dat > depute["anciens_mandats"][0]["debut"]:
                depute["groupes_historique"].append({
                  "sigle": "NI",
                  "debut": depute["anciens_mandats"][0]["debut"],
                  "fin": substract_day(dat)
                })
            oldgpe = None
            groupe = None
            curgpe = None
            curdat = None
            olddat = None
            curdep = dep
        if not any(dat >= a["debut"] and dat <= a["fin"] for a in depute["anciens_mandats"]):
            continue
        if gpe != curgpe:
            if dat == curdat and gpe == oldgpe and olddat == substract_day(dat):
                continue
            if groupe:
                groupe["fin"] = min(curdat, substract_day(dat))
                oldgpe = curgpe if curdat == substract_day(dat) else None
                depute["groupes_historique"].append(groupe)
            curgpe = gpe
            groupe = {
              "sigle": gpe,
              "debut": dat
            }
        else:
            oldgpe = None
        if dat != curdat:
            olddat = curdat
            curdat = dat
    groupe["fin"] = depute["mandat_fin"]
    depute["groupes_historique"].append(groupe)
    results.append(depute)
    with open(os.path.join("data", "deputes-historique-leg%s.json" % leg), "w") as f:
        print >> f, json.dumps(results, indent=2, ensure_ascii=False).encode("utf-8")

    # TEST results
    for d in results:
        if not d["anciens_mandats"]:
            print "WARNING, no mandats for", d["nom"]
        if d["anciens_mandats"][-1]["debut"] != d["mandat_debut"]:
            print "WARNING, first date last mandat for", d["nom"], d["anciens_mandats"][-1]["debut"], d["mandat_debut"]
        if d["anciens_mandats"][-1]["fin"] != d["mandat_fin"]:
            print "WARNING, last date last mandat for", d["nom"], d["anciens_mandats"][-1]["fin"], d["mandat_fin"]
        if not d["groupes_historique"]:
            print "WARNING, no historique for", d["nom"]
        if d["groupes_historique"][0]["debut"] != d["anciens_mandats"][0]["debut"]:
            print "WARNING, first date for", d["nom"], d["groupes_historique"][0]["debut"], d["anciens_mandats"][0]["debut"]
        if d["groupes_historique"][-1]["fin"] != d["mandat_fin"]:
            print "WARNING, last date for", d["nom"], d["groupes_historique"][-1]["fin"], d["mandat_fin"]


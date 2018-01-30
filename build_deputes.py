#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, json
from pprint import pprint
from datetime import date, datetime, timedelta


leg = int(sys.argv[1])
assert leg in [13,14]

leg_start = "%d-06-20" % (leg * 5 + 1942)
leg_end = ("%d-06-%s" % (leg * 5 + 1947, leg + 6)).decode("utf-8")


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


# READ PARLS
deputes = {}
slugs = {}
with open(os.path.join("data", "deputes-leg%s.json" % leg)) as jsonf:
    for depute in json.load(jsonf)["deputes"]:
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
        slugs[dep["slug"]] = dep

with open(os.path.join("data", "senateurs.json")) as jsonf:
    for senateur in json.load(jsonf)["senateurs"]:
        sen = senateur["senateur"]
        senid = sen["url_institution"].replace("http://www.senat.fr/", "")
        if sen["slug"] in slugs:
            deputes[senid] = slugs[sen["slug"]]


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


# BUILD DATA
with open(os.path.join("data", "historique-groupes-leg%s.csv" % leg)) as csvf:
    curdat = None
    curgpe = None
    curdep = None
    groupe = None
    depute = None
    oldgpe = None
    olddat = None
    results = []
    for r in csv.reader(csvf, delimiter=";"):
        dep = r[0]
        dat = r[1]
        gpe = siglize[r[2]]
        if r[2] in max_date and dat > max_date[r[2]]:
            continue
        if dep != curdep:
            if depute:
                groupe["fin"] = max(curdat, max([a["fin"] for a in depute["anciens_mandats"] if not curdat < a["debut"] and not curdat > a["fin"]]))
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
                  "fin": min(depute["anciens_mandats"][0]["fin"], substract_day(dat))
                })
            oldgpe = None
            groupe = None
            curgpe = None
            curdat = None
            olddat = None
            curdep = dep
        if not any(dat >= a["debut"] and dat <= a["fin"] for a in depute["anciens_mandats"]):
            continue
        if gpe != curgpe or curdat != substract_day(dat):
            if dat == curdat and gpe == oldgpe and olddat == substract_day(dat):
                continue
            if groupe:
                groupe["fin"] = min(curdat, substract_day(dat))
                if not groupe["fin"] < groupe["debut"]:
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
    groupe["fin"] = max(curdat, max([a["fin"] for a in depute["anciens_mandats"] if not curdat > a["fin"]]))
    depute["groupes_historique"].append(groupe)
    results.append(depute)
    with open(os.path.join("data", "deputes-historique-leg%s.json" % leg), "w") as jsonf:
        print >> jsonf, json.dumps(results, indent=2, ensure_ascii=False).encode("utf-8")


# CHECK RESULTS
for d in results:
    am = d["anciens_mandats"]

    if not am:
        print "WARNING, no mandats for", d["nom"]
    if am[-1]["debut"] != d["mandat_debut"]:
        print "WARNING, first date last mandat for", d["nom"], am[-1]["debut"], d["mandat_debut"]
    if am[-1]["fin"] != d["mandat_fin"]:
        print "WARNING, last date last mandat for", d["nom"], am[-1]["fin"], d["mandat_fin"]
    if not d["groupes_historique"]:
        print "WARNING, no historique for", d["nom"]
    if d["groupes_historique"][0]["debut"] != am[0]["debut"]:
        print "WARNING, first date for", d["nom"], d["groupes_historique"][0]["debut"], am[0]["debut"]
    if d["groupes_historique"][-1]["fin"] != am[-1]["fin"]:
        print "WARNING, last date for", d["nom"], d["groupes_historique"][-1]["fin"], am[-1]["fin"]

    a = 0
    dat = ""
    for h in d["groupes_historique"]:
        if h["debut"] < am[a]["debut"]:
            print "WARNING, groupe before mandat for", d["nom"], h, am[a]
        if h["fin"] > am[a]["fin"]:
            print "WARNING, groupe after mandat for", d["nom"], h, am[a]
        elif h["fin"] == am[a]["fin"]:
            a += 1

        if h["debut"] > h["fin"]:
            print "WARNING, negative dates for", d["nom"], d["groupes_historique"]
        if not h["debut"] > dat:
            print "WARNING, duplicate period for", d["nom"], dat, h["debut"]
        dat = h["fin"]

    if a != len(am):
        print "WARNING, last mandate not covered for", d["nom"], dat, am[a:]


# WRITE SQL
sql = "UPDATE %s%s SET %s_groupe_acronyme = '%s' WHERE %s_id = %s AND date >= '%s' AND date <= '%s';"
join = " LEFT JOIN %s o ON o.id = %s_id"
for table in [
  "amendement",
  "parlementaire_amendement",
  "parlementaire_texteloi",
  "presence",
  "intervention",
  "question_ecrite",
]:
    ref_field = "parlementaire"
    lj = ""
    extra = None
    if table.startswith("parlementaire_"):
        tbl = table.replace("parlementaire_", "")
        lj = join % (tbl, tbl)
    elif table == "amendement":
        ref_field = "auteur"
        if leg == 13:
            lj = " LEFT JOIN parlementaire_amendement o ON o.amendement_id = id"
            extra = "o.numero_signataire = 1 AND o.parlementaire"

    with open(os.path.join("sql", "update-%s-leg%s.sql" % (table, leg)), "w") as sqlf:
        for d in results:
            for h in d["groupes_historique"]:
                print >> sqlf, sql % (table, lj, ref_field, h["sigle"], extra or ref_field, d["id"], h["debut"], h["fin"])


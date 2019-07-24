#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO
# - gérer les rattachements

import os, sys, json
from datetime import date
from zipfile import ZipFile
import requests
from build_deputes import add_day, substract_day, load_deputes, read_opendata_an

CACHE_DIR = ".cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def save_local_groupes(leg=15):
    try:
        data = requests.get("https://www.nosdeputes.fr/organismes/groupe/json").json()["organismes"]
        with open(os.path.join("data", "groupes-leg%s.json" % leg), "w") as jsonf:
            json.dump([o["organisme"] for o in data], jsonf)
    except Exception as e:
        print >> sys.stderr, "ERROR: impossible to read ND's API json data at https://www.nosdeputes.fr/organismes/groupe/json"
        print >> sys.stderr, "%s: %s" % (type(e), e)
        sys.exit(1)

def build_data_legi(leg=15):
    deputes, _ = load_deputes()
    try:
        zipfile = os.path.join(CACHE_DIR, "AN-OpenData-AMO30.json.zip")
        with open(zipfile, "wb") as out:
            r = requests.get("http://data.assemblee-nationale.fr/static/openData/repository/15/amo/tous_acteurs_mandats_organes_xi_legislature/AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip", stream=True)
            for block in r.iter_content(1024):
                out.write(block)
        if leg >= 15:
            data = {
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "acteurs": {
                    "acteur": []
                },
                "organes": {
                    "organe": []
                }
            }
        with ZipFile(zipfile, "r") as z:
            for f in [f for f in z.namelist() if f.endswith(".json")]:
                with z.open(f) as zf:
                    datum = json.load(zf)
                    if leg >= 15:
                        if '/organe/' in f:
                            data["organes"]["organe"].append(datum["organe"])
                        elif '/acteur/' in f:
                            data["acteurs"]["acteur"].append(datum["acteur"])
                    else:
                        data = datum["export"]
    except Exception as e:
        print >> sys.stderr, "ERROR: impossible to read AN's OpenData json at http://data.assemblee-nationale.fr/static/openData/repository/15/amo/tous_acteurs_mandats_organes_xi_legislature/AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip"
        print >> sys.stderr, "%s: %s" % (type(e), e)
        sys.exit(1)
    historique = read_opendata_an(data, leg, deputes)
    return historique

def get_dep_groupe_at(dep, date):
    for g in dep["groupes_historique"]:
        if g["debut"] <= date <= (g["fin"] or "9999-99-99"):
            return g["sigle"]
    return ""

def write_csv(data, leg=15):
    deputes = {p["slug"]: p for p in data}
    slugs = sorted(deputes.keys())
    min_date = "%d-06-%s" % (leg * 5 + 1942, (21 if leg == 15 else 20))
    end_legi = "%d-06-%s" % (leg * 5 + 1947, (19 if leg == 13 else 20))
    max_date = min(date.today().isoformat(), end_legi)
    csvfile = os.path.join("data", "deputes-groupes-jours-%s.csv" % leg)
    with open(csvfile, "w") as f:
        headers = ["date_debut", "date_fin", "total"] + slugs
        print >> f, ",".join(headers)
        curr_gpes = None
        dat = d0 = min_date
        while dat <= max_date:
            gpes = [get_dep_groupe_at(deputes[d], dat) for d in slugs]
            if curr_gpes != gpes:
                if curr_gpes != None:
                    #print [d0, substract_day(dat)]
                    #for i, d in enumerate(slugs):
                    #    if curr_gpes[i] != gpes[i]:
                    #        print "-> %s from %s to %s" % (d, curr_gpes[i], gpes[i])
                    print >> f, ",".join([d0, substract_day(dat), total] + curr_gpes)
                curr_gpes = gpes
                total = str(len([1 for p in curr_gpes if p]))
                d0 = dat
            dat = add_day(dat)
        #print [d0, max_date]
        print >> f, ",".join([d0, max_date, total] + curr_gpes)


if __name__ == "__main__":
    write_csv(build_data_legi())
    save_local_groupes()

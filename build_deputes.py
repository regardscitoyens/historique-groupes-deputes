#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, json
from pprint import pprint

leg = int(sys.argv[1])
assert leg in [13,14]

leg_start = "%d-06-20" % (int(leg)*5 + 1942)
leg_end = ("%d-06-20" % (int(leg)*5 + 1947)).decode("utf-8")

def parse_date(dat):
    if not dat:
        return leg_end
    d = dat.split("/")
    return "-".join([d[2], d[1], d[0]])

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
        deputes["OMC_PA%s" % dep["id_an"]] = dep


with open(os.path.join("data", "historique-groupes-leg%s.csv" % leg)) as f:
    pass
    #belongs = csv..load(f)


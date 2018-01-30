#!/bin/bash

cd $(dirname $0)
mkdir -p .cache data

function escapeit { perl -e 'use URI::Escape; print uri_escape shift();print"\n"' "$1" | sed 's/\s/_/g'; }
function download {
  cache=.cache"/"$(escapeit $1)
  if ! test -s $cache ; then
    if curl -sLI $1 | grep " 404" > /dev/null; then
      touch $cache.tmp
    else
      curl -sL $1 > $cache.tmp
    fi
    mv $cache.tmp $cache
  fi
  cat $cache
}

if ! test -s data/opendata_an.json; then
  download "http://data.assemblee-nationale.fr/static/openData/repository/AMO/tous_acteurs_mandats_organes_xi_legislature/AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip" > data/opendata_an.json.zip
  unzip data/opendata_an.json.zip
  mv AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json data/opendata_an.json
  rm -f data/opendata_an.json.zip
fi

function scrap_legi {
  leg=$1
  yr=$((1942 + $leg*5))
  echo
  echo "LEGI $leg:"
  echo "--------"
  rm -f .cache/historique-groupes-leg$leg.csv
   python -m json.tool data/opendata_an.json |
   grep '^                    "@xsi:type": "GroupePolitique_type",' -A 20 |
   grep "legislature.*$leg" -A 20 |
   grep "PO" |
   sed "s/[^0-9]//g" |
   while read organe; do
    url="http://www.assemblee-nationale.fr/qui/xml/organe.asp?id_organe=/$leg/tribun/xml/xml/organes/$organe.xml"
    curl -sLI $url |
     grep '^Location:' |
     sed 's/\r//g' |
     sed 's/^Location: //' |
     sed 's|/fiche/|/tableau/|' |
     while read gpeurl; do
      for i in `seq 0 1826`; do
        dat=$(date -d "$yr-06-20 $i days" +%Y-%m-%d)
        gpe=$(download "$gpeurl/$dat" |
         grep "Composition" |
         head -n 1 |
         sed 's/^.*Composition\s*//' |
         sed -r 's/^(du|des)\s+//' |
         sed 's/^groupe\s*//' |
         sed -r "s/^de l[a' ]+//" |
         sed -r 's/\s+au\s+[0-9].*$//'
        )
        tot=$(download "$gpeurl/$dat" |
         grep "href=.*deputes/fiche" |
         wc -l
        )
        echo "- $gpe $dat ($tot)"
        download "$gpeurl/$dat" |
         grep "href=.*deputes/fiche" |
         sed -r 's|^.*/(OMC_[^"]+)".*$|\1|' |
         while read depid; do
          echo "$depid;$dat;$gpe;$gpeurl/$dat" >> .cache/historique-groupes-leg$leg.csv
        done
      done
    done
  done
  sort .cache/historique-groupes-leg$leg.csv > data/historique-groupes-leg$leg.csv
  cp data/historique-groupes-leg$leg.csv{,.sv}
  gzip data/historique-groupes-leg$leg.csv
  mv data/historique-groupes-leg$leg.csv{.sv,}
  rm -f .cache/historique-groupes-leg$leg.csv
}

for leg in 13 14; do
  if ! test -s data/historique-groupes-leg$leg.csv; then
    scrap_legi $leg
  fi
  yr=$((1942 + $leg*5))
  download https://$yr.nosdeputes.fr/deputes/json > data/deputes-leg$leg.json
  ./build_deputes.py $leg
done


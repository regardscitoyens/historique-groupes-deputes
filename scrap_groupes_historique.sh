#!/bin/bash

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

for leg in 13 14; do
  rm -f .cache/historique-groupes-leg$leg.csv
  yr=$((1942 + $leg*5))
  echo
  echo "LEGI $leg:"
  echo "--------"
  download "http://www.assemblee-nationale.fr/$leg/qui/modifications.asp" |
   iconv -f "iso8859-15" -t "utf-8" |
   grep "organe" |
   sed -r 's/^.*href="([^"]+)".*$/\1/' |
   sed 's|^/|http://www.assemblee-nationale.fr/|' |
   sort -u |
   while read url; do
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
  cp {.cache,data}/historique-groupes-leg$leg.csv
  gzip data/historique-groupes-leg$leg.csv
  mv {.cache,data}/historique-groupes-leg$leg.csv
done


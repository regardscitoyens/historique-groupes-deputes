# Historique des groupes des députés

## Battlefield:

- [X] scrap list of groups on http://www.assemblee-nationale.fr/13/qui/modifications.asp

- [X] scrap daily list of MPs for each group

- [X] build list of MPs such as:

```json
[{
  "nom": "",
  "id": "",
  "id_an": "",
  "slug": "",
  "mandat_debut": "",
  "mandat_fin": "",
  "anciens_mandats": [{
    "debut": "",
    "fin": ""
  }, ...],
  "groupe_sigle": "",
  "groupes_historique": [{
    "sigle": "",
    "debut": "",
    "fin": ""
  }, ...]
}, ...]
```

- [X] check debuts/fin mandat

- [X] check doubles appartenances à une meme date

- [X] check missing/extra periodes

- [X] fix missing deputes listed as senateurs

- [X] fix still missing deputes (ex P. Roy)

- [X] use AN OpenData instead of all of this mess...

- [X] create missing _groupe_acronyme fields in ND mysql on Amendement/ParlAmendement/Intervention/ParlementaireTexteLoi/Presence/QuestionEcrite

- [X] generate sql commands by MP by period to fill _groupe_acronyme for authored object with date included

- [X] check objects with info not filled
  + [X] 2007-2012
  + [X] 2012-2017

- [X] run sql in prod and check objects again

- [X] use fields in API

- [ ] build data repartition_deputes by day

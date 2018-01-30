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

- [X] create missing _groupe_acronyme fields in ND mysql on Amendement/ParlAmendement/Intervention/ParlementaireTexteLoi/Presence/QuestionEcrite

- [ ] generate sql commands by MP by period to fill _groupe_acronyme for authored object with date included

- [ ] check objects with info not filled

- [ ] generate sql commands to set last groupe to all MPs ?

- [ ] use fields in API

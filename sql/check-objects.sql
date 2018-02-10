# AMENDEMENTS

SELECT * 
FROM  `amendement` 
WHERE  `auteur_groupe_acronyme` IS NULL 
AND  `signataires` !=  'le gouvernement'
ORDER BY texteloi_id, date


# PARL_AMENDEMENTS

SELECT p . * , t.texteloi_id, t.source, t.date, a.nom, a.debut_mandat, a.fin_mandat
FROM  `parlementaire_amendement` p
JOIN amendement t ON t.id = p.amendement_id
JOIN parlementaire a ON a.id = p.parlementaire_id
WHERE  `parlementaire_groupe_acronyme` IS NULL 
ORDER BY t.texteloi_id, t.date, parlementaire_id


# PARL_TEXTELOIS

SELECT p.*, t.id, t.source, t.date, a.nom, a.debut_mandat, a.fin_mandat FROM `parlementaire_texteloi` p
JOIN texteloi t ON t.id = p.texteloi_id
JOIN parlementaire a ON a.id = p.parlementaire_id
WHERE `parlementaire_groupe_acronyme` IS NULL
ORDER BY fonction, parlementaire_id, t.date


# INTERVENTIONS

SELECT  `intervention`.id, source, seance_id,  `intervention`.type, fonction, DATE, p.id, p.nom, p.debut_mandat, p.fin_mandat, intervention
FROM  `intervention` 
JOIN parlementaire p ON p.id = parlementaire_id
WHERE  `parlementaire_id` IS NOT NULL 
AND  `parlementaire_groupe_acronyme` IS NULL 
ORDER BY seance_id, parlementaire_id


# PRESENCES

SELECT * 
FROM  `presence` 
WHERE  `parlementaire_groupe_acronyme` IS NULL 
ORDER BY parlementaire_id, date


# QUESTIONS

SELECT * 
FROM  `question_ecrite` 
WHERE  `parlementaire_groupe_acronyme` IS NULL 
ORDER BY parlementaire_id, date


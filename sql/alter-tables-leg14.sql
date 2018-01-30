ALTER TABLE amendement               ADD auteur_groupe_acronyme        VARCHAR(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL AFTER auteur_id;
ALTER TABLE parlementaire_amendement ADD parlementaire_groupe_acronyme VARCHAR(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL AFTER parlementaire_id;
ALTER TABLE parlementaire_texteloi   ADD parlementaire_groupe_acronyme VARCHAR(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL AFTER parlementaire_id;
ALTER TABLE presence                 ADD parlementaire_groupe_acronyme VARCHAR(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL AFTER parlementaire_id;
ALTER TABLE intervention             ADD parlementaire_groupe_acronyme VARCHAR(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL AFTER parlementaire_id;
ALTER TABLE question_ecrite          ADD parlementaire_groupe_acronyme VARCHAR(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL AFTER parlementaire_id;

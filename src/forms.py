from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo


class InscriptionForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    prenom = StringField('Prénom', validators=[DataRequired()])
    telephone = StringField('Téléphone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    adresse = StringField('Adresse', validators=[DataRequired()])
    publier_articles = BooleanField('Autoriser à publier des articles')
    commenter_articles = BooleanField('Autoriser à commenter des articles')
    login = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    mot_de_passe = PasswordField('Mot de passe', validators=[DataRequired()])
    confirmer_mot_de_passe = PasswordField('Confirmer le mot de passe', validators=[DataRequired(),
                                                                                    EqualTo('mot_de_passe',
                                                                                            message='Les mots de passe doivent correspondre')])

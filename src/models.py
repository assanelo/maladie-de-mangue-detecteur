from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


# Modèle de l'article
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    introduction = db.Column(db.Text, nullable=False)
    manifestation = db.Column(db.Text, nullable=False)
    prevention = db.Column(db.Text, nullable=False)
    cause = db.Column(db.Text, nullable=False)
    audio = db.Column(db.String(100))  # Chemin vers le fichier audio
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    image_article = db.Column(db.String(100))  # Chemin vers l'image de l'article

    # Relation avec l'auteur de l'article (un utilisateur)
    auteur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))
    auteur = db.relationship('Utilisateur', backref='articles')

    # Relation avec les commentaires
    commentaires = db.relationship('Commentaire', backref='article', cascade='all, delete-orphan')


# Modèle du commentaire
class Commentaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenu = db.Column(db.Text, nullable=False)
    date_commentaire = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation avec l'auteur du commentaire (un utilisateur)
    auteur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))
    auteur = db.relationship('Utilisateur', backref='commentaires')

    # Relation avec l'article
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))


# Modèle de l'utilisateur
class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50))
    prenom = db.Column(db.String(50))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    adresse = db.Column(db.String(200))
    publier_articles = db.Column(db.Boolean, default=False)
    commenter_articles = db.Column(db.Boolean, default=True)
    login = db.Column(db.String(50), unique=True)
    mot_de_passe = db.Column(db.String(100))

    def __init__(self, nom, prenom, telephone, email, adresse, publier_articles, commenter_articles, login,
                 mot_de_passe):
        self.nom = nom
        self.prenom = prenom
        self.telephone = telephone
        self.email = email
        self.adresse = adresse
        self.publier_articles = publier_articles
        self.commenter_articles = commenter_articles
        self.login = login
        self.mot_de_passe = generate_password_hash(mot_de_passe)

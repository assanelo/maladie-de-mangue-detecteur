import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from database import db
from script import predict_class
from src.models import Article, Utilisateur

app = Flask(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Définissez la vue de connexion par défaut

UPLOAD_FOLDER = 'upload'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# configuration de la base de donne
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mdapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# needed for session cookies
app.config['SECRET_KEY'] = 'MY_SECRET'
# hashes the password and then stores in the database
app.config['SECURITY_PASSWORD_SALT'] = "MY_SECRET"
# allows new registrations to application
app.config['SECURITY_REGISTERABLE'] = True
# to send automatic registration email to user
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

db.init_app(app)

# runs the app instance
app.app_context().push()

# Settings for migrations
migrate = Migrate(app, db)


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/samples")
def samples():
    return render_template("samples.html")


@app.route("/classify", methods=['POST', 'GET'])
def classify():
    if request.method == "POST":
        print("inside the request")
        file = request.files['input_file']
        file.save("./media/image.jpeg")
        return redirect(url_for("result"))
    return render_template("classify.html")


@app.route("/result")
def result():
    prediction = predict_class("./media/image.jpeg")
    print(prediction)
    return render_template("result.html", prediction=prediction)


# @app.route("/diseases-add/")
# def diseases():
#    return render_template("diseases.html")


# #################### DEBUT DES FONCTION POUR  EFFECTUER DES OPERATIONS SUR LES ARTICLES
# ####################

@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST':
        # Recuperation des donnée du formulaire
        titre = request.form['titre']
        introduction = request.form['introduction']
        manifestation = request.form['manifestation']
        prevention = request.form['prevention']
        cause = request.form['cause']
        audio = request.files['audio']
        image = request.files['image']

        # Vérifier si un fichier d'image a été sélectionné
        if image and image.filename != '':
            # Vérifier si l'extension de l'image est autorisée
            if image.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                # Sécuriser le nom du fichier
                image_filename = secure_filename(image.filename)
                # Enregistrer l'image dans le dossier d'upload
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            else:
                # Gérer le cas où l'extension de l'image n'est pas autorisée
                return 'Extension de fichier d\'image non autorisée'

        # Vérifier si un fichier audio a été sélectionné
        if audio and audio.filename != '':
            # Vérifier si l'extension de l'audio est autorisée
            if audio.filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS:
                # Sécuriser le nom du fichier
                audio_filename = secure_filename(audio.filename)
                # Enregistrer l'audio dans le dossier d'upload
                audio.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))
            else:
                # Gérer le cas où l'extension de l'audio n'est pas autorisée
                return 'Extension de fichier audio non autorisée'

        # Créer un nouvel objet Article avec les données du formulaire
        nouvel_article = Article(titre=titre, introduction=introduction, manifestation=manifestation,
                                 prevention=prevention, cause=cause, image=image_filename, audio=audio_filename)
        db.session.add(nouvel_article)
        db.session.commit()

        # Rediriger vers la page d'accueil ou une autre page de confirmation
        return redirect('/add_article')

    return render_template("add_article.html")


@app.route('/edit_article/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    article = Article.query.get(article_id)

    if request.method == 'POST':
        # Récupérer les données du formulaire
        article.titre = request.form['titre']
        article.introduction = request.form['introduction']
        article.manifestation = request.form['manifestation']
        article.prevention = request.form['prevention']
        article.cause = request.form['cause']

        # Enregistrer les modifications dans la base de données
        db.session.commit()

        # Rediriger vers la page d'accueil ou une autre page de confirmation
        return redirect('/')

    # Si la méthode de la requête est GET, afficher le formulaire de mise à jour
    return render_template('article/edit_article.html', article=article)


@app.route('/delete_article/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    article = Article.query.get(article_id)

    # Vérifiez si l'article existe
    if article:
        # Supprimez l'article de la base de données
        db.session.delete(article)
        db.session.commit()

        # Redirigez vers la page d'accueil ou une autre page de confirmation
        return redirect('/')
    else:
        # Gérez le cas où l'article n'existe pas
        return 'Article non trouvé'


@app.route('/articles')
def articles():
    articles = Article.query.all()
    return render_template('article/articles.html', articles=articles)


# #################### DEBUT DES FONCTION POUR  EFFECTUER DES OPERATIONS SUR LES ARTICLES
# ####################

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        telephone = request.form['telephone']
        email = request.form['email']
        adresse = request.form['adresse']
        publier_articles = bool(request.form.get('publier_articles'))
        commenter_articles = bool(request.form.get('commenter_articles'))
        login = request.form['login']
        mot_de_passe = request.form['mot_de_passe']

        # Vérifiez si l'utilisateur existe déjà dans la base de données
        utilisateur_existant = Utilisateur.query.filter_by(email=email).first()
        if utilisateur_existant:
            flash('Un compte avec cette adresse e-mail existe déjà.')
            return redirect('/register')

        # Générer le hachage du mot de passe
        mot_de_passe_hash = generate_password_hash(mot_de_passe)

        # Créer un nouvel utilisateur
        nouvel_utilisateur = Utilisateur(nom=nom, prenom=prenom, telephone=telephone, email=email, adresse=adresse, publier_articles=publier_articles, commenter_articles=commenter_articles, login=login, mot_de_passe=mot_de_passe_hash)
        db.session.add(nouvel_utilisateur)
        db.session.commit()

        flash('Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.')
        return redirect('/login')

    return render_template('utilisateur/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        mot_de_passe = request.form['mot_de_passe']

        # Vérifiez les informations d'identification de l'utilisateur
        utilisateur = Utilisateur.query.filter_by(login=login).first()
        if utilisateur and check_password_hash(utilisateur.mot_de_passe, mot_de_passe):
            # Authentification réussie
            login_user(utilisateur)
            flash('Vous êtes maintenant connecté.')
            return redirect('/')

        # En cas d'échec de l'authentification
        flash('Nom d\'utilisateur ou mot de passe incorrect.')

    return render_template('login.html')


@login_manager.user_loader
def load_user(user_id):
    # Fonction pour charger l'utilisateur depuis la base de données ou autre source
    return Utilisateur.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirigez l'utilisateur connecté vers la page d'accueil ou une autre page appropriée
        return redirect('/')

    if request.method == 'POST':
        login = request.form['login']
        mot_de_passe = request.form['mot_de_passe']

        # Recherchez l'utilisateur dans la base de données
        utilisateur = Utilisateur.query.filter_by(login=login).first()

        if utilisateur and check_password_hash(utilisateur.mot_de_passe, mot_de_passe):
            # Connectez l'utilisateur
            login_user(utilisateur)
            return redirect('/')
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.')

    return render_template('login.html')


@app.route('/logout')
@login_required  # Assurez-vous que l'utilisateur est connecté
def logout():
    logout_user()
    return redirect('/login')


if __name__ == "__main__":
    app.run(port=8000, debug=True)

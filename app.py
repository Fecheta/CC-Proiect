import random
import uuid

from flask import Flask, render_template, request, redirect, session, url_for
import msal
import app_config
from werkzeug.middleware.proxy_fix import ProxyFix
# from auth.utils import _save_cache, _build_msal_app, _build_auth_code_flow, _get_token_from_cache, _load_cache
from flask_session import Session
import requests

from FormRecognizer import FormRecognizer
from cosmosDB.database import DBConnection
from database.query import Query
from speech.text_to_speech import TextToSpeech
from storage import Storage
from computer_vision import ComputerVision
from TextAnalytics import TextAnalytics
from translate.translate import Translate
from speech import text_to_speech

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"
app.config.from_object(app_config)
Session(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.route("/")
def index():
    logged = False
    if session.get("user"):
        logged = True
    if logged:
        user = session['user']
        db = DBConnection('Users')
        result = db.select_user_by_email(user.get('preferred_username'))
        if len(result) == 0:
            db.insert_user(str(random.randint(100, 10000)), user.get('preferred_username'), user.get('name'), '1234')
    else:
        user = None
    # print(logged)
    return render_template('index.html', logged=logged, user=user)


@app.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    logged = False
    if session.get('user'):
        logged = True
    return redirect(session["flow"]["auth_uri"])
    # return render_template("index.html", auth_url=session["flow"]["auth_uri"], loggedin=logged, user=session["user"])


@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))


@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
    ).json()
    return render_template('display.html', result=graph_data)


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)


def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result


# @app.route('/')
# def start_page():
#     return render_template('index.html')


# @app.route('/login')
# def text_analytics():
#     session["flow"] = _build_auth_code_flow(scopes=auth.app_config.SCOPE)
#     return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)


# @app.route('/textAnalytics')
# def text_analytics():
#     return render_template('textAnalytics.html')


@app.route('/textAnalytics/result', methods=['POST', 'GET'])
def text_analytics_results():
    output = request.form.to_dict()
    description = output["description"]
    print(description)
    results = TextAnalytics.reviews(description)
    print(results)
    return render_template('textAnalytics.html', description=results)


@app.route('/formRecognizer')
def form_recognizer():
    return render_template('form.html')


@app.route('/formRecognizer/result', methods=['POST', 'GET'])
def form_recognizer_results():
    output = request.form.to_dict()
    description = output["description"]
    print(description)
    results = FormRecognizer.get_information(description)
    print(results)
    return render_template('form.html', description=results)


@app.route('/<int:count>')
def second_page(count):
    return render_template('ana.html', no=range(count))


@app.route("/view-photos")
def view_photos():
    storage = Storage.storage('images')

    return render_template('photos.html', urls=storage.get_images())


@app.route("/upload-photos", methods=['GET', 'POST'])
def upload_photos():
    if request.method == 'POST':
        storage = Storage.storage('images')

        for file in request.files.getlist('photos'):
            try:
                storage.container_client.upload_blob(file.filename,
                                                     file)
            except Exception as e:
                print('File already exist')

        return redirect('/view-photos')

    elif request.method == 'GET':
        return render_template('upload.html')


@app.route('/Hand-To-Text', methods=['GET', 'POST'])
def hand_to_text():
    if not session.get('user'):
        return redirect(url_for('login'))
    else:
        user = session['user']

    if request.method == 'GET':
        return render_template('image_form.html')

    if request.method == 'POST':
        computer_vision = ComputerVision()

        method = request.form['source']
        language = request.form['lang']
        # print("Method: " + str(method))

        if method == 'file':
            file_to_analyze = request.files.getlist('photos-files')[0]
            # print(file_to_analyze.filename)

            texts, url = computer_vision.identify_text_from_local_file_str(file_to_analyze, language)

            db = DBConnection("Documents")
            db.insert_document(
                uuid.uuid4(),
                user.get('preferred_username'),
                url,
                None,
                'English',
                'handwritten'
            )

            return render_template('image_text.html', image=url, texts=texts)

        if method == 'url':
            photo_url = request.form['photo-url']
            # print(file_to_analyze.filename)
            print(photo_url)

            texts, url = computer_vision.identify_text_from_url(photo_url, language)

            db = DBConnection("Documents")
            db.insert_document(
                uuid.uuid4(),
                user.get('preferred_username'),
                url,
                None,
                'English',
                'handwritten'
            )

            return render_template('image_text.html', image=url, texts=texts)

        if method == 'test':
            file = request.files.getlist('photos-files')[0]
            # print(file_to_analyze.filename)
            print(file)

            storage = Storage('images-analyzed')
            storage.upload_file(file)
            url = storage.get_image_by_name(file.filename)

            return render_template('image_text.html', image=url, texts=['pdf'])

        return "NU e ok ce e aici"


@app.route('/translate', methods=['GET', 'POST'])
def translate():
    if request.method == "GET":
        return render_template('translate.html')
    if request.method == "POST":
        text = request.form["text"]
        to_language = request.form["select"]
        translation = Translate()
        result = translation.translate(text, toLanguage=to_language)
        return render_template('translate.html', result=result)
    return render_template('translate.html')


@app.route('/texttospeech', methods=("GET", "POST"))
def text_to_speech_page():
    if request.method == "GET":
        return render_template('speech.html')
    if request.method == "POST":
        text = request.form["text"]
        textts = TextToSpeech()
        textts.tts(text)
        return redirect('/tts_result')
    return render_template('speech.html')


@app.route('/tts_result', methods=["GET"])
def get_speech():
    if request.method == "GET":
        return render_template('speech_result.html')
    return render_template('speech_result.html')


@app.route('/search')
def search_page():
    return render_template('search.html')


@app.route('/db')
def db():
    db = DBConnection("Documents")  # connect to Users / Documents database with this param
    result = db.select_all()
    # db.insert_user('22', 'virgilfecheta@gmail.com', 'virgil', '11111')
    return render_template('db.html', result=result)


app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

from flask import Flask, render_template, request, redirect

from FormRecognizer import FormRecognizer
from database.query import Query
from storage import Storage
from computer_vision import ComputerVision
from TextAnalytics import TextAnalytics
from translate.translate import Translate
from speech import text_to_speech


app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"


@app.route('/')
def start_page():
    return render_template('index.html')


@app.route('/textAnalytics')
def text_analytics():
    return render_template('textAnalytics.html')


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
    if request.method == 'GET':
        return render_template('image_form.html')

    if request.method == 'POST':
        computer_vision = ComputerVision()

        method = request.form['source']
        # print("Method: " + str(method))

        if method == 'file':
            file_to_analyze = request.files.getlist('photos-files')[0]
            print(file_to_analyze.filename)

            texts = computer_vision.identify_text_from_local_file_str(file_to_analyze)

            return render_template('image_text.html', image=file_to_analyze, texts=texts)

        if method == 'url':
            photo_url = request.form['photo-url']
            # print(file_to_analyze.filename)
            print(photo_url)

            texts = computer_vision.identify_text_from_url(photo_url)

            return render_template('image_text.html', image=photo_url, texts=texts)

        return "NU e ok ce e aici"


@app.route('/translate/<value>')
def translate(value):
    trs = Translate()
    response = trs.translate(value)
    print(response[0])
    return render_template('translate.html', result=response[0])


@app.route('/texttospeech',methods=("GET", "POST"))
def text_to_speech_page():
    form = text_to_speech.Widgets()
    if request.method == "GET":
        return render_template('speech.html', form=form)
    if request.method == "POST":
        text = request.form["text"]
        text_to_speech.text_to_speach(text)
        return render_template('speech.html', form=form)
    return render_template('speech.html', form=form)


@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/db')
def db():
    query = Query()
    result = query.return_all()
    return render_template('db.html', result=result)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

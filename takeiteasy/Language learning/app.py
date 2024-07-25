from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from gtts import gTTS
import random
import tempfile

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///language_learning.db'
db = SQLAlchemy(app)


# Models
class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    word = db.Column(db.String(100), nullable=False)
    translation = db.Column(db.String(100), nullable=False)
    pronunciation = db.Column(db.String(100), nullable=False)
    language = db.relationship('Language', backref=db.backref('words', lazy=True))


# Sample data initialization
def init_sample_data():
    # Check if data already exists
    if Language.query.first() is not None:
        return

    # Add sample languages
    languages = ['Spanish', 'French', 'German']
    for lang in languages:
        language = Language(name=lang)
        db.session.add(language)

    db.session.commit()

    # Add detailed lessons and words for each language
    for language in Language.query.all():
        if language.name == 'Spanish':
            lessons = [
                {
                    'title': 'Basic Greetings in Spanish',
                    'content': '''
                    <h2>Common Spanish Greetings</h2>
                    <ul>
                        <li><strong>Hola</strong> - Hello</li>
                        <li><strong>Buenos días</strong> - Good morning</li>
                        <li><strong>Buenas tardes</strong> - Good afternoon</li>
                        <li><strong>Buenas noches</strong> - Good evening/night</li>
                        <li><strong>Adiós</strong> - Goodbye</li>
                        <li><strong>Hasta luego</strong> - See you later</li>
                    </ul>
                    <h3>Example Conversation:</h3>
                    <p>
                    Person A: Hola, ¿cómo estás? (Hello, how are you?)<br>
                    Person B: Bien, gracias. ¿Y tú? (Good, thank you. And you?)<br>
                    Person A: Muy bien, gracias. (Very well, thank you.)
                    </p>
                    '''
                },
                {
                    'title': 'Numbers in Spanish (1-10)',
                    'content': '''
                    <h2>Numbers 1-10 in Spanish</h2>
                    <ol>
                        <li><strong>Uno</strong> - One</li>
                        <li><strong>Dos</strong> - Two</li>
                        <li><strong>Tres</strong> - Three</li>
                        <li><strong>Cuatro</strong> - Four</li>
                        <li><strong>Cinco</strong> - Five</li>
                        <li><strong>Seis</strong> - Six</li>
                        <li><strong>Siete</strong> - Seven</li>
                        <li><strong>Ocho</strong> - Eight</li>
                        <li><strong>Nueve</strong> - Nine</li>
                        <li><strong>Diez</strong> - Ten</li>
                    </ol>
                    <h3>Practice:</h3>
                    <p>Try counting from 1 to 10 in Spanish: Uno, dos, tres, cuatro, cinco, seis, siete, ocho, nueve, diez.</p>
                    '''
                }
            ]
            words = [
                ('hola', 'hello', 'oh-la'),
                ('adiós', 'goodbye', 'ah-dee-os'),
                ('gracias', 'thank you', 'grah-see-as'),
                ('por favor', 'please', 'por fah-vor'),
                ('uno', 'one', 'oo-no'),
                ('dos', 'two', 'dos')
            ]
        elif language.name == 'French':
            lessons = [
                {
                    'title': 'Basic Greetings in French',
                    'content': '''
                    <h2>Common French Greetings</h2>
                    <ul>
                        <li><strong>Bonjour</strong> - Hello/Good day</li>
                        <li><strong>Salut</strong> - Hi (informal)</li>
                        <li><strong>Bonsoir</strong> - Good evening</li>
                        <li><strong>Au revoir</strong> - Goodbye</li>
                        <li><strong>À bientôt</strong> - See you soon</li>
                    </ul>
                    <h3>Example Conversation:</h3>
                    <p>
                    Person A: Bonjour, comment allez-vous? (Hello, how are you?)<br>
                    Person B: Très bien, merci. Et vous? (Very well, thank you. And you?)<br>
                    Person A: Ça va bien, merci. (I'm doing well, thank you.)
                    </p>
                    '''
                },
                {
                    'title': 'Numbers in French (1-10)',
                    'content': '''
                    <h2>Numbers 1-10 in French</h2>
                    <ol>
                        <li><strong>Un</strong> - One</li>
                        <li><strong>Deux</strong> - Two</li>
                        <li><strong>Trois</strong> - Three</li>
                        <li><strong>Quatre</strong> - Four</li>
                        <li><strong>Cinq</strong> - Five</li>
                        <li><strong>Six</strong> - Six</li>
                        <li><strong>Sept</strong> - Seven</li>
                        <li><strong>Huit</strong> - Eight</li>
                        <li><strong>Neuf</strong> - Nine</li>
                        <li><strong>Dix</strong> - Ten</li>
                    </ol>
                    <h3>Practice:</h3>
                    <p>Try counting from 1 to 10 in French: Un, deux, trois, quatre, cinq, six, sept, huit, neuf, dix.</p>
                    '''
                }
            ]
            words = [
                ('bonjour', 'hello', 'bon-zhoor'),
                ('au revoir', 'goodbye', 'oh ruh-vwar'),
                ('merci', 'thank you', 'mer-see'),
                ('s\'il vous plaît', 'please', 'seel voo pleh'),
                ('un', 'one', 'un'),
                ('deux', 'two', 'duh')
            ]
        elif language.name == 'German':
            lessons = [
                {
                    'title': 'Basic Greetings in German',
                    'content': '''
                    <h2>Common German Greetings</h2>
                    <ul>
                        <li><strong>Hallo</strong> - Hello</li>
                        <li><strong>Guten Morgen</strong> - Good morning</li>
                        <li><strong>Guten Tag</strong> - Good day</li>
                        <li><strong>Guten Abend</strong> - Good evening</li>
                        <li><strong>Auf Wiedersehen</strong> - Goodbye</li>
                        <li><strong>Tschüss</strong> - Bye (informal)</li>
                    </ul>
                    <h3>Example Conversation:</h3>
                    <p>
                    Person A: Hallo, wie geht es Ihnen? (Hello, how are you?)<br>
                    Person B: Gut, danke. Und Ihnen? (Good, thank you. And you?)<br>
                    Person A: Mir geht es auch gut, danke. (I'm also doing well, thank you.)
                    </p>
                    '''
                },
                {
                    'title': 'Numbers in German (1-10)',
                    'content': '''
                    <h2>Numbers 1-10 in German</h2>
                    <ol>
                        <li><strong>Eins</strong> - One</li>
                        <li><strong>Zwei</strong> - Two</li>
                        <li><strong>Drei</strong> - Three</li>
                        <li><strong>Vier</strong> - Four</li>
                        <li><strong>Fünf</strong> - Five</li>
                        <li><strong>Sechs</strong> - Six</li>
                        <li><strong>Sieben</strong> - Seven</li>
                        <li><strong>Acht</strong> - Eight</li>
                        <li><strong>Neun</strong> - Nine</li>
                        <li><strong>Zehn</strong> - Ten</li>
                    </ol>
                    <h3>Practice:</h3>
                    <p>Try counting from 1 to 10 in German: Eins, zwei, drei, vier, fünf, sechs, sieben, acht, neun, zehn.</p>
                    '''
                }
            ]
            words = [
                ('hallo', 'hello', 'ha-lo'),
                ('auf wiedersehen', 'goodbye', 'owf vee-der-zey-en'),
                ('danke', 'thank you', 'dahn-kuh'),
                ('bitte', 'please', 'bi-tuh'),
                ('eins', 'one', 'eyns'),
                ('zwei', 'two', 'tsvey')

            ]

        # Add lessons
        for lesson_data in lessons:
            lesson = Lesson(language_id=language.id, title=lesson_data['title'], content=lesson_data['content'])
            db.session.add(lesson)

        # Add words
        for word, translation, pronunciation in words:
            new_word = Word(language_id=language.id, word=word, translation=translation, pronunciation=pronunciation)
            db.session.add(new_word)

    db.session.commit()


# Routes
@app.route('/')
def home():
    languages = Language.query.all()
    return render_template('home.html', languages=languages)


@app.route('/language/<int:language_id>')
def language_dashboard(language_id):
    language = Language.query.get_or_404(language_id)
    lessons = Lesson.query.filter_by(language_id=language_id).all()
    return render_template('language_dashboard.html', language=language, lessons=lessons)


@app.route('/lesson/<int:lesson_id>')
def lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    return render_template('lesson.html', lesson=lesson)


@app.route('/quiz/<int:language_id>')
def quiz(language_id):
    words = Word.query.filter_by(language_id=language_id).order_by(db.func.random()).limit(10).all()
    return render_template('quiz.html', words=words)


@app.route('/practice_pronunciation/<int:word_id>')
def practice_pronunciation(word_id):
    word = Word.query.get_or_404(word_id)
    return render_template('pronunciation.html', word=word)


@app.route('/check_pronunciation', methods=['POST'])
def check_pronunciation():
    # This is a mock implementation of voice recognition
    # In a real app, you'd integrate with a voice recognition API
    word_id = request.form.get('word_id')
    user_pronunciation = request.form.get('user_pronunciation')

    word = Word.query.get_or_404(word_id)

    # Simulate voice recognition accuracy
    accuracy = random.uniform(0.7, 1.0)
    is_correct = accuracy > 0.8

    feedback = "Excellent pronunciation!" if is_correct else "Close! Try again."

    return jsonify({
        'is_correct': is_correct,
        'feedback': feedback,
        'correct_pronunciation': word.pronunciation
    })


@app.route('/get_pronunciation/<int:word_id>')
def get_pronunciation(word_id):
    word = Word.query.get_or_404(word_id)

    # Create a temporary file to store the audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_filename = temp_file.name
    temp_file.close()

    # Generate the audio file
    tts = gTTS(text=word.word, lang=word.language.name.lower()[:2])
    tts.save(temp_filename)

    # Send the file
    return send_file(temp_filename, mimetype='audio/mp3', as_attachment=True, download_name=f"{word.word}.mp3")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    app.run(debug=True)
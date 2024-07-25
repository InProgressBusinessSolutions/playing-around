from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storytelling.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tone = db.Column(db.String(50), nullable=False)
    genre = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    stories = Story.query.all()
    return render_template('index.html', stories=stories)

@app.route('/story/<int:story_id>')
def view_story(story_id):
    story = Story.query.get_or_404(story_id)
    return render_template('story.html', story=story)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_story():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tone = request.form['tone']
        genre = request.form['genre']
        new_story = Story(title=title, content=content, tone=tone, genre=genre)
        db.session.add(new_story)
        db.session.commit()
        flash('Your story has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/edit/<int:story_id>', methods=['GET', 'POST'])
@login_required
def edit_story(story_id):
    story = Story.query.get_or_404(story_id)
    if request.method == 'POST':
        story.title = request.form['title']
        story.content = request.form['content']
        story.tone = request.form['tone']
        story.genre = request.form['genre']
        db.session.commit()
        flash('Your story has been updated!', 'success')
        return redirect(url_for('view_story', story_id=story.id))
    return render_template('edit.html', story=story)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
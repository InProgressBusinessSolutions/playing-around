# app.py

from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a real secret key
Bootstrap(app)
ckeditor = CKEditor(app)

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')


class SearchForm(FlaskForm):
    """Form for the search query"""
    query = StringField('Enter your search query:', validators=[DataRequired()])
    submit = SubmitField('Search')


def scrape_and_analyze(query):
    """
    Scrape web content based on the query and analyze it

    Args:
    query (str): The search query

    Returns:
    dict: A dictionary containing the analysis results
    """
    try:
        # Perform a web search (this is a simplified example, you might want to use a proper search API)
        response = requests.get(f"https://en.wikipedia.org/wiki/{query}")
        response.raise_for_status()

        # Parse the content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text from paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])

        # Tokenize and remove stopwords
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text.lower())
        filtered_text = [word for word in word_tokens if word.isalnum() and word not in stop_words]

        # Get most common words
        fdist = FreqDist(filtered_text)
        most_common = fdist.most_common(10)

        # Get a summary (first 3 sentences)
        sentences = text.split('.')[:3]
        summary = '. '.join(sentences) + '.'

        return {
            'most_common_words': most_common,
            'summary': summary
        }
    except requests.RequestException as e:
        app.logger.error(f"Error scraping content: {str(e)}")
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle the main page with the search form"""
    form = SearchForm()
    if form.validate_on_submit():
        query = form.query.data
        results = scrape_and_analyze(query)
        if results:
            return render_template('results.html', results=results, query=query)
        else:
            return render_template('error.html', message="Failed to retrieve results. Please try again.")
    return render_template('index.html', form=form)


@app.route('/api/search', methods=['POST'])
def api_search():
    """JSON API endpoint for search"""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'No query provided'}), 400

    query = data['query']
    results = scrape_and_analyze(query)

    if results:
        return jsonify(results)
    else:
        return jsonify({'error': 'Failed to retrieve results'}), 500


if __name__ == '__main__':
    app.run(debug=True)
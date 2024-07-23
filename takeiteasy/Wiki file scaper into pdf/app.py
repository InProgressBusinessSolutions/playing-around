from flask import Flask, render_template, request, send_file, flash
import requests
from bs4 import BeautifulSoup
import pdfkit
import os
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key

# Explicitly set the path to wkhtmltopdf
wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Adjust this path as necessary

# Check if wkhtmltopdf exists at the specified path
if not os.path.exists(wkhtmltopdf_path):
    print(f"wkhtmltopdf not found at {wkhtmltopdf_path}")
    print("Please install wkhtmltopdf and update the path in app.py")
    exit(1)

config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)


def get_image_base64(img_url):
    response = requests.get(img_url)
    return base64.b64encode(response.content).decode('utf-8')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title and content
            title = soup.find(id='firstHeading').text
            content = soup.find(id='mw-content-text').find_all(['p', 'h2', 'h3', 'img'])

            # Process content and encode images
            processed_content = []
            for element in content:
                if element.name == 'img':
                    src = element.get('src', '')
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://en.wikipedia.org' + src
                    img_base64 = get_image_base64(src)
                    processed_content.append({
                        'type': 'img',
                        'src': f"data:image/jpeg;base64,{img_base64}"
                    })
                else:
                    processed_content.append({
                        'type': element.name,
                        'text': element.text
                    })

            # Render template with scraped data
            html = render_template('result.html', title=title, content=processed_content)

            # Generate PDF
            pdf_file = 'output.pdf'
            pdfkit.from_string(html, pdf_file, configuration=config, options={
                'enable-local-file-access': None,
                'encoding': 'UTF-8',
            })

            return send_file(pdf_file, as_attachment=True)
        except requests.RequestException as e:
            flash(f"Error fetching the URL: {str(e)}", 'error')
        except pdfkit.PDFKitError as e:
            flash(f"Error generating PDF: {str(e)}", 'error')
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", 'error')

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
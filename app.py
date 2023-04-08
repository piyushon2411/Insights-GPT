from flask import Flask, render_template, request
# Import your existing functions from your main script
from crawlCTA import get_buttons_from_url, extract_button_text

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        button_locations = get_buttons_from_url(url)
        button_texts = extract_button_text(button_locations)
        return render_template('index.html', button_texts=button_texts)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

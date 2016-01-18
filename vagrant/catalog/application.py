from flask import Flask, render_template, url_for

app = Flask(__name__)


# Show all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    return render_template('categories.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

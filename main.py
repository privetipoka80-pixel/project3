from flask import Flask, render_template
import data.db_session as db_session

db_session.global_init('db/shop.db')

app = Flask(__name__)
app.secret_key = 'dev_secret_key_123'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
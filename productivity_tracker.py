from flask import Flask

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return "<p>Lebron James!</p>"



if __name__ == '__main__':
    app.run(debug=True)
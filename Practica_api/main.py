from flask import Flask

app = Flask(__name__)

@app.get("/")
def root():
    return "Hola mundo"

@app.get("/url")
def url():
    return "Weon en la url"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, jsonify
from smhilog.util.store import Store
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
    
@app.route("/api/date")
def api_date():
    with Store('./smhilog/smhilog.sqlite3') as store:
        return jsonify(store.get_dates())

@app.route("/api/data/<date_key>")
def api_data(date_key):
    with Store('./smhilog/smhilog.sqlite3') as store:
       return jsonify(store.get_data(date_key))
       
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)


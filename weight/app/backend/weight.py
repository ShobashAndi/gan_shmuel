from flask import Flask, request
from datetime import datetime
import mysqlweight

import routes_functions.get_weight
import routes_functions.get_item
import routes_functions.get_session
import routes_functions.get_unknown
import routes_functions.post_weight
import routes_functions.post_batch_weight


app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def home():
#     return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    try:
        mysqlweight.connect()
        return 'OK', 200
    except:
        return 'Failure', 500


@app.route("/weight", methods=["GET"])
def get_weight():
    now = datetime.now()
    paramFrom = request.args.get("from", now.strftime("%Y%m%d000000"))
    paramTo = request.args.get("to", now.strftime("%Y%m%d%H%M%S"))

    return routes_functions.get_weight.get_weight(paramFrom, paramTo)


@app.route("/item/<id>", methods=["GET"])
def get_item(id):
    now = datetime.now()
    paramFrom = request.args.get("from", now.strftime("%Y%m01000000"))
    paramTo = request.args.get('to', now.strftime('%Y%m%d%H%M%S'))

    return routes_functions.get_item.get_item(id, paramFrom, paramTo)


@app.route("/session/<id>", methods=["GET"])
def get_session(id):
    return routes_functions.get_session.get_session(id)


@app.route("/unknown", methods=["GET"])
def get_unknown():
    return routes_functions.get_unknown.get_unknown()


@app.route("/weight", methods=["POST"])
def post_weight():
    return routes_functions.post_weight.post_weight()


@app.route("/batch-weight", methods=["POST"])
def post_batch_weight():
    return routes_functions.post_batch_weight.post_batch_weight()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    # app.run(debug=True, host="0.0.0.0", port="5001")

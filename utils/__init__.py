from flask import jsonify


def return_response(status_code, status=None, message=None, data=None):
    res_data = {
        "status": status,
        "message": message,
    }

    if data:
        res_data["data"] = data

    return jsonify(res_data), status_code

from flask import Flask, request, jsonify
from db_utils_query import run_query

app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "ARGO Backend is running!"}

# 1. General SQL query (careful: hackathon demo only)
@app.route("/query")
def query():
    sql = request.args.get("sql")
    try:
        result = run_query(sql)
        return jsonify(result)
    except Exception as e:
        return {"error": str(e)}

# 2. Salinity profiles by region + date
@app.route("/salinity")
def salinity():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    month = request.args.get("month")
    year = request.args.get("year")

    query = """
        SELECT latitude, longitude, time, salinity
        FROM argo_data
        WHERE strftime('%m', time) = ? AND strftime('%Y', time) = ?
          AND ABS(latitude - ?) < 5
          AND ABS(longitude - ?) < 5
    """
    result = run_query(query, (month.zfill(2), year, lat, lon))
    return jsonify(result)

# 3. Nearest float
@app.route("/nearest")
def nearest():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))

    query = """
        SELECT latitude, longitude, time, temperature, salinity,
               ((latitude - ?)*(latitude - ?) + (longitude - ?)*(longitude - ?)) as dist
        FROM argo_data
        ORDER BY dist ASC LIMIT 1
    """
    result = run_query(query, (lat, lat, lon, lon))
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

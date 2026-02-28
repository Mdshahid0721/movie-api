from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

TMDB_API_KEY = "69aae3dc11b4e7ae18cd17ca08d0ef54"
BASE_URL = "https://api.themoviedb.org/3"


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        query = data.get("movie")

        if not query:
            return jsonify({"recommendations": []})

        # Step 1: Search multi
        search_url = f"{BASE_URL}/search/multi"
        response = requests.get(search_url, params={
            "api_key": TMDB_API_KEY,
            "query": query
        })

        results = response.json().get("results", [])

        recommendations = []

        for item in results[:6]:

            # If it's a movie
            if item["media_type"] == "movie":
                title = item.get("title")
                poster_path = item.get("poster_path")
                vote = item.get("vote_average", 0)

                poster = (
                    f"https://image.tmdb.org/t/p/w500{poster_path}"
                    if poster_path else "N/A"
                )

                recommendations.append({
                    "title": title,
                    "poster": poster,
                    "score": vote
                })

            # If it's a person (actor/director)
            elif item["media_type"] == "person":
                person_id = item["id"]

                # Get their movie credits
                credits_url = f"{BASE_URL}/person/{person_id}/movie_credits"
                credits = requests.get(credits_url, params={
                    "api_key": TMDB_API_KEY
                }).json()

                for movie in credits.get("cast", [])[:3]:
                    title = movie.get("title")
                    poster_path = movie.get("poster_path")
                    vote = movie.get("vote_average", 0)

                    poster = (
                        f"https://image.tmdb.org/t/p/w500{poster_path}"
                        if poster_path else "N/A"
                    )

                    recommendations.append({
                        "title": title,
                        "poster": poster,
                        "score": vote
                    })

        return jsonify({"recommendations": recommendations[:8]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
import os
from flask import Flask, request, jsonify
import ollama
import time
from flask import send_from_directory


app = Flask(__name__)


@app.route("/")
def home():
    return send_from_directory("static", "index.html")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        start_time = time.time()

        prompt = request.form.get("prompt")
        image = request.files.get("image")

        print("----------",prompt)
        print("----------",image)

        if not prompt or not image:
            return jsonify({"error": "prompt and image are required"}), 400

        # 🔥 Delete old images
        for f in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, f)
            if os.path.isfile(file_path):
                os.remove(file_path)


        print("Old images deleted.")


        # Save new image
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)

        # Call Ollama
        resp = ollama.chat(
            model="qwen2.5vl:3b",
            messages=[
                {
                    "role": "user",
                    "content": "describe the image in detail",
                    "images": [image_path]
                }
            ],
            stream=True
        )
        print("Ollama response received.", resp)


        full_response = ""
        for chunk in resp:
            if "message" in chunk:
                text = chunk["message"]["content"]
                full_response += text

        print("Full response:", full_response)

        return jsonify({
            "response": full_response,
            "time_taken": time.time() - start_time
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

from flask import Flask, request, jsonify
import ollama
import time

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        start_time = time.time()

        # Get data from request
        data = request.get_json()
        prompt = data.get("prompt")
        image_path = data.get("image_path")

        if not prompt or not image_path:
            return jsonify({"error": "prompt and image_path are required"}), 400

        # Call Ollama model
        resp = ollama.chat(
            model="qwen2.5vl:3b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_path]
                }
            ],
            # options={
            #     "temperature": 0,
            #     "num_gpu": 1,
            #     "gpu_layers": 20000
            # },
            stream=True
        )

        # Collect response
        full_response = ""
        for chunk in resp:
            if "message" in chunk:
                text = chunk["message"]["content"]
                full_response += text

        return jsonify({
            "response": full_response,
            "time_taken": time.time() - start_time
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

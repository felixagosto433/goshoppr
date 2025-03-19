from flask import Flask, request, jsonfy

app = Flask(__name__)

@app.route("/")
def first_function():
    return "Welcome to my Flask App"

@app.route("/hello")
def second_function():
    return "Hello, Flask!"

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/chat", methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    return jsonfy({"response": f"You said: {user_message}"})

if __name__ == "__main__":
    app.run(debug=True)
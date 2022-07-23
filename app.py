from flask import Flask, request, render_template
from flask_wtf.csrf import CSRFProtect
from Scanner import *
app = Flask(__name__)
csrf = CSRFProtect(app)

@app.route("/", methods=['GET', 'POST'])
@csrf.exempt
def index():
    if request.method == "POST":
        file = request.files['image']
        if file.filename:
            image = "static/image/papers/1.png"
            file.save(image)
            result = "static/image/result/result.png"
            direction = request.form.get("direction")
            q_num = int(request.form.get("questions_number"))
            choice = int(request.form.get("choice_number"))
            Answers = Scann(image, result, direction, q_num, choice)
            return Answers
        return "Invalid Image !"
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# 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
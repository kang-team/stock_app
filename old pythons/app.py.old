# app.py
import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", message="hello")


if __name__ == "__main__":
    # Railway 배포를 위해 PORT 환경 변수를 사용하도록 설정합니다.
    # 로컬에서 실행 시 기본값은 5000입니다.
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True) # debug=True는 개발 중에 유용합니다.


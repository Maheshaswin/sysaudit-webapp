from flask import Flask, render_template
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def sysautdit_form():
    return render_template('index.html')


@app.route("/policy", methods=['GET', 'POST'])
def policy():
    return render_template('policy.html')


if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True)
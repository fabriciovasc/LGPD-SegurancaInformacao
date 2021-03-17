import os
from flask import (
    Flask, request, jsonify,
    render_template, redirect,
    url_for
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Usuario

@app.route("/")
def home():
    return 'Segurança de Informação'

@app.route("/add/usuario",methods=['GET', 'POST'])
def add_usuario_form():
    if request.method == 'POST':
        nome=request.form.get('nome')
        try:
            usuario=Usuario(
                nome=nome,
            )
            db.session.add(usuario)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            return(str(e))
    return render_template("adicionar_usuario.html")



if __name__ == '__main__':
    app.run()

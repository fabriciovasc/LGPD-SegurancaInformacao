from app import db


class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String())

    def __init__(self, nome):
        self.nome = nome

    def __repr__(self):
        return '{}'.format(self.nome)

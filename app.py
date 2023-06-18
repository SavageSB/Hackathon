from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
from random import choice, randint
from string import ascii_lowercase

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
with app.app_context():
    db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    personalId = db.Column(db.String(50), nullable=False, unique=True)
    phoneNumber = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    businessName = db.Column(db.String(50), nullable=False, default='None')
    balance = db.Column(db.Integer, nullable=False, default=0)
    finances = db.relationship('UserTransactions', backref='person', lazy=True)


class UserTransactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date)
    transaction = db.Column(db.Integer, nullable=False)
    location = db.Column(db.Integer, nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def response_generator(name, source, limit):
    result = {}
    for i in range(1, limit+1):
        income = randint(source // 2, source * 3 // 2)
        outcome = randint(source // 3, source * 5 // 4)
        result[f'{name}{i}'] = {
            'income': income,
            'outcome': outcome
        }
    return result


@app.route('/Stats/<int:id>')
def calculations(id):
    user = db.session.execute(db.select(User).filter_by(id=id)).first()[0]
    tviuri_shemosavali = sum(
        [transaction.transaction for transaction in user.finances])
    kvireuli_shemosavali = tviuri_shemosavali // 4
    dgiuri_shemosavali = kvireuli_shemosavali // 7
    print(tviuri_shemosavali)
    resp = dict()
    resp['days'] = response_generator('day', dgiuri_shemosavali, 7)
    resp['weeks'] = response_generator('week', kvireuli_shemosavali, 4)
    resp['months'] = response_generator('month', tviuri_shemosavali, 12)
    print(resp)
    return jsonify(resp)


@app.route('/')
def hello_world():  # put application's code here
    a = db.session.execute(db.select(User)).first()[0]
    jsn = {'name': a.name}
    return jsn


@app.route('/Register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        user = User(name=data['firstName'], lastName=data['lastName'], personalId=data['yourId'],
                    phoneNumber=data['phone'], email=data['email'], password=data['password'],
                    businessName=data['businessName'])
        email_check = db.session.execute(
            db.select(User).filter_by(email=user.email))
        phone_number_check = db.session.execute(
            db.select(User).filter_by(phoneNumber=user.phoneNumber))
        id_check = db.session.execute(
            db.select(User).filter_by(personalId=user.personalId))
        if bool(email_check):
            return {'responseMessage': "Email Already Exists."}
        if bool(phone_number_check):
            return {'responseMessage': 'Phone Number Already Exists.'}
        if bool(id_check):
            return {'responseMessage': 'Personal ID Already Exists.'}
        db.session.add(user)
        db.session.commit()
        return 'muwuka'
    else:
        return 'muwuka'


@app.route('/Transactions', methods=['GET'])
def transaction():
    user = db.session.execute(
        db.select(User).filter_by(id=1)
    ).first()[0]
    data = db.session.execute(
        db.select(UserTransactions).filter_by(userId=19)).scalars()
    response = {}
    response[user.name] = list()

    for j, i in enumerate(data):
        response[user.name].append(dict())
        response[user.name][j]['location'] = i.location
        response[user.name][j]['transaction'] = i.transaction
        response[user.name][j]['date'] = str(i.date)
    print(response)

    return jsonify(response)


@app.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        check = db.session.execute(db.select(User).filter_by(
            email=data['email'], password=data['password'])).first()

        print(bool(check))
        response = {'resp': bool(check)}
        return response
    else:
        return 'muwuka'

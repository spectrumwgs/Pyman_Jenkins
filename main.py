from flask import Flask
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import Column, String, Integer, Boolean
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

# Flask configuration
app = Flask(__name__)
app.config.from_object('configmodule')

# Instance initialization
jwt = JWTManager(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)


# Model definition
class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))

    def __init__(self, username, password):
        self.username = username
        self.password = password


# Marshmallow serialization
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password', 'roles', 'is_active')


# Database creation and schema initialization
db.create_all()
user_schema = UserSchema()
users_schema = UserSchema(many=True)


# Endpoints
@app.route('/')
def base():
    msg = {'msg': 'Hello World!'}
    return jsonify(msg)


@app.route('/register', methods=['POST'])
def register():
    req = request.get_json(force=True)
    username = req.get('username', None)
    password = req.get('password', None)
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 200


@app.route('/login', methods=['POST'])
def login():
    req = request.get_json(force=True)
    username = req.get('username', None)
    password = req.get('password', None)
    user = User.query.filter(User.username == username, User.password == password).first()
    ret = {'access_token': create_access_token(identity=user.username)}
    return jsonify(ret), 200


@app.route('/protected')
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


if __name__ == '__main__':
    app.run()

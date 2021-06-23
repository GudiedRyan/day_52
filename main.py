from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from secret_key import key
import random


app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes) 
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all")
def get_all():
    all_cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route('/search')
def search():
    location = request.args.get("location")
    cafes = db.session.query(Cafe).filter_by(location=location).all()
    if len(cafes) == 0:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})
    else:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


## HTTP POST - Create Record

@app.route('/cafe', methods=['POST'])
def add_new():
    cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=True,
        has_wifi=False,
        has_sockets=False,
        can_take_calls=True,
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

## HTTP PUT/PATCH - Update Record

@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        cafe.coffee_price = request.args.get('price')
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404

## HTTP DELETE - Delete Record

@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def delete(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        api_key = request.args.get('api_key')
        if api_key != key:
            return jsonify(response={"Failure": "Access denied. Try again with valid api key."}), 403
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(response={"Success": "Cafe has been removed from the database"}), 200
    return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from flask import jsonify
import os
#from dotenv import load_dotenv

#load_dotenv()



app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_BINDS'] = {
    'cafes': 'sqlite:///cafes.db'
}

db = SQLAlchemy()
db.init_app(app)

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

        return {column.name:getattr(self,column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    all_records = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(all_records)
    # return jsonify(name=random_cafe.name,
    #                location=random_cafe.location,
    #                id=random_cafe.id,
    #                map_url=random_cafe.map_url,
    #                img_url=random_cafe.img_url,
    #                seats = random_cafe.seats,
    #                has_toilet=random_cafe.has_toilet,
    #                has_wifi=random_cafe.has_wifi,
    #                has_sockets=random_cafe.has_sockets,
    #                can_take_calls=random_cafe.can_take_calls,
    #                coffee_price=random_cafe.coffee_price

    #You could also group properties into a subsection called amenities.
    # return jsonify(cafe={
    #     # Omit the id from the response
    #     # "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #
    #     # Put some properties in a sub-category
    #     "amenities": {
    #         "seats": random_cafe.seats,
    #         "has_toilet": random_cafe.has_toilet,
    #         "has_wifi": random_cafe.has_wifi,
    #         "has_sockets": random_cafe.has_sockets,
    #         "can_take_calls": random_cafe.can_take_calls,
    #         "coffee_price": random_cafe.coffee_price,
    #     }
    # })
# OR, the following could be a great way to return your data supposing you have MANY columns
    #First create a dictinary representation of your table data:
    return jsonify(cafes=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    all_cafes_list = list()
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route("/search")
def search():
    loc = request.args.get('loc')

    location = db.session.execute(db.select(Cafe).where(Cafe.location==loc)).scalars().all()
    if location:

        return jsonify(cafes=[cafe.to_dict() for cafe in location])
    else:
        return jsonify(errors={"not found":"sorry, but we can't find anything on this location"})


## HTTP POST - Create Record
@app.route("/add",methods=["POST"])
def add_cafe():
    new_cafe = Cafe(name =request.form.get('name'),
                    map_url=request.form.get('map_url'),
                    img_url=request.form.get('img_url'),
                    location=request.form.get('location'),
                    seats=request.form.get('seats'),
                    has_toilet=bool(request.form.get('has_toilet')),
                    has_wifi=bool(request.form.get('has_wifi')),
                    has_sockets=bool(request.form.get('has_sockets')),
                    can_take_calls=bool(request.form.get('can_take_calls')),
                    coffee_price=request.form.get('coffee_price')
                    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={"success": "Successfully added the new cafe."})



## HTTP PUT/PATCH - Update Record

@app.route("/update_price/<cafe_id>",methods=["PATCH"])
def update_cafe_price(cafe_id):
    price_to_chg = db.session.execute(db.select(Cafe).where(Cafe.id==cafe_id)).scalar()
    new_price=request.args.get("new_price")
    price_to_chg.coffee_price=new_price
    db.session.commit()
    return jsonify(success={'msg':"price change was successfull"})

@app.route("/report-closed/<cafe_id>",methods=["DELETE"])
def delete_cafe(cafe_id):

    closed_cafe = db.get_or_404(Cafe,cafe_id)
    api_key = os.environ.get("API_KEY")
    user_api_key = request.args.get('api_key')

    if user_api_key==api_key:
        db.session.delete(closed_cafe)
        db.session.commit()
        return jsonify(success={"cafe deleted":"the requested cafe has been deleted"})
    else:
        return jsonify(error={'action failed':"the operation was't successful. Ensure you're using the right api key"})


## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)

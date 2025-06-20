# !/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurants = [restaurant.to_dict(rules=('-restaurant_pizzas',)) 
                      for restaurant in Restaurant.query.all()]
        return make_response(jsonify(restaurants), 200)

api.add_resource(Restaurants, '/restaurants')


class RestaurantById(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        
        restaurant_data = restaurant.to_dict()
        restaurant_data['restaurant_pizzas'] = [
            {
                "id": rp.id,
                "pizza": rp.pizza.to_dict(),
                "pizza_id": rp.pizza_id,
                "price": rp.price,
                "restaurant_id": rp.restaurant_id
            }
            for rp in restaurant.restaurant_pizzas
        ]
        return restaurant_data, 200

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

api.add_resource(RestaurantById, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict(rules=('-restaurant_pizzas',)) 
                  for pizza in Pizza.query.all()]
        return make_response(jsonify(pizzas), 200)

api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            
            # Get the associated restaurant
            restaurant = db.session.get(Restaurant, data['restaurant_id'])
            
            return {
                "id": restaurant_pizza.id,
                "pizza": restaurant_pizza.pizza.to_dict(),
                "pizza_id": restaurant_pizza.pizza_id,
                "price": restaurant_pizza.price,
                "restaurant_id": restaurant_pizza.restaurant_id,
                "restaurant": restaurant.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400

api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)





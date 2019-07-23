
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.store import StoreModel

class Store(Resource):
    @jwt_required
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {'message': 'Store not found'}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {'message': "An store with name '{}' already exists.".format(name)}, 400

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"message":"An error occurred creating the store"}, 500  #Internal Server Error

        return store.json(), 201

    @jwt_required
    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {'message': 'Store deleted'}



class StoreList(Resource):
    def get(self):
        #if you only coding in Pyrhon:
        #return {'items': [it.json() for it in ItemModel.query.all()]}  
        
        #if you works with other programming languages (e.g. JS):
        #return {'stores': list(map(lambda x: x.json(), StoreModel.query.all()))} 
        return {'stores': [x.json() for x in StoreModel.find_all()]} 
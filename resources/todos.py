import json
from flask import Blueprint, g, url_for, abort, make_response, jsonify

from flask_restful import Resource, reqparse, marshal, fields, Api, marshal_with

from auth import auth
import models


todo_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'completed': fields.Boolean,
    'edited': fields.Boolean
}


def todo_or_404(todo_id):
    try:
        todo = models.ToDo.get_by_id(todo_id)
    except models.ToDo.DoesNotExist:
        abort(404)
    else:
        return todo


class ToDoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No name provided for todo item',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'completed',
            required=False,
            default=False,
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'edited',
            location=['form', 'json']
        )
        super().__init__()

    @auth.login_required
    def get(self):
        return [
            marshal(todo, todo_fields)
            for todo in models.ToDo.select()
        ], 200

    @auth.login_required
    @marshal_with(todo_fields)
    def post(self):
        args = self.reqparse.parse_args()
        todo = models.ToDo.create(
            created_by=g.user,
            **args
        )
        return (todo, 201, {
            'Location': url_for('resources.todos.todo', id=todo.id)
        })
    

class ToDo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'id',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No name provided for todo item',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'completed',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'edited',
            location=['form', 'json']
        )
        super().__init__()

    @auth.login_required
    @marshal_with(todo_fields)
    def get(self, id):
        return todo_or_404(id)

    @auth.login_required
    @marshal_with(todo_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        query = models.ToDo.update(**args).where(
            models.ToDo.id==id,
            models.ToDo.created_by==g.user
        )
        if not query.execute():
            abort(403)
        todo = todo_or_404(id)
        return (todo, 200, {
            'Location': url_for('resources.todos.todo', id=todo.id)
        })

    @auth.login_required
    def delete(self, id):
        query = models.ToDo.delete().where(models.ToDo.id==id)
        if query.execute() == 0:
            return abort(404)
        return '', 204, {'Location': url_for('resources.todos.todos')}


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    ToDoList,
    '/todos',
    endpoint='todos'
)
api.add_resource(
    ToDo,
    '/todos/<int:id>',
    endpoint='todo'
)

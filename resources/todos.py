from flask import Blueprint, g, url_for, abort

from flask_restful import Resource, reqparse, marshal, fields, Api, marshal_with

from auth import auth
import models


todo_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'completed': fields.Boolean,
}


def todo_or_404(todo_id):
    try:
        todo = models.ToDo.get_by_id(todo_id)
    except models.ToDo.DoesNotExists:
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
        super().__init__()

    def get(self):
        return [
            marshal(todo, todo_fields)
            for todo in models.ToDo.select()
        ]

    @marshal_with(todo_fields)
    def post(self):
        args = self.reqparse.parse_args()
        print(args)
        todo = models.ToDo.create(
            # fix this direct user, should be g object
            created_by=models.User.get_by_id(1),
            **args
        )
        return (todo, 201, {
            'Location': url_for('resources.todos.todo', id=todo.id)
        })


class ToDo(Resource):
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
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(todo_fields)
    def get(self, id):
        return todo_or_404(id)

    @marshal_with(todo_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        print(args)
        try:
            update = models.ToDo.update(**args).where(models.ToDo.id==id)
            update.execute()
        except models.ToDo.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That todo does not exist or is not editable'}
            ), 403)
        todo = todo_or_404(id)
        return (todo, 200, {
                'Location': url_for('resources.todos.todo', id=id)
                })

    def delete(self, id):
        delete = models.ToDo.delete().where(models.ToDo.id==id)
        delete.execute()
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

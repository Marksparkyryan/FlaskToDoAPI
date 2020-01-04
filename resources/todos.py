from flask import Blueprint, g, url_for, abort
from flask_restful import (Resource, reqparse, marshal, fields, Api,
                           marshal_with, inputs)

from auth import auth
import models


todo_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'completed': fields.Boolean,
    'edited': fields.Boolean,
}


def todo_or_404(todo_id):
    """Attempts to fetch a todo item if it exists. If not, responds with
    404.

    Arguments:
        todo_id {integer} -- integer id of ToDo item

    Returns:
        ToDo instance -- if item is successfuly found
        abort 404 response -- if item is not found
    """
    try:
        todo = models.ToDo.get_by_id(todo_id)
    except models.ToDo.DoesNotExist:
        abort(404)
    else:
        return todo


class ToDoList(Resource):
    """API endpoints for GET and POST methods of todo items
    """
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
            type=inputs.boolean,
            location=['form', 'json']
        )
        super().__init__()

    @auth.login_required
    def get(self):
        """Endpoint for handling GET requests. Returns a json response
        of all existing ToDo items with status 200.

        Returns:
            json response -- of all ToDo items with status 200
        """
        return [
            marshal(todo, todo_fields)
            for todo in models.ToDo.select()
        ], 200

    @auth.login_required
    @marshal_with(todo_fields)
    def post(self):
        """Endpoint for handling POST requests. Returns a json response
        of new ToDo item if successfully created. If not, returns a
        blank response with status 204.

        Returns:
            json response -- of single new ToDo item
            blank response -- if single item was not successfully
            created
        """
        args = self.reqparse.parse_args()
        try:
            todo = models.ToDo.create(
                created_by=g.user,
                **args
            )
        except models.IntegrityError:
            return '', 204
        return (todo, 201, {
            'Location': url_for('resources.todos.todo', id=todo.id)
        })


class ToDo(Resource):
    """API endpoints for GET, PUT, and DELETE methods of single ToDo 
    items
    """
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
            type=inputs.boolean,
            location=['form', 'json']
        )
        super().__init__()

    @auth.login_required
    @marshal_with(todo_fields)
    def get(self, id):
        """Endpoint for handling the getting of a single ToDo item
        
        Arguments:
            id {integer} -- integer id of single ToDo item
        
        Returns:
            ToDo instance -- if item is successfuly found
            abort 404 response -- if item is not found
        """
        return todo_or_404(id)

    @auth.login_required
    @marshal_with(todo_fields)
    def put(self, id):
        """Endpoint for handling PUT requests for single ToDo items
        
        Arguments:
            id {integer} -- integer id of single ToDo item
        
        Returns:
            ToDo instance -- if item is succussfully updated
            abort 403 response -- if item does not exist or requesting
            user is not the author of ToDo item.
        """
        args = self.reqparse.parse_args()
        query = models.ToDo.update(**args).where(
            models.ToDo.id == id,
            models.ToDo.created_by == g.user
        )
        if not query.execute():
            abort(403)

        todo = todo_or_404(id)
        return (todo, 200, {
            'Location': url_for('resources.todos.todo', id=todo.id)
        })

    @auth.login_required
    def delete(self, id):
        """Endpoint for handling DELETE requests of single ToDo items
        
        Arguments:
            id {integer} -- integer id of single ToDo item
        
        Returns:
            204 response -- blank 204 response if successfull
        """
        query = models.ToDo.delete().where(models.ToDo.id == id)
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

import json
import os
import unittest
import tempfile

from peewee import *

from app import app
import config
from models import User, ToDo

DATABASE = SqliteDatabase('test_db.sqlite')

class ToDoTestBase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client() 

        DATABASE.connect()
        DATABASE.create_tables([User, ToDo], safe=True)

        try:
            self.user1 = User.create_user(
                username='user1',
                email='user1@email.com',
                password='password1'
            )
        except:
            pass
        
        try:
            with open('mock/todos.json') as mocktodos:
                    json_reader = json.load(mocktodos)
                    for todo in json_reader:
                        ToDo.create(
                            created_by=1,
                            **todo
                        )
        except Exception as err:
            print(err)
            pass

    def tearDown(self):
        DATABASE.drop_tables([User, ToDo])
        DATABASE.close()


class AppTestCases(ToDoTestBase):
    """Tests for routes in app.py
    """
    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My TODOs!', response.data)
    
    def test_login(self):
        response = self.app.post('/login', data=dict(
            email='user1@email.com',
            password='password1'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    

class ResourceTestCases(ToDoTestBase):
    """Tests for the api resources in resources/todos.py
    """
    def get_token(self):
        """Get a token directly from the user instance to access api
        """
        token = self.user1.generate_auth_token()
        return "Token " + token.decode('ascii')

    def test_todolist_get(self):
        """Test the get list of all todos
        """
        token = self.get_token()
        response = self.app.get('/api/v1/todos', headers={'Content-Type': 'application/json', 'Authorization': token })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'pay dem bills', response.data)
        self.assertEqual(len(json.loads(response.data)), 6)
    
    def test_todolist_post(self):
        """Test the creation of a todo item
        """
        token = self.get_token()
        todo = json.dumps({"name": "do that thing", "created_by": 1, "edited": False})
        response = self.app.post('/api/v1/todos', data=todo, headers={'Content-Type': 'application/json', 'Authorization': token })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'do that thing', response.data)
        self.assertEqual(len(json.loads(response.data)), 4)
        response = self.app.get('/api/v1/todos', headers={'Content-Type': 'application/json', 'Authorization': token })
        self.assertEqual(len(json.loads(response.data)), 7)
        self.assertIn(b'do that thing', response.data)

    def test_todo_get_that_exists(self):
        """Test the getting of a single todo item that exists
        """
        token = self.get_token()
        response = self.app.get('/api/v1/todos/1', headers={'Content-Type': 'application/json', 'Authorization': token })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'clean the house', response.data)
        self.assertEqual(len(json.loads(response.data)), 4)
    
    def test_todo_get_that_does_not_exist(self):
        """Test the getting of a single todo item that doesn't exist
        """
        token = self.get_token()
        response = self.app.get('/api/v1/todos/999', headers={'Content-Type': 'application/json', 'Authorization': token })
        self.assertEqual(response.status_code, 404)
    
    def test_edit_of_item(self):
        token = self.get_token()
        todo = json.dumps({"id": 5, "name": "run faster", "created_by": 1, "edited": True, "completed": False})
        response = self.app.put('/api/v1/todos/5', data=todo, headers={'Content-Type': 'application/json', 'Authorization': token })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'run faster', response.data)
        self.assertEqual(len(json.loads(response.data)), 4)
    
    def test_edit_of_item_does_not_exist(self):
        token = self.get_token()
        todo = json.dumps({"id": 85, "name": "run faster", "created_by": 1, "edited": True, "completed": False})
        response = self.app.put('/api/v1/todos/85', data=todo, headers={'Content-Type': 'application/json', 'Authorization': token })
        self.assertEqual(response.status_code, 403)
    
    def test_delete_of_item(self):
        token = self.get_token()
        todo = json.dumps({"id": 5, "name": "run faster", "created_by": 1, "edited": True, "completed": False})
        response = self.app.delete('/api/v1/todos/5', data=todo, headers={'Content-Type': 'application/json', 'Authorization': token })
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(b'run faster', response.data)
        self.assertEqual(response.data, b"")
    
    def test_delete_of_item_that_does_not_exist(self):
        token = self.get_token()
        todo = json.dumps({"id": 99, "name": "run faster", "created_by": 1, "edited": True, "completed": False})
        response = self.app.delete('/api/v1/todos/99', data=todo, headers={'Content-Type': 'application/json', 'Authorization': token })
        self.assertEqual(response.status_code, 404)
        

    def test_all_api_endpoints_without_token(self):
        # get list of todos
        response = self.app.get('/api/v1/todos', headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 401)
        # add todo item
        todo = json.dumps({"name": "do that thing", "created_by": 1, "edited": False})
        response = self.app.post('/api/v1/todos', data=todo, headers={'Content-Type': 'application/json' })
        self.assertEqual(response.status_code, 401)
        # get single todo item
        response = self.app.get('/api/v1/todos/1', headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 401)




if __name__ == '__main__':
    try:
        if config.TESTING is not True:
            raise Exception("Config.TESTING is not True. To allow testing setconfig.TESTING "
            "to True to create a testing database and ensure main database is "
            "not used.")
    except Exception as err:
        print(err)
    else:
        unittest.main()
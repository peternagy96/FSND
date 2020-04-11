import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:postgres@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        response = self.client().get('/questions')
        self.assertEqual(response.status_code, 200)


    def test_delete_q(self):
        questions = Question.query.all()
        response = self.client().delete(f"/questions/{questions[0].id}")
        self.assertEqual(response.status_code, 200)


    def test_add_new_q(self):
        question = {
            'question': 'Test?',
            'answer': 'Test.', 'category': '1', 'difficulty': '1'
        }
        headers  = {'Content-type': 'application/json'}
        response = self.client().post('/questions',
                                 data=json.dumps(question),
                                 headers=headers)
        self.assertEqual(response.status_code, 200)


    def test_search_q(self):
        search_term = {"searchTerm": "title"}
        headers  = {'Content-type': 'application/json'}
        response = self.client().post("/questions/search", json=search_term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)


    def test_q_based_on_cat(self):
        response = self.client().get('/categories/1/questions')
        self.assertEqual(response.status_code, 200)


    def test_trivia_game(self):
        category = {'id': 1}
        quiz_data = {"previous_questions": [], "quiz_category": category}
        response = self.client().post("/quizzes", json=quiz_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
    



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
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
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'postgres',
            'root',
            'localhost:5432',
            self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'this is a test question?',
            'answer': 'this is a test answer',
            'difficulty': 3,
            'category': 2
        }

        self.failed_question = {
            'answer': 'this is a test answer',
            'difficulty': 3,
            'category': 2
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    '''
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen.
    Clicking on the page numbers should update the questions.
    '''
    # ------------success------------
    def test_get_all_questions_success(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['total_questions'])

    # ------------fail------------
    def test_get_all_questions_fail(self):
        '''using wrong endpoint [/question]'''
        res = self.client().get('/question')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    '''
    TEST: When you click the trash icon next to a question,
    -------------the question will be removed-------------
    This removal will persist in the database and when you refresh the page.
    '''
    # ------------success------------
    def test_del_question_success(self):

        question = Question(
            'this is a test question?',
            'this is a test answer',
            3,
            2
        )

        question.insert()

        res = self.client().delete('/questions/{}'.format(question.id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['deleted'])

    # ------------fail------------
    def test_del_question_fail(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    '''
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end
    of the last page of the questions list in the "List" tab.
    '''
    # ------------success------------
    def test_add_new_question_success(self):
        res = self.client().post(
            '/questions',
            json=self.new_question
            )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    # ------------fail------------
    def test_add_new_question_fail(self):
        res = self.client().post(
            'questions',
            json=self.failed_question
            )

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    '''
    TEST: Search by any phrase.
    The questions list will update to include only question
    that include that string within their question.
    Try using the word "title" to start.
    '''
    # ------------success------------
    def test_search_question_success(self):
        res = self.client().post('/questions', json={
            'searchTerm': 'Taj Mahal'
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['searchTerm'], 'Taj Mahal')
        self.assertTrue(data['questions'])

    # ------------fail------------
    def test_search_question_fail(self):
        res = self.client().post('/questions', json={
            'searchTerm': 'notInDatabase'
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    '''
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    # ------------success------------
    def test_get_questions_by_category_success(self):
        id = 2
        res = self.client().get(
            '/categories/{}/questions'.format(id))
        data = json.loads(res.data)

        category = Category.query.get(id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['currentCategory'], category.type)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    # ------------fail------------
    def test_get_questions_by_category_fail(self):
        id = 1000
        res = self.client().get(
            '/categories/{}/questions'.format(id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    '''
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    # ------------success------------
    def test_get_quiz_success(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id': 1,
                'type':'Science'
            }})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    # ------------success------------
    def test_finish_quiz_success(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [20, 21, 22],
            'quiz_category': {
                'id': 1,
                'type':'Science'
            }})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['message'],
            'you finished all questions in this category'
            )

    # ------------fail------------
    def test_get_quiz_fail(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id': 7,
                'type':'Development'
            }})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

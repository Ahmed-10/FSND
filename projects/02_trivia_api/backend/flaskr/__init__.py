import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def pages_pagination(request):
    page = request.args.get('page', 1, type=int)

    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    return [start, end]


def get_all_questions():
    selection = Question.query.all()
    questions = [question.format() for question in selection]
    return questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    Set up CORS. Allow '*' for origins.
    '''
    CORS(app, resources={'/': {'origins': '*'}})

    '''
    the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):

        response.headers.add(
          'Access-Control-Allow-Headers',
          'Content-Type, Authorization'
        )

        response.headers.add(
          'Access-Control-Allow-Methods',
          'GET, POST, PATCH, DELETE, OPTIONS'
        )

        return response

    '''
    GET endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    def get_categories():

        selection = Category.query.all()
        categories = [c.format() for c in selection]

        if len(categories) == 0:
            abort(404)

        return jsonify({
          'success': True,
          'categories': categories,
          'num_of_categories': len(categories)
        })

    '''
    GET endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    def get_questions():

        questions = get_all_questions()

        if len(questions) == 0:
            abort(404)

        start, end = pages_pagination(request)

        categories = Category.query.all()
        category_dict = {}

        for category in categories:
            category_dict[category.id] = category.type

        return jsonify({
          'success': True,
          'questions': questions[start:end],
          'total_questions_num': len(questions),
          'categories': category_dict
        })

    @app.route('/questions/<int:question_id>', methods=['GET'])
    def get_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)
        else:
            return jsonify(question.format())

    '''
    DELETE an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    -------------the question will be removed-------------
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def del_question(id):

        question = Question.query.get(id)

        # if question is None:
        #     abort(404)

        try:
            question.delete()

            questions = get_all_questions()
            start, end = pages_pagination(request)

            return jsonify({
              'success': True,
              'deleted': id,
              'questions': questions[start:end],
              'total_questions_num': len(questions),
            })

        except:
            abort(422)

    '''
    POST endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end
    of the last page of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def insert_question():
        body = request.get_json()

        if body.get('search_string') is None:
            question = body.get('question')
            answer = body.get('answer')
            difficulty = body.get('difficulty')
            category = body.get('category')
            new_question = Question(question, answer, category, difficulty)

            try:
                new_question.insert()

                selection = Question.query.all()
                questions = [q.format() for q in selection]
                start, end = pages_pagination(request)

                return jsonify({
                  'success': True,
                  'inserted': new_question.id,
                  'questions': questions[start:end],
                  'total_questions_num': len(questions),
                })

            except:
                abort(422)

        else:
            '''
            POST endpoint to get questions based on a search term.
            It should return any questions for whom the search term
            is a substring of the question.

            TEST: Search by any phrase.
            The questions list will update to include only question
            that include that string within their question.
            Try using the word "title" to start.
            '''
            search_string = body.get('search_string')

            result = Question.query.filter(
              Question.question.ilike('%' + search_string + '%')
              ).all()

            questions = [r.format() for r in result]

            if len(questions) == 0:
                abort(404)

            start, end = pages_pagination(request)
            return jsonify({
              'success': True,
              'search_string': search_string,
              'questions': questions[start: end]
            })

    '''
    GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_category(id):
        category = Category.query.get(id)

        if category is None:
            abort(404)

        selection = Question.query.filter_by(category=category.id).all()

        questions = [q.format() for q in selection]

        if len(questions) == 0:
            abort(404)

        start, end = pages_pagination(request)
        return jsonify({
          'success': True,
          'category': category.type,
          'questions': questions[start: end]
        })

    '''
    POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        body = request.get_json()

        previous_questions = body.get('previous_questions')
        category_id = body.get('quiz_category')

        if category_id == 0:
            questions = Question.query.all()

        else:
            questions = Question.query.filter_by(
              category=category_id
            ).all()

        if len(previous_questions) == len(questions):
            return jsonify({
              'success': True,
              'message': 'you finished all questions in this category'
            })

        question = questions[random.randint(0, len(questions)-1)]
        in_previous = True

        while in_previous:
            if question.id in previous_questions:
                question = questions[random.randint(0, len(questions)-1)]

            else:
                in_previous = False

        return jsonify({
          'success': True,
          'question': question.format()
        })

    '''
    Error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
          'success': False,
          'error': 422,
          'message': 'unprocessable'
        }), 422

    return app

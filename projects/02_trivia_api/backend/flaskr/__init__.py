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


def get_all_categories():
    selection = Category.query.all()
    categories = {}

    for category in selection:
        categories[category.id] = category.type

    return categories


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

        categories = get_all_categories()

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
    '''
    @app.route('/questions', methods=['GET'])
    def get_questions():

        questions = get_all_questions()

        if len(questions) == 0:
            abort(404)

        start, end = pages_pagination(request)

        categories = get_all_categories()

        return jsonify({
          'success': True,
          'questions': questions[start:end],
          'totalQuestions': len(questions),
          'categories': categories,
          'currentCategory': None
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
    '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def del_question(id):

        question = Question.query.get(id)

        if question is None:
            abort(404)

        try:
            question.delete()

            return jsonify({
              'success': True,
              'deleted': id
            })

        except:
            abort(422)

    '''
    POST endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    '''
    @app.route('/questions', methods=['POST'])
    def insert_question():
        body = request.get_json()

        if body.get('searchTerm') is None:

            try:
                question = body.get('question')
                answer = body.get('answer')
                difficulty = body.get('difficulty')
                category = body.get('category')

                if (question is None or answer is None
                        or difficulty is None or category is None):
                    abort(422)

                new_question = Question(question, answer, category, difficulty)

                new_question.insert()

                return jsonify({
                  'success': True,
                  'question': new_question.question
                })

            except:
                abort(422)

        else:
            '''
            POST endpoint to get questions based on a search term.
            It should return any questions for whom the search term
            is a substring of the question.
            '''
            search_string = body.get('searchTerm')

            result = Question.query.filter(
              Question.question.ilike('%' + search_string + '%')
              ).all()

            questions = [r.format() for r in result]

            if len(questions) == 0:
                abort(404)

            start, end = pages_pagination(request)
            return jsonify({
              'success': True,
              'searchTerm': search_string,
              'questions': questions[start: end]
            })

    '''
    GET endpoint to get questions based on category.
    '''
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_category(id):
        category = Category.query.get(id)

        if category is None:
            abort(404)

        selection = Question.query.filter_by(category=category.id).all()
        all_questions = Question.query.all()

        questions = [q.format() for q in selection]

        if len(questions) == 0:
            abort(404)

        start, end = pages_pagination(request)
        return jsonify({
          'success': True,
          'currentCategory': category.type,
          'questions': questions[start: end],
          'totalQuestions': len(all_questions)
        })

    '''
    POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    '''
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        body = request.get_json()

        previous_questions = body.get('previous_questions')
        category = body.get('quiz_category')
        category_id = category.get('id')

        if category_id == 0:
            questions = Question.query.all()

        else:
            category = Category.query.get(category_id)
            if category is None:
                abort(404)

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

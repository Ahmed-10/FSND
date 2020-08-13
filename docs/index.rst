.. Trivia API documentation master file, created by
   sphinx-quickstart on Thu Aug 13 18:16:01 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Trivia API's documentation!
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Udacity is invested in creating bonding experiences for its employees and students. 

A bunch of team members got the idea to hold trivia on a regular basis and to create a webpage to manage the trivia app and play the game. so we built the APIs they needed to support their application.

what does The application do:

1. Display questions - both all questions and by category. Questions show the question, category and difficulty rating by default and can show/hide the answer. 
2. Delete questions.
3. Add questions and require that they include question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category. 


Indices and tables
==================

* `Getting Started`_
   * `Dependencies`_
   * `PIP Dependencies`_
   * `Database Setup`_
   * `Running the server`_
   * `Testing`_
* `API referance`_
   * `GET '/categories'`_
   * `GET '/questions'`_
   * `DELETE '/questions/<question_id>'`_
   * `POST '/questions'`_
   * `GET '/categories/<id>/questions'`_
   * `POST '/quizzes'`_


Getting Started
================

.. _Dependencies:

**Dependencies**

* Python 3.7: Follow instructions to install the latest version of python for your platform in the python docs

* Virtual Enviornment: We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the python docs

-------------------

.. _PIP Dependencies:

**PIP Dependencies**

* Once you have your virtual environment setup and running, install dependencies by naviging to the ``/backend`` directory and running::

   pip install -r requirements.txt

This will install all of the required packages we selected within the ``requirements.txt`` file.

-------------------

.. _Database Setup:

**Database Setup**

With Postgres running, restore a database using the ``trivia.psql`` file provided. *From the backend folder in terminal run*::

   psql trivia < trivia.psql

-------------------

.. _Running the server:

**Running the server**

From within the ``backend`` directory first ensure you are working using your created virtual environment.

To run the server, execute:
::

   export FLASK_APP=flaskr
   export FLASK_ENV=development
   flask run


Setting the ``FLASK_ENV`` variable to development will detect file changes and restart the server automatically.

Setting the ``FLASK_APP`` variable to flaskr directs flask to use the flaskr directory and the ``__init__.py`` file to find the application.

-------------------

.. _Testing:

**Testing**

To run the tests, run ::

   dropdb trivia_test

   createdb trivia_test

   psql trivia_test < trivia.psql

   python test_flaskr.py

API referance
=============

.. _GET '/categories':

**GET**
*'/categories'*

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with three keys, success, num_of_categories, and categories, that contains a object of id: category_string key:value pairs. 

::

   {
      'success': True,
      'categories': {
         '1' : "Science",
         '2' : "Art",
         '3' : "Geography",
         '4' : "History",
         '5' : "Entertainment",
         '6' : "Sports"
         },
      'num_of_categories': 6
   }

-------------

.. _GET '/questions':

**GET**
*'/questions'*

- Fetches a list of questions in each quetion the keys are the question, answer, category, difficulty and the values are the corresponding of each
- Request Arguments: None
- Returns: An object with five keys, success, total_questions, categories, currentCategory, and questions that contains an array of objects. 

::

   {
      "categories": {
         "1": "Science",
         "2": "Art",
         "3": "Geography",
         "4": "History",
         "5": "Entertainment",
         "6": "Sports"
      },
      "currentCategory": null,
      "questions": [
         {
            "answer": "Maya Angelou",
            "category": 4,
            "difficulty": 2,
            "id": 5,
            "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
         }, ....],
      "success": true,
      "total_questions": 21
   }


-------------

.. _DELETE '/questions/<question_id>':

**DELETE** 
*'/questions/<question_id>'*

- An endpoint to DELETE question using a question ID.
- Request Arguments: None
- Returns: An object with Two keys, success, and deleted that contains a value of the deleted quetion ID. 

::

   {
      "deleted": 10,
      "success": true
   }


-------------

.. _POST '/questions':

**POST** 
*'/questions'*

- to add a new question to an existing category
   - Request Arguments:
   
   ::

      {
         "question": "this is a test question?",
         "answer": "this is a test answer",
         "difficulty": 3,
         "category": 2
      }

   - Returns: 
   
   ::
   
      {
         "question": "this is a test question?",
         "success": true
      }

---

- Fetches a list of questions that contains a specific search term 
   - Request Arguments: 
   
   ::

      {
         "searchTerm": "Taj Mahal"
      }

   - Returns: An object with three keys, success, searchTerm, and list of questions that contain the search term. 
   
   ::

      {
         "questions": [
            {
               "answer": "Agra",
               "category": 3,
               "difficulty": 2,
               "id": 15,
               "question": "The Taj Mahal is located in which Indian city?"
            }
         ],
         "searchTerm": "Taj Mahal",
         "success": true
      }

-------------

.. _GET '/categories/<id>/questions':

**GET** 
*'/categories/<id>/questions'*

- Fetches a list of questions in each quetion the keys are the question, answer, category, difficulty and the values are the corresponding of each
- Request Arguments: None
- Returns: An object with four keys, success, total_questions, currentCategory, and questions that contains an array of objects.

::

   {
      "currentCategory": "Sports",
      "questions": [
         {
            "answer": "Uruguay",
            "category": 6,
            "difficulty": 4,
            "id": 11,
            "question": "Which country won the first ever soccer World Cup in 1930?"
         }, ...],
      "success": true,
      "total_questions": 20
   }

-------------

.. _POST '/quizzes':

**POST** 
*'/quizzes'*

- Fetches a question from the available categories
- Request Arguments: a list of previous questions IDs and the specific category you want the questions in

::

   {
      "previous_questions": [20, 22],
      "quiz_category": {
         "id": 1,
         "type": "Science"
      }
   }

- Returns: An object with three keys, success, num_of_categories, and categories, that contains a object of id: category_string key:value pairs. 

::

   {
      "question": {
         "answer": "Alexander Fleming",
         "category": 1,
         "difficulty": 3,
         "id": 21,
         "question": "Who discovered penicillin?"
      },
      "success": true
   }

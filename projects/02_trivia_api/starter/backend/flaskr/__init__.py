import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    #app.config.from_object('config')
    setup_db(app)




    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                            'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                            'GET,PATCH,POST,DELETE,OPTIONS')
        return response


    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        if len(categories) > 0:
            category_obj = {cat.id: cat.type for cat in categories}
            return jsonify({
                'success': True,
                'categories': category_obj
            })




    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions', methods=['GET'])
    def index():
        try:
            page_num = request.args.get('page', 1, type=int)
            all_categories = Category.query.order_by(Category.id).all()
            categories = {}
            for category in all_categories:
                categories[category.id] = category.type
                    
            questions = Question.query.paginate(
                page=page_num, per_page=QUESTIONS_PER_PAGE)

            return jsonify({
                'success': True,
                'categories': categories,
                'questions': [question.format() for question
                                in questions.items],
                'total_questions': questions.total,
                'current_category': None
            })
        except:
            abort(404)


    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            return jsonify({
                'success': True
            })
        except:
            abort(404)






    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def post_question():
        try:
            input_data = request.get_json()

            new_question = Question(question=input_data.get('question', None),
                            answer=input_data.get('answer', None),
                            difficulty=input_data.get('difficulty', None),
                            category=input_data.get('category', None))
            new_question.insert()
            return jsonify({
                'success': True
            })
        except:
            abort(404)




    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            page_num = request.args.get('page', 1, type=int)
            search_query = request.get_json().get('searchTerm', '')

            if search_query == '':
                pass
            else:
                search_results = Question.query\
                    .filter(Question.question.ilike(f'%{search_query}%'))
                page_results = search_results.paginate(page=page_num, 
                                        per_page=QUESTIONS_PER_PAGE)
            return jsonify({
                'success': True,
                'questions': [result.format() for result
                                in page_results.items],
                'total_questions': page_results.total
            })

        except:
            abort(404)



    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def questions_by_category(cat_id):
        try:
            page_num = request.args.get('page', 1, type=int)
            category = Category.query.filter(Category.id == cat_id).one_or_none()
            if category is None:
                abort(422)
            questions = Question.query.filter(Question.category == cat_id)
            page_results = questions.paginate(page=page_num, 
                                        per_page=QUESTIONS_PER_PAGE)
            return jsonify({
                'success': True,
                'questions': [result.format() for result
                                in page_results.items],
                'total_questions': page_results.total,
                'current_category': category.type
            })
        except:
            abort(404)


    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()

            cat_id = body.get('quiz_category', None)['id']
            print(cat_id)
            prev_questions = body.get('previous_questions', None)
            if cat_id == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(Question.category == cat_id)       
            not_used_questions = [question.format() for question in questions
                    if question.id not in prev_questions]
            
            print(questions)
            if len(not_used_questions) > 0:
                question = random.choice(not_used_questions)
                return jsonify({
                    'success': True,
                    'question': question
                })
            abort(404)



        except:
            abort(404)





    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal application error'
        }), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable'
        }), 422

    return app


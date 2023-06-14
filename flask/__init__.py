import logging
import azure.functions as func
from flask import Flask, request, render_template, flash
from decouple import config
from . import api

endpoint = config('ENDPOINT')
secret_key = config('SECRET_KEY')

app = Flask(__name__)
app.config.from_mapping(SECRET_KEY=secret_key)
api = api.API(endpoint)

app_data = {
    'title': config('APP_TITLE'),
    'logo': 'APP_LOGO',
}

@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template(
        "home.html",
        page="home",
        data=app_data,
        summary=api.summary(),
    )

@app.route("/article", methods=['POST', 'GET'])
@app.route("/article/<article_id>", methods=['GET'])
def article(article_id: int = None):
    # recommended articles related to an article in question
    recommended_articles = None

    if article_id is None:
        if request.method == 'GET':
            article_id = request.args.get('article_id')

        elif request.method == 'POST':
            article_id = request.form['article_id']
            if article_id == '':
                article_id = None

    if article_id:
        try:
            article_id = int(article_id)
        except:
            article_id = None
    
    if article_id is not None and (article_id < 0 or article_id >= api.get('n_items')):
        flash(f"article_id {article_id}, n'existe pas")
        article_id = None

    if article_id is not None:
        recommended_articles = api.recommended_articles(article_id=article_id)

    return render_template(
        "article/index.html",
        page="article",
        data=app_data, 

        article_id=article_id,
        recommended_articles = recommended_articles,
        popular_articles=api.popular_articles(),
        random_articles=api.random_articles()
    )

@app.route("/category", methods=['POST', 'GET'])
@app.route("/category/<category_id>", methods=['GET'])
def category(category_id: int = None):
    # recent and popular articles of a specific category
    recent_articles = None
    popular_articles = None

    if category_id is None:
        if request.method == 'GET':
            category_id = request.args.get('category_id')

        elif request.method == 'POST':
            category_id = request.form['category_id']
            if category_id == '':
                category_id = None

    if category_id:
        try:
            category_id = int(category_id)
        except:
            category_id = None

    if category_id is not None and (category_id < 0 or category_id >= api.get('n_groups')):
        flash(f"category_id {category_id}, n'existe pas")
        category_id = None

    if category_id is not None:
        recent_articles = api.recent_articles(category_id=category_id)
        popular_articles = api.popular_articles(category_id=category_id)

    return render_template(
        "category/index.html",
        page="category",
        data=app_data,

        category_id=category_id,
        recent_articles=recent_articles,
        popular_articles=popular_articles,
        popular_categories=api.popular_categories(),
        random_categories=api.random_categories(),
    )

@app.route("/user", methods=['POST', 'GET'])
@app.route("/user/<user_id>", methods=['GET'])
def user(user_id: int=None):
    recommended_articles = []
    recent_articles = []

    block = request.args.get('block')
    blocks = None
    users = []
    n_users = api.get('n_users')
    
    if user_id is None:
        if request.method == 'GET':
            user_id = request.args.get('user_id')

        elif request.method == 'POST':
            user_id = request.form['user_id']
            if user_id == '':
                user_id = None    

    if user_id is not None:
        try:
            user_id = int(user_id)
        except:
            user_id = None

    if user_id is not None and (user_id < 0 or user_id >= n_users):
        flash(f"user_id {user_id}, n'existe pas")
        user_id = None

    if user_id is not None:
        recommended_articles = api.recommended_articles(user_id=user_id)
        recent_articles = api.recent_articles(user_id=user_id)
    else:
        blocks = [x for x in range(n_users//1000 + 1)]
        block = request.args.get('block')
        try:
            block = int(block)
        except:
            block = 0

        for x in range(1000):
            uid = block*1000 + x
            if uid < n_users:
                users.append(uid)

    return render_template(
        "user/index.html",
        page="user",
        data=app_data,
        
        block=block,
        blocks=blocks,
        users=users,

        user_id=user_id,
        recommended_articles=recommended_articles,
        recent_articles=recent_articles
    )

@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        '404.html',
        page="404",
        data=app_data,
        articles=api.get_json({"type":"random_items"}),
    ), 404

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    return func.WsgiMiddleware(app.wsgi_app).handle(req, context)

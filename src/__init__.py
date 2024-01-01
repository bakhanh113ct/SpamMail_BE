from flask.json import jsonify
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Flask, config, redirect
import os
from src.auth import auth
from src.database import db
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config
from flask_cors import CORS, cross_origin
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from src.service.naive_bayes import NaiveBayesMultinomial, preprocess_text
from src.email import emails
from src.email import nb, vectorizer
# from ..src.service.naive_bayes import nb, preprocess_text

# nb = NaiveBayesMultinomial()

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    CORS(app, supports_credentials=True, origins='*')
    app.url_map.strict_slashes = False

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI'),
            # SQLALCHEMY_DATABASE_URI="postgresql://bakhanh113ct:uP7USI2ydhTb@ep-plain-recipe-68444027.ap-southeast-1.aws.neon.tech/emailspam?sslmode=require",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),

            SWAGGER={
                'title': "Bookmarks API",
                'uiversion': 3
            }
        )
    else:
        app.config.from_mapping(test_config)

    # db.app = app
    db.init_app(app)
    
    
    #init classifier
    trainDf = pd.read_csv('src/assets/spam.csv')
    # vectorizer = CountVectorizer()
    trainDf['Message'] = trainDf['Message'].apply(preprocess_text)
    X_train = vectorizer.fit_transform(trainDf["Message"]).toarray()
    y_train=trainDf['Category'].values
    nb.fit(X_train, y_train)

    #init route
    JWTManager(app)
    app.register_blueprint(auth)
    app.register_blueprint(emails)

    Swagger(app, config=swagger_config, template=template)


    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR

    return app

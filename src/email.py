from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import Email, db, User
from flasgger import swag_from
from sqlalchemy import delete, desc, asc
from flask_cors import CORS, cross_origin
from service.naive_bayes import NaiveBayesMultinomial
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import re
emails = Blueprint("emails", __name__, url_prefix="/api/v1/emails")

def preprocess_text(text):
    # Loại bỏ ký tự đặc biệt và chuyển đổi về chữ thường
    text = re.sub('[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

trainDf = pd.read_csv('../assets/spam.csv')
vectorizer = CountVectorizer()
trainDf['Message'] = trainDf['Message'].apply(preprocess_text)
X_train = vectorizer.fit_transform(trainDf["Message"]).toarray()
y_train=trainDf['Category'].values
nb = NaiveBayesMultinomial()
nb.fit(X_train, y_train)

def is_spam(email_content):
    cleaned_email = preprocess_text(email_content)
    email_vectorized = vectorizer.transform([cleaned_email]).toarray()
    prediction = nb.predict(email_vectorized)

    return prediction == "spam"
#
@emails.route('/test')
@cross_origin(origin='*')
def test():
    emails = Email.query.filter_by(
        user_id=1)

    return jsonify({"a": "b"})


@emails.get('/')
@cross_origin(origins='*', supports_credentials=True)
@jwt_required()
def getAllEmail():
    current_user = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    is_spam = request.args.get('is_spam', False, type=bool)

    print(is_spam)

    try:
        emails = Email.query.filter_by(
            receiver_id=current_user).order_by(desc('created_at')).paginate(page=page, per_page=per_page)

        if (emails.total == 0):
            return jsonify({"data": [], "msg": "No data in page {}".format(page)}), HTTP_200_OK

        data = []

        for email in emails.items:
            data.append({
                "id": email.id,
                "title": email.title,
                "body": email.body,
                "user_id": email.user_id,
                "receiver_id": email.receiver_id,
                "is_spam": email.is_spam,
                "sender_name": email.receiver.username,
                'time_send': email.created_at
            })

        meta = {
            "page": emails.page,
            'pages': emails.pages,
            'total_count': emails.total,
            'prev_page': emails.prev_num,
            'next_page': emails.next_num,
            'has_next': emails.has_next,
            'has_prev': emails.has_prev,
        }

        return jsonify({"data": data, "meta": meta}), HTTP_200_OK
    except:
        return jsonify({"data": [], "msg": "No data in page {}".format(page)}), HTTP_400_BAD_REQUEST


@emails.get('/nspam')
@cross_origin(origins='*', supports_credentials=True)
@jwt_required()
def getAllEmailNotSpam():
    current_user = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    is_spam = request.args.get('is_spam', False, type=bool)

    try:
        emails = Email.query.filter_by(
            receiver_id=current_user, is_spam=False).order_by(desc('created_at')).paginate(page=page, per_page=per_page)

        if (emails.total == 0):
            return jsonify({"data": [], "msg": "No data in page {}".format(page)}), HTTP_200_OK

        data = []

        for email in emails.items:
            data.append({
                "id": email.id,
                "title": email.title,
                "body": email.body,
                "user_id": email.user_id,
                "receiver_id": email.receiver_id,
                "is_spam": email.is_spam,
                "sender_name": email.receiver.username,
                'time_send': email.created_at
            })

        meta = {
            "page": emails.page,
            'pages': emails.pages,
            'total_count': emails.total,
            'prev_page': emails.prev_num,
            'next_page': emails.next_num,
            'has_next': emails.has_next,
            'has_prev': emails.has_prev,
        }

        return jsonify({"data": data, "meta": meta}), HTTP_200_OK

    except:
        return jsonify({"data": [], "msg": "No data in page {}".format(page)}), HTTP_400_BAD_REQUEST


@emails.get('/spam')
@cross_origin(origins='*', supports_credentials=True)
@jwt_required()
def getAllEmailSpam():
    current_user = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    is_spam = request.args.get('is_spam', False, type=bool)

    try:
        emails = Email.query.filter_by(
            receiver_id=current_user, is_spam=True).order_by(desc('created_at')).paginate(page=page, per_page=per_page)

        if (emails.total == 0):
            return jsonify({"data": [], "msg": "No data in page {}".format(page)}), HTTP_200_OK

        data = []

        for email in emails.items:
            data.append({
                "id": email.id,
                "title": email.title,
                "body": email.body,
                "user_id": email.user_id,
                "receiver_id": email.receiver_id,
                "is_spam": email.is_spam,
                "sender_name": email.receiver.username,
                'time_send': email.created_at
            })

        meta = {
            "page": emails.page,
            'pages': emails.pages,
            'total_count': emails.total,
            'prev_page': emails.prev_num,
            'next_page': emails.next_num,
            'has_next': emails.has_next,
            'has_prev': emails.has_prev,
        }

        return jsonify({"data": data, "meta": meta}), HTTP_200_OK

    except:
        return jsonify({"data": [], "msg": "No data in page {}".format(page)}), HTTP_400_BAD_REQUEST


@emails.get('/<email_id>')
@cross_origin(origins='*', supports_credentials=True)
@jwt_required()
def getOneEmail(email_id):
    email = Email.query.filter_by(id=email_id).first()

    if (email is None):
        return jsonify({
            'error': 'email_id is not exist'
        }), HTTP_400_BAD_REQUEST

    return jsonify({
        "message": "Success",
        "data": {
            "title": email.title,
            "body": email.body,
            "receiver_email": email.receiver.email,
            "created_at": email.created_at,
            "is_spam": email.is_spam,
            "sender_name": email.receiver.username,
            'time_send': email.created_at
        }
    }), HTTP_200_OK


@emails.route('/', methods=["POST"])
@cross_origin(origins='*', supports_credentials=True)
@jwt_required()
def create_email():
    current_user = get_jwt_identity()

    title = request.get_json().get('title', '')
    body = request.get_json().get('body', '')
    receiver_email = request.get_json().get('receiver_email', '')

    receiver_user = User.query.filter_by(email=receiver_email).first()

    if (receiver_user is None):
        return jsonify({
            'error': 'Email is not exist'
        }), HTTP_400_BAD_REQUEST

    email = Email(title=title, body=body, user_id=current_user,
                  receiver_id=receiver_user.id)
    db.session.add(email)
    db.session.commit()

    print(str(email))
    # email.toJSON()

    return jsonify({
        "message": "Create successful",
        "data": {
            "title": email.title,
            "body": email.body,
            "receiver_email": email.receiver.email,
            # "created_at": email.created_at,
            # "is_spam": email.is_spam
        }
    }), HTTP_200_OK


@emails.route('/<email_id>', methods=["DELETE"])
@cross_origin(origins='*', supports_credentials=True)
@jwt_required()
def delete_email(email_id):

    if (not email_id.isnumeric()):
        return jsonify({
            'error': 'Email_id is not numeric'
        }), HTTP_400_BAD_REQUEST

    row = Email.query.filter_by(id=email_id).delete()

    db.session.commit()

    print(row)
    if (row == 0):
        return jsonify({"message": "Delete fail"}), HTTP_409_CONFLICT

    return jsonify({"message": "Delete successful"}), HTTP_200_OK


@emails.route('/<email_id>', methods=["PUT"])
@cross_origin(origins='*', supports_credentials=True)
@jwt_required()
def update_email(email_id):
    if (not email_id.isnumeric()):
        return jsonify({
            'error': 'Email_id is not numeric'
        }), HTTP_400_BAD_REQUEST

    title = request.get_json().get('title', '')
    body = request.get_json().get('body', '')

    row = Email.query.filter_by(id=email_id).update(
        {'title': title, 'body': body})

    db.session.commit()

    if (row == 0):
        return jsonify({"message": "Update fail"}), HTTP_409_CONFLICT

    return jsonify({"message": "Update successful", "data": {
        "title": title,
        "body": body,
    }}), HTTP_200_OK

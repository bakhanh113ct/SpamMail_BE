from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import Email, db, User
from flasgger import swag_from
from sqlalchemy import delete, desc, asc
from flask_cors import CORS, cross_origin
from sklearn.feature_extraction.text import CountVectorizer
from src.service.naive_bayes import preprocess_text, NaiveBayesMultinomial
import pandas as pd
import requests
import schedule
from threading import Thread
# from src import train_model
import time
nb = NaiveBayesMultinomial()

emails = Blueprint("emails", __name__, url_prefix="/api/v1/emails")

vectorizer = CountVectorizer()

def merge_data_and_export_csv():
    # Đọc dữ liệu từ file CSV đã có vào DataFrame
    existing_data = pd.read_csv('src/assets/spam.csv')

    # Truy vấn dữ liệu từ cơ sở dữ liệu trong Flask
    flask_data = Email.query.all()

    # Chuyển đổi dữ liệu từ Flask thành DataFrame
    flask_data_df = pd.DataFrame([(data.is_spam, data.body) for data in flask_data], columns=['Category', 'Message'])
    flask_data_df.replace({True: 'spam', False: 'ham'}, inplace=True)
    # Gộp dữ liệu từ file CSV và dữ liệu từ Flask
    merged_data = pd.concat([existing_data, flask_data_df], ignore_index=True)

    # Lưu dữ liệu mới vào file CSV mới
    print('done merge')
    merged_data.to_csv('src/assets/merge_data.csv', index=False)

def train_model():
    merge_data_and_export_csv()
    trainDf = pd.read_csv('src/assets/merge_data.csv')
    # vectorizer = CountVectorizer()
    trainDf['Message'] = trainDf['Message'].apply(preprocess_text)
    X_train = vectorizer.fit_transform(trainDf["Message"]).toarray()
    y_train=trainDf['Category'].values
    print('done')
    nb.fit(X_train, y_train)

def fetch_data_from_api():
    # Gửi yêu cầu GET đến endpoint của Flask
    response = requests.get('http://127.0.0.1:5000/api/v1/emails/test')
    
    if response.status_code == 200:
        # Xử lý dữ liệu được trả về từ API endpoint
        data = response.json()
        print("Received data:", data)
    else:
        print("Failed to fetch data from the API")

def schedule_task():
    # fetch_data_from_api()
    # schedule.every().day.at("00:00").do(fetch_data_from_api)
    while True:
        # Gọi hàm fetch_data_from_api() sau mỗi 1 ngày
        fetch_data_from_api()
        time.sleep(24*3600)
        # schedule.run_pending()
        # time.sleep(1)

# schedule_task()
#start other thread
schedule_thread = Thread(target=schedule_task)
schedule_thread.start()

def spam_classifier(email_content):
    cleaned_email = preprocess_text(email_content)
    email_vectorized = vectorizer.transform([cleaned_email]).toarray()
    prediction = nb.predict(email_vectorized)
    # return True

    return prediction == "spam"



@emails.route('/test')
@cross_origin(origin='*')
def test():
    train_model()
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

@emails.get('/sended')
@cross_origin(origins='*', supports_credentials=True)
@jwt_required()
def getEmailSended():
    current_user = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    is_spam = request.args.get('is_spam', False, type=bool)

    try:
        emails = Email.query.filter_by(
            user_id=current_user, is_spam=False).order_by(desc('created_at')).paginate(page=page, per_page=per_page)

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

    is_spam = spam_classifier(body)
    print(is_spam)

    email = Email(title=title, body=body, user_id=current_user,
                  receiver_id=receiver_user.id, is_spam=is_spam)
    # db.session.add(email)
    # db.session.commit()

    print(str(email))
    # email.toJSON()

    return jsonify({
        "message": "Create successful",
        "data": {
            "title": email.title,
            "body": email.body,
            # "receiver_email": email.receiver.email,
            # "created_at": email.created_at,
            "is_spam": email.is_spam
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


#Mark spam or not
@emails.route('/<email_id>', methods=["PUT"])
@cross_origin(origins='*', supports_credentials=True)
@jwt_required()
def update_email(email_id):
    if (not email_id.isnumeric()):
        return jsonify({
            'error': 'Email_id is not numeric'
        }), HTTP_400_BAD_REQUEST

    is_spam = request.args.get('isSpam', False, type=is_it_true)
    print(is_spam)
    # title = request.get_json().get('title', '')
    # body = request.get_json().get('body', '')

    row = Email.query.filter_by(id=email_id).update(
        {'is_spam': is_spam})

    db.session.commit()

    if (row == 0):
        return jsonify({"message": "Update fail"}), HTTP_409_CONFLICT
    # return jsonify({"message": "Update successful", "data": {
    #     "title": 'title',
    #     "body": 'body',
    # }}), HTTP_200_OK

    return jsonify({"message": "Update successful", "data": {
        "is_spam": is_spam,
    }}), HTTP_200_OK

def is_it_true(value):
  return value.lower() == 'true'
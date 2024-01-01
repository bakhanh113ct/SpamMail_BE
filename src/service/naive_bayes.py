import numpy as np
import re

def preprocess_text(text):
    # Loại bỏ ký tự đặc biệt và chuyển đổi về chữ thường
    text = re.sub('[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

class NaiveBayesMultinomial:
    def fit(self, X, y):
        # Số lượng mẫu, số đặc trưng
        n_samples, n_features = X.shape
        # Mảng các duy nhất phân lớp (Spam, Ham)
        self.classes = np.unique(y)
        # Số lượng phân lớp
        n_classes = len(self.classes)

        # Tính xác suất tiên nghiệm P(Y = c)
        self.class_probs = np.zeros(n_classes) # Tạo một mảng có độ dài bằng số lượng lớp
        for i, c in enumerate(self.classes): # i là chỉ số của lớp và c là giá trị của lớp đó.
            self.class_probs[i] = np.sum(y == c) / float(n_samples)

        # Tính xác suất của các đặc trưng dựa trên mỗi lớp P(X_i = x | Y = c)
        self.feature_probs = np.zeros((n_classes, n_features)) # Tạo một ma trận có kích thước (n_classes, n_features) chứa xác suất của các đặc trưng dựa trên từng lớp.
        for i, c in enumerate(self.classes):
            X_c = X[y == c] # Chứa các mẫu từ tập dữ liệu X mà nhãn tương ứng y là c.
            self.feature_probs[i] = (np.sum(X_c, axis=0) + 1) / (np.sum(X_c) + n_features) # axis = 0 để tính theo cột

    def predict(self, X):
        posteriors = []
        for j, c in enumerate(self.classes):
            prior = self.class_probs[j]
            # Tính tích các xác suất đặc trưng
            likelihood = np.prod(self.feature_probs[j]**X)
            posterior = prior * likelihood
            posteriors.append(posterior)

        # Chọn lớp có xác suất cao nhất
        prediction = self.classes[np.argmax(posteriors)]
        return prediction

    def predict_proba(self, X):
        probabilities = []
        posteriors = []
        for j, c in enumerate(self.classes):
            prior = self.class_probs[j]
            # Tính tích các xác suất đặc trưng
            likelihood = np.prod(self.feature_probs[j]**X)
            posterior = prior * likelihood
            posteriors.append(posterior)


        # Chuyển posteriors thành xác suất
        prob = posteriors / np.sum(posteriors)
        probabilities.append(prob)

        return probabilities


# trainDf = pd.read_csv('emails.csv')
# trainDf1 = pd.read_csv('../assets/spam.csv')
# X_train = trainDf.iloc[:, 1:-1].values
# y_train = trainDf['Prediction'].values
# print(X_train)
# def preprocess_text(text):
#     # Loại bỏ ký tự đặc biệt và chuyển đổi về chữ thường
#     text = re.sub('[^a-zA-Z\s]', '', text)
#     text = text.lower()
#     return text
# text_column = 'Message'  # Thay 'text_column_name' bằng tên cột chứa dữ liệu văn bản
# label_column = 'Category'

# X_train, X_test, y_train, y_test = train_test_split(trainDf[text_column], trainDf[label_column], test_size=0.2, random_state=42)

# Khởi tạo và sử dụng CountVectorizer để chuyển đổi văn bản thành ma trận tần suất xuất hiện của từng từ
# vectorizer = CountVectorizer()
# trainDf1['Message'] = trainDf1['Message'].apply(preprocess_text)
# X_train1 = vectorizer.fit_transform(trainDf1["Message"]).toarray()
# y_train1=trainDf1['Category'].values
# X_test_transformed = vectorizer.transform(X_test)
# print(vectorizer.get_feature_names_out())
# print(X_train_transformed.toarray())
# print(y_train)
# email_content = "dobmeos with hgh my energy level has gone up ! stukm"
# email_words = email_content.split()

# # # Khởi tạo một mảng để lưu trữ tần suất xuất hiện của từng đặc trưng trong email
# frequency_array = np.zeros(len(trainDf.columns[1:-1]))

# # # Duyệt qua từng đặc trưng trong file CSV và kiểm tra tần suất xuất hiện trong email
# for idx, feature in enumerate(trainDf.columns[1:-1]):
#     # Đếm số lần xuất hiện của đặc trưng trong email
#     frequency = email_words.count(feature)

#     # Lưu trữ tần suất vào mảng
#     frequency_array[idx] = frequency


# X_test = np.array(frequency_array)

# # Huấn luyện và dự đoán
# nb = NaiveBayesMultinomial()
# nb.fit(X_train, y_train)

# X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.25, random_state=42)

# X_train1, X_test1, y_train1, y_test1 = train_test_split(X_train1, y_train1, test_size=0.2, random_state=42)

# # Khởi tạo và huấn luyện mô hình NaiveBayesMultinomial trên tập huấn luyện
# nb = NaiveBayesMultinomial()
# nb.fit(X_train1, y_train1)

# nb.predict_proba()

# Dự đoán nhãn cho tập dữ liệu kiểm tra
# y_pred_test = [nb.predict(sample) for sample in X_test1]

# Tính toán accuracy trên tập dữ liệu kiểm tra
# accuracy = accuracy_score(y_test1, y_pred_test)
# print(f"Tỷ lệ đúng của mô hình trên tập dữ liệu kiểm tra: {accuracy}")

# def is_spam(email_content):
#     cleaned_email = preprocess_text(email_content)
#     email_vectorized = vectorizer.transform([cleaned_email]).toarray()
#     prediction = nb.predict(email_vectorized)
#     return prediction == "spam"

# print(is_spam("hello world world"))

# # predictions = nb.predict(X_test)

# # print("Dự đoán:", predictions)
# labels = ['Accuracy']
# values = [accuracy]

# plt.figure(figsize=(6, 4))
# plt.bar(labels, values, color='skyblue')
# plt.ylabel('Accuracy')
# plt.title('Accuracy of Naive Bayes Model on Test Data')
# plt.ylim(0, 1)  # Giới hạn trục y từ 0 đến 1
# plt.show()
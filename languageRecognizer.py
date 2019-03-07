import requests
import numpy as np
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB


class LanguageRecognizer:
    def __init__(self, clf=MultinomialNB, tf_transformer=TfidfTransformer, vectorizer=CountVectorizer):
        self.clf = clf
        self.lang_tuple = None
        self.session = requests.Session()
        self.text_dict = {}
        self.tf_transformer = tf_transformer(use_idf=False)
        self.vectorizer = vectorizer
        self.X_test = None
        self.X_train = None
        self.y_test = None
        self.y_train = None

    def log_in(self, login, password):
        r = self.session.get("https://github.com/login")
        soup = BeautifulSoup(r.text, "html.parser")
        inputs = soup.find_all("input")
        auth_token = inputs[1]["value"]
        payload = {
            'login': login,
            'password': password,
            'authenticity_token': auth_token,
        }
        self.session.post("https://github.com/session", params=payload)
        print('Logged In')

    def get_raw_from_link(self, link):
        link = link.replace("/blob/", "/raw/")
        r = self.session.get("https://github.com{}".format(link))
        return r.text

    def get_data(self, lang_tuple=(("python", "py"), ("java", "java"), ("cpp", "cpp")),
                 data_size=100):
        self.lang_tuple = lang_tuple
        for lang, ext in self.lang_tuple:
            texts = []
            for i in range(1, data_size+1):
                url = "https://github.com/search?p={}&q={}+in%3Apath+extension%3A{}&type=Code".format(str(i), lang, ext)
                r = self.session.get(url)
                print(r.status_code)
                soup = BeautifulSoup(r.text, "html.parser")
                links = soup.select('a[href$=".{}"]'.format(ext))
                texts.extend([self.get_raw_from_link(link["href"]) for link in links[::2]])
            self.text_dict[lang] = texts
        print('Done')

    def preprocess_data(self, test_set_size=0.2):
        y = np.array([len(v) * [k] for v, k in self.text_dict.items()])
        flattened_texts = [text for category in self.text_dict.values() for text in category]
        labeled_texts = list(zip(flattened_texts, y))
        np.random.shuffle(labeled_texts)
        X, y = zip(*labeled_texts)
        size = int(len(X) * test_set_size)
        self.X_train = X[:size]
        self.X_test = X[size:]
        self.y_train = y[:size]
        self.y_test = y[size:]
        print('Done')

    def fit(self):
        X_train = self.vectorizer.fit_transform(self.X_train)
        X_train = self.tf_transformer.fit(X_train).transform(X_train)
        self.clf.fit(X_train, self.y_train)
        print("Classifier trained")

    def test(self):
        X_test = self.vectorizer.transform(self.X_test)
        X_test = self.tf_transformer.transform(X_test)
        predictions = self.clf.predict(X_test)
        print("Accuracy score = {}".format(accuracy_score(self.y_test, predictions)))

    def predict(self, filename):
        with open(filename) as f:
            new_text = [f.read()]
        X_new = self.vectorizer.transform(new_text)
        X_new = self.tf_transformer.transform(X_new)
        predicted = self.clf.predict(X_new)
        print(predicted)

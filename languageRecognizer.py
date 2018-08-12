import requests
import numpy as np

from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

class LanguageRecognizer():
    def __init__(self):
        self.session = requests.Session()

    def log_in(self, login, password):
        r = self.session.get("https://github.com/login")
        soup = BeautifulSoup(r.text, "html.parser")
        inputs = soup.find_all("input")
        auth_token = inputs[1]["value"]
        payload = {'login': login,
                   'password': password,
                   'authenticity_token': auth_token}
        r = self.session.post("https://github.com/session", params=payload)

    def get_data(self, langs=[["python","py"],["java","java"],["cpp","cpp"]],
                 data_size=100):
        self.langs = langs
        texts = []
        for j in range(len(langs)):
            texts.append([])
            for i in range(1,data_size+1):
                url = ("https://github.com/search?p={}&q={}+in%3Apath+extension%3A{}&type=Code").format(str(i),
                                                                                                        langs[j][0],
                                                                                                        langs[j][1])
                r = self.session.get(url)
                
                soup = BeautifulSoup(r.text,"html.parser")
                links = soup.select('a[href$=".{}"]'.format(langs[j][1]))
                links = [link["href"] for link in links[::2]]
                for link in links:
                    link = link.replace("/blob/","/raw/")
                    r = self.session.get("https://github.com{}".format(link))
                    texts[j].append(r.text)
        self.texts = texts

    def preprocess_data(self, test_set_size=0.2):
        y = []
        for i in range(len(self.langs)):
            y += len(self.texts[i])*[self.langs[i][0]]
        y = np.array(y)
        flattened_texts = [text for category in self.texts for text in category]
        labeled_texts = list(zip(flattened_texts, y))
        np.random.shuffle(labeled_texts)
        X, y = zip(*labeled_texts)
        size = int(len(X)*test_set_size)
        self.X_train = X[:size]
        self.X_test = X[size:]
        self.y_train = y[:size]
        self.y_test = y[size:]

    def fit(self):
        vectorizer = CountVectorizer()
        X_train = vectorizer.fit_transform(self.X_train)
        tf_transformer = TfidfTransformer(use_idf=False).fit(X_train)
        X_train = tf_transformer.transform(X_train)
        clf = MultinomialNB().fit(X_train, self.y_train)
        print("Classifier trained")
        self.vectorizer = vectorizer
        self.tf_transformer = tf_transformer
        self.clf = clf

    def calc_acc(self, arr1, arr2):
        return sum([i == j for i,j in zip(arr1, arr2)])/float(len(arr1))

    def test(self):
        X_test = self.vectorizer.transform(self.X_test)
        X_test = self.tf_transformer.transform(X_test)
        predictions = self.clf.predict(X_test)
        print("Accuracy score = {}".format(self.calc_acc(predictions,
                                                         self.y_test)))

    def predict(self, filename):
        with open(filename) as f:
            new_text = [f.read()]
        X_new = self.vectorizer.transform(new_text)
        X_new = self.tf_transformer.transform(X_new)
        predicted = self.clf.predict(X_new)
        print(predicted)
        

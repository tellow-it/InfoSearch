import re
import nltk

nltk.download("stopwords")
from nltk.corpus import stopwords
import pymorphy3
import pandas as pd
from collections import defaultdict
from string import punctuation

morph = pymorphy3.MorphAnalyzer()
russian_stopwords = stopwords.words("russian")


class InvertedIndexMorph:
    def __init__(self):
        self.index = defaultdict(set)
        self.doc_ids = set()
        self.max_doc_id = max(self.doc_ids) if self.doc_ids else None

    def tokenize(self, doc):
        bad_words = [
            "или", "изза", "для", "нем", "еще", "либо",
            "его", "её", "при", "также", "так", "это", "этого",
            "interfaxru", "москва", "июня", "июнь", "май", "мая"
        ]
        text = doc.lower()
        text = re.sub(r"[^а-яА-ЯёЁa-zA-Z\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        words = text.split()
        words = [word for word in words if len(word) > 2 and word not in bad_words]
        words = [word for word in words if word not in russian_stopwords]
        words = [morph.parse(word)[0].normal_form for word in words]
        return words

    def add_doc(self, doc_id, doc):
        if doc_id in self.doc_ids:
            raise ValueError(f"Doc with doc_id: {doc_id} already in index")
        tokenized_doc = self.tokenize(doc)
        for word in tokenized_doc:
            self.index[word].add(doc_id)

    def build(self, docs):
        for doc_id, doc in enumerate(docs):
            self.add_doc(doc_id, doc)

    def search(self, query):
        words = self.tokenize(query)
        print(words)
        if not words:
            return set(), set()

        # ищем документы в которых есть все слова из запроса
        common_docs = self.index.get(words[0], set()).copy()
        for word in words[1:]:
            common_docs &= self.index.get(word, set())

        # ищем документы в которых хоть одно слово упоминается
        any_docs = set()
        for word in words:
            any_docs |= self.index.get(word, set())

        return common_docs, any_docs


if __name__ == "__main__":
    df = pd.read_csv("hm_01/interfax_business_iter_5.csv")
    df = df.dropna()
    df = df.drop_duplicates(keep="first")

    docs = df["text"].tolist()

    inv_index = InvertedIndexMorph()
    inv_index.build(docs)

    q_1 = (
        "Акционеры на собрании"
    )
    # output: ({0, 513, 386, 387, 384, 396, 424, 429, 432, 309, 438, 55, 445, 71, 79, 84, 85, 87, 349, 482, 488, 494, 240, 113,
    #   241, 115, 370},
    #  {0, 513, 515, 8, 13, 526, 15, 273, 23, 541, 288, 291, 292, 293, 309, 55, 71, 78, 79, 339, 84, 85, 87, 343, ...})
    print(inv_index.search(q_1))
    q_2 = (
        "Акционеры банка на собрании объявили о закрытии банка в связи с невозможностью выплат по вкладам"
    )
    # output: (set(),
    #  {0, 3, 5, 6, 7, 8, 9, 10, 13, 14, 15, 18, 22, 23, 24, 27, 30, 31, 34, 36, 37, 38, 40, 42, 43, 46, 48, 49, 53, 55,...}
    print(inv_index.search(q_2))
    q_3 = (
        "рики и морти"  # проверка поиска информации, которой нет в индексе
    )
    # output: (set(), {156})
    print(inv_index.search(q_3))
    q_4 = (
        ""  # проверка на пустую строку
    )
    print(inv_index.search(q_4))
    # output: (set(), set())
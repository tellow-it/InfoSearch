import re

import pandas as pd
from collections import defaultdict


class InvertedIndex:
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

    inv_index = InvertedIndex()
    inv_index.build(docs)

    q_1 = (
        "Акционеры на собрании"
    )
    print(inv_index.search(q_1))
    # output: ({0, 384, 482, 71, 424, 488, 240, 241, 370, 445}, {0, 384, 513, 71, 396, 79, 273, 84, 87, 349, 351, 161, 482,
    # 291, 424, 488, 240, 241, 370, 435, 496, 372, 432, 445})
    q_2 = (
        "Акционеры банка на собрании объявили о закрытии банка в связи с невозможностью выплат по вкладам"
    )
    # output: (set(), {0, 513, 514, 3, 515, 6, 7, 8, 518, 519, 523, 9, 526, 527, 15, 528, 532, 22, 535, 24, 536, 30, 31, 544,
    # 34, 36, 38, 40, 42, 43, 46, 48, 55, 63, 64, 66, 71, 77, 79, 81, 83, 84, 86, 87, 90, 96, 97, 109, 110, 114, 115,
    # 118, 120, 122, 129, 133, 134, 144, 145, 147, 151, 157, 159, 161, 166, 168, 169, 170, 175, 178, 179, 183, 186,
    # 193, 200, 205, 210, 211, 219, 225, 228, 232, 236, 239, 240, 241, 251, 252, 260, 261, 267, 271, 272, 273, 274,
    # 275, 277, 278, 279, 280, 285, 289, 290, 291, 293, 303, 304, 315, 317, 320, 327, 330, 332, 337, 338, 343, 346,
    # 349, 351, 353, 355, 356, 370, 372, 374, 380, 384, 391, 395, 396, 407, 416, 419, 422, 423, 424, 426, 432, 435,
    # 436, 439, 445, 447, 450, 452, 455, 457, 462, 464, 465, 470, 475, 477, 478, 480, 482, 483, 485, 488, 489, 490,
    # 491, 493, 494, 496, 505, 506, 507, 509, 510, 511})
    print(inv_index.search(q_2))
    q_3 = (
        "рики и морти" # проверка поиска информации, которой нет в индексе
    )
    # output: (set(), set())
    print(inv_index.search(q_3))
    q_4 = (
        "" # проверка на пустую строку
    )
    print(inv_index.search(q_4))
    # output: (set(), set())

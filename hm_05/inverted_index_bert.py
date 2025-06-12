import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd


class InvertedIndexBert:
    def __init__(self, model_name="DeepPavlov/rubert-base-cased-sentence"):
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.doc_vectors = None

    def build(self, documents):
        self.documents = documents
        self.doc_vectors = self.model.encode(documents, convert_to_tensor=False, show_progress_bar=True)

    def search(self, query, top_k=10, min_cos_sim=0.4):
        query_vector = self.model.encode([query])[0]
        similarities = cosine_similarity([query_vector], self.doc_vectors)[0]
        top_doc_ids = np.argsort(similarities)[::-1][:top_k]
        return [
            (int(doc_id), round(float(similarities[doc_id]), 3))
            for doc_id in top_doc_ids if similarities[doc_id] > min_cos_sim
        ]


if __name__ == "__main__":
    df = pd.read_csv("hm_01/interfax_business_iter_5.csv")
    df = df.dropna()
    df = df.drop_duplicates(keep="first")

    docs = df["text"].tolist()

    inv_index = InvertedIndexBert()
    inv_index.build(docs)

    q_1 = (
        "Акционеры на собрании"
    )
    print(q_1)
    print(inv_index.search(q_1))
    # [(94, 0.511), (81, 0.494), (98, 0.484), (55, 0.481), (396, 0.481), (62, 0.472),
    # (14, 0.469), (118, 0.46), (371, 0.46), (246, 0.46)]
    q_2 = (
        "Акционеры банка на собрании объявили о закрытии банка в связи с невозможностью выплат по вкладам"
    )
    print(q_2)
    print(inv_index.search(q_2))
    # [(27, 0.861), (84, 0.821), (71, 0.82), (115, 0.818), (113, 0.817),
    # (432, 0.808), (360, 0.806), (429, 0.805), (83, 0.8), (273, 0.794)]
    q_3 = (
        "рики и морти"  # проверка поиска информации, которой нет в индексе
    )
    print(q_3)
    # [(1, 0.454), (246, 0.444), (56, 0.418), (107, 0.41), (118, 0.41), (96, 0.404), (31, 0.403), (523, 0.401)]
    print(inv_index.search(q_3))
    q_4 = (
        ""  # проверка на пустую строку
    )
    print(q_4)
    print(inv_index.search(q_4))
    # output: []

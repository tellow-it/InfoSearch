import re
import pandas as pd


def preprocess_text(text):
    bad_words = [
        "или", "изза", "для", "нем", "еще", "либо",
        "его", "её", "при", "также", "так", "это", "этого",
        "interfaxru", "москва", "июня", "июнь", "май", "мая"
    ]
    text = text.lower()
    text = re.sub(r"[^а-яА-ЯёЁa-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()
    words = [word for word in words if len(word) > 2 and word not in bad_words]
    return words


def generate_ngrams(words, n: int = 2):
    if n < 2:
        raise ValueError("n must be minimum 2")
    ngrams = []
    for i in range(len(words) - n + 1):
        phrase = tuple(words[i:i + n])
        ngrams.append(phrase)
    return ngrams


def count_ngrams(ngrams):
    freq = dict()
    for phrase in ngrams:
        if phrase in freq:
            freq[phrase] += 1
        else:
            freq[phrase] = 1
    return freq


def find_top_ngrams(freq_dict, min_count: int = 2, top_n: int = 5):
    filtered = [(phrase, count) for phrase, count in freq_dict.items() if count >= min_count]
    sorted_ngrams = sorted(filtered, key=lambda x: x[1], reverse=True)
    return dict(sorted_ngrams[:top_n])


def pipeline_searching_top_ngrams(text: str, n: int = 2, min_count: int = 2, top_n: int = 5):
    words = preprocess_text(text)
    ngrams = generate_ngrams(words, n)
    ngram_freq = count_ngrams(ngrams)
    return find_top_ngrams(ngram_freq, min_count, top_n)


def search_top_ngrams(ngrams: list, top_ngrams: dict):
    ngrams_in_top = []
    for ngram in ngrams:
        if ngram in top_ngrams:
            ngrams_in_top.append(ngram)
    return ngrams_in_top


if __name__ == "__main__":
    df = pd.read_csv("hm_01/interfax_business_iter_5.csv")
    df = df.dropna()
    df = df.drop_duplicates(keep="first")

    df["tokens"] = df["text"].apply(preprocess_text)
    df["bigrams"] = df["tokens"].apply(lambda x: generate_ngrams(x, n=2))
    df["trigrams"] = df["tokens"].apply(lambda x: generate_ngrams(x, n=3))

    all_tokens = []

    for tokens in df["tokens"].dropna():
        if isinstance(tokens, list):
            all_tokens += tokens

    bigrams = generate_ngrams(all_tokens, 2)
    bigram_freq = count_ngrams(bigrams)
    top_bigram = find_top_ngrams(bigram_freq, min_count=2, top_n=20)

    trigrams = generate_ngrams(all_tokens, 3)
    trigram_freq = count_ngrams(trigrams)
    top_trigram = find_top_ngrams(trigram_freq, min_count=2, top_n=20)

    df["top_bigram_in_text"] = df["bigrams"].apply(lambda x: search_top_ngrams(x, top_bigram))
    df["top_trigram_in_text"] = df["trigrams"].apply(lambda x: search_top_ngrams(x, top_trigram))

    df.to_csv("hm_02/interfax_business_top_ngrams.csv")

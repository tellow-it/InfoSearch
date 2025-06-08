import re
import pandas as pd


def preprocess_text(text):
    bad_words = [
        "или", "изза", "для", "нем", "еще", "либо",
        "его", "её", "при", "также", "так", "это", "этого"
    ]
    text = text.lower()
    text = re.sub(r"[^а-яА-ЯёЁa-zA-Z\s]", "", text)
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
    return sorted_ngrams[:top_n]


def find_top_ngrams_df(text: str, n: int = 2, min_count: int = 2, top_n: int = 5):
    words = preprocess_text(text)
    ngrams = generate_ngrams(words, n)
    ngram_freq = count_ngrams(ngrams)
    return find_top_ngrams(ngram_freq, min_count, top_n)


if __name__ == "__main__":
    df = pd.read_csv("hm_01/interfax_business_iter_5.csv")
    df = df.dropna()
    df = df.drop_duplicates(keep="first")

    df["top_bigrams"] = df["text"].apply(lambda x: find_top_ngrams_df(x, n=2, min_count=2, top_n=5))
    df["top_trigrams"] = df["text"].apply(lambda x: find_top_ngrams_df(x, n=3, min_count=2, top_n=5))

    df.to_csv("hm_02/interfax_business_top_ngrams.csv")

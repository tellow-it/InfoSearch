import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.interfax.ru"
CATEGORY = "business"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"
NUM_ITERATION = 10
OUTPUT_FILENAME = "hm_01/interfax_business_iter_5.csv"


def extract_articles(soup: BeautifulSoup) -> list[dict]:
    articles = []

    for block_class in ["timeline__text", "timeline__group", "timeline__photo"]:
        for block in soup.find_all("div", class_=block_class):
            for entry in block.find_all("div") if block_class == "timeline__group" else [block]:
                a_tag = entry.find("a")
                time_tag = entry.find("time")
                if not (a_tag and time_tag):
                    continue
                article_time = time_tag.get("datetime")
                articles.append(
                    {
                        "article_time_str": article_time,
                        "article_time_datetime": datetime.datetime.strptime(article_time, DATETIME_FORMAT),
                        "link": f"{BASE_URL}{a_tag.get('href')}",
                        "title": a_tag.get("title")
                    }
                )
    return articles


def get_news_articles(request_params: dict = None) -> list[dict]:
    resp = requests.get(f"{BASE_URL}/{CATEGORY}", params=request_params)
    soup = BeautifulSoup(resp.text, "html.parser")
    return extract_articles(soup)


def get_article_info(url: str):
    try:
        resp = requests.get(url)
        resp.encoding = 'cp1251'
        soup = BeautifulSoup(resp.text, "html.parser")
        article_block = soup.find("article")
        return article_block.text
    except Exception as err:
        print(f"Problems with parsing {url}")
        return None


if __name__ == "__main__":
    all_articles = sorted(get_news_articles(), key=lambda x: x["article_time_datetime"], reverse=True)

    for i in range(1, NUM_ITERATION + 1):
        if not all_articles:
            break
        oldest_date = all_articles[-1]["article_time_str"]
        params = {"a": "timeline", "dt": oldest_date}
        print(f"Iter {i}, params: {params}, current total: {len(all_articles)}")

        new_articles = get_news_articles(params)
        if new_articles:
            all_articles += new_articles
            all_articles = sorted(all_articles, key=lambda x: x["article_time_datetime"], reverse=True)

    print(f"Total articles collected: {len(all_articles)}")

    for idx, article in enumerate(all_articles):
        print(f"{idx} Parse: {article["link"]}")
        article_text = get_article_info(article["link"])
        article["text"] = article_text

    pd.DataFrame(all_articles).to_csv(OUTPUT_FILENAME, encoding="utf-8", index=False)

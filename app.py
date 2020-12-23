import streamlit as st
from streamlit_observable import observable
import pandas as pd
import numpy as np
from enum import Enum
import requests
import json
import datetime

@st.cache
def get_wiki_data():
    df = pd.DataFrame(columns=["date", "article", "views", "rank"])
    dates = pd.date_range(datetime.date(2020, 3, 1), periods=50).tolist()
    for d in dates:
        response = requests.get(
            "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/desktop/{year}/{month}/{day}"
                .format(year=d.year, month=d.strftime("%m"), day=d.strftime("%d"))
        )
        day_data = response.json()
        articles = day_data.get("items")[0].get("articles")
        articles = list(map(lambda a: {
            "article": a.get("article"),
            "views": a.get("views"),
            "rank": a.get("rank"),
            "date": d.strftime("%Y-%m-%d")
        }, articles))

        def filter_articles(d):
            if d.get("article") == "Main_Page":
                return False
            if "Special:" in d.get("article"):
                return False
            return d.get("rank") < 50

        articles = list(filter(filter_articles, articles))
        df = df.append(articles, ignore_index=True)
    return df.rename(columns={
        "article": "name",
        "views": "value"
    })
df_wiki = get_wiki_data()

observable("Wiki Bar Chart Race",
    notebook="d/9bbcce8f2f6834d7",
    redefine={
        "rawData": df_wiki.to_csv(),
        "duration": 200,
        "n": 10
    },
    targets=["chart", "viewof keyframe", "update"],
    hide=["update"]
)

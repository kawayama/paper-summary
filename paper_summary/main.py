import configparser
import csv
import os
import random
import time

import arxiv
import openai
import sqlite_utils

from paper_summary.utils import notifications

DAILY_PAPER_NUM = 3

inifile = configparser.ConfigParser()
inifile.read('./config.ini', 'utf-8')
openai.api_key = inifile.get('openai', 'api_key')


def post_paper_summary():
    query_list = _get_query_list()
    history_text_list = _get_existed_title_list()

    for query in query_list:
        daily_paper_list = random.sample([
            item for item in _get_paper_result_list(query)
            if item not in history_text_list
        ], k=DAILY_PAPER_NUM)

        daily_paper_info_list = [_summarize_paper(
            title_en=item.title,
            summary=item.summary,
            url=item.entry_id,
            published_dt=item.published,
        ) for item in daily_paper_list]

        for info in daily_paper_info_list:
            # 10回連続で取得失敗の場合はスキップ
            if info is None:
                continue

            notifications.notify_to_slack(
                f"発行日: {info['published_date_str']}\n{info['url']}\n{info['title_en']}\n{info['title_jpn']}\n{info['summary']}",
                channel='paper'
            )
            _add_title_to_db(info['title_en'])


def _get_existed_title_list():
    db = sqlite_utils.Database(os.path.join('data', 'history.db'))

    if 'arxiv_paper' in db.table_names():
        return [item['title'] for item in db.query(f"SELECT * FROM arxiv_paper")]
    else:
        return []


def _add_title_to_db(title):
    db = sqlite_utils.Database(os.path.join('data', 'history.db'))
    db['arxiv_paper'].insert({'title': title})


def _get_query_list():
    with open(os.path.join('data', 'query_list.txt'), 'r', encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f if line is not None]


def _get_paper_result_list(query):
    search = arxiv.Search(
        query=query,
        max_results=50,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    return list(search.results())


def retry_wrapper(func):
    def wrapper(*args, **kwargs):
        for _ in range(10):
            try:
                value = func(*args, **kwargs)
                break
            except openai.error.RateLimitError:
                print('retry: sleep 60s')
                time.sleep(60)
                continue
        else:
            print('failed')
            return None
        
        print('pass')
        return value
    return wrapper


@retry_wrapper
def _summarize_paper(title_en, summary, url, published_dt):
    system = """与えられた論文の要点を3点のみでまとめ、以下のフォーマットで日本語で出力してください。```
    タイトルの日本語訳
    ・要点1
    ・要点2
    ・要点3
    ```"""

    not_newlines_summary = ''.join(summary.split('\n'))
    text = f"title: {title_en}\nbody: {not_newlines_summary}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': text},
        ],
        temperature=0.25,
    )

    summary = response['choices'][0]['message']['content']
    title_jpn, *body = summary.split('\n')
    body = '\n'.join(body)

    return {
        'title_en': title_en,
        'title_jpn': title_jpn,
        'url': url,
        'published_date_str': published_dt.strftime("%Y-%m-%d %H:%M:%S"),
        'summary': body,
    }


if __name__ == '__main__':
    post_paper_summary()

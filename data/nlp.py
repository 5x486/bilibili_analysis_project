"""NLP: jieba segmentation + SnowNLP sentiment analysis."""
import pandas as pd
import jieba
from snownlp import SnowNLP
from data.data_clean import get_engine


def analyze_danmaku_sentiment():
    """Load danmaku data, perform sentiment analysis, save to CSV and SQL."""
    engine = get_engine()
    df = pd.read_sql_table('danmakudata', engine)

    if df.empty:
        print("No danmaku data to analyze.")
        return df

    stopwords = set()
    try:
        with open('data/stop_words', 'r', encoding='utf-8') as f:
            stopwords = set(line.strip() for line in f)
    except FileNotFoundError:
        pass

    scores = []
    segmented_list = []

    for text in df['content']:
        text = str(text) if text else ""
        words = jieba.cut(text)
        filtered = [w for w in words if w not in stopwords and w.strip()]
        segmented_list.append(' '.join(filtered))
        filtered_text = ' '.join(filtered)
        if not filtered_text.strip():
            scores.append(0.5)
        else:
            s = SnowNLP(filtered_text)
            scores.append(s.sentiments)

    df['score'] = scores
    df['segmented'] = segmented_list

    df.to_csv('data/nlp_result.csv', index=False, encoding='utf-8-sig')
    df.to_sql('nlp_result', engine, if_exists='replace', index=False)

    return df


if __name__ == '__main__':
    analyze_danmaku_sentiment()

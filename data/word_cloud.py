"""Generate word cloud data from segmented danmaku text."""
import re
from collections import Counter
import pandas as pd


def get_word_frequencies(csv_path='data/nlp_result.csv', top_n=200):
    """Extract Chinese words and return frequency list of [word, count] pairs."""
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return [['暂无数据', 1]]

    chinese_pattern = re.compile(r'^[一-鿿]+$')
    all_words = []

    for text in df.get('segmented', []):
        if isinstance(text, str):
            words = text.strip().split()
            chinese_words = [w for w in words if chinese_pattern.fullmatch(w)]
            all_words.extend(chinese_words)

    word_counts = Counter(all_words)
    return [[w, c] for w, c in word_counts.most_common(top_n)]


if __name__ == '__main__':
    freqs = get_word_frequencies()
    print(f"Extracted {len(freqs)} words for word cloud.")

import pandas as pd
import re
from tqdm import tqdm
import os


def preprocess(input_path, output_path):
    print("<--------------------------Running 2 -------------------------->")
    df = pd.read_parquet(input_path)

    def extract_tickers(text):
        if not text:
            return []
        return re.findall(r"\$[A-Za-z]{1,5}", text)

    def merge_tickers(row):
        tickers = extract_tickers(row['title']) + extract_tickers(row['body'])
        tickers = list(set([t.upper().replace('$', '') for t in tickers]))
        return tickers

    tqdm.pandas(desc="Extracting tickers")
    df['tickers'] = df.progress_apply(merge_tickers, axis=1)
    df['content'] = df['title'].fillna('') + "\n\n" + df['body'].fillna('')
    df_exploded = df.explode('tickers')
    df_exploded = df_exploded[df_exploded['tickers'].notna()]
    df_final = df_exploded[['tickers', 'score',
                            'num_comments', 'content', 'comments', 'created_utc']]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_final.to_parquet(output_path, engine="pyarrow", index=False)

    print(
        f"Preprocessed dataset ready for LLM: {len(df_final)} rows saved to {output_path}")

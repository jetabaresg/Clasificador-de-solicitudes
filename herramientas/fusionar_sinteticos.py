import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'Sistema_clasificador' / 'data'
ORIG = DATA_DIR / 'dataset_bitext_final_limpio.csv'
SYN = DATA_DIR / 'intents_synthetic_samples.csv'
INTENTS = DATA_DIR / 'tabla_intenciones.csv'
OUT = DATA_DIR / 'dataset_with_synthetic.csv'


def merge():
    df_orig = pd.read_csv(ORIG, encoding='utf-8', low_memory=False)
    df_syn = pd.read_csv(SYN, encoding='utf-8', low_memory=False)
    df_int = pd.read_csv(INTENTS, encoding='utf-8-sig', low_memory=False)

    # build intent->category map
    intent2cat = dict(zip(df_int['intent'].astype(str), df_int['categoria_amigable'].astype(str)))

    # prepare synthetic df: instruction, category, intent
    df_syn_p = pd.DataFrame()
    df_syn_p['instruction'] = df_syn['text'].astype(str)
    df_syn_p['intent'] = df_syn['intent'].astype(str)
    df_syn_p['category'] = df_syn_p['intent'].map(lambda x: intent2cat.get(x, 'UNKNOWN'))
    df_syn_p['source'] = 'synthetic'

    df_orig_p = df_orig.copy()
    df_orig_p['source'] = 'original'

    df_comb = pd.concat([df_orig_p, df_syn_p], ignore_index=True, sort=False)
    # ensure column order
    cols = ['instruction', 'category', 'intent', 'source']
    for c in cols:
        if c not in df_comb.columns:
            df_comb[c] = ''
    df_comb = df_comb[cols]

    df_comb.to_csv(OUT, index=False, encoding='utf-8')
    print('Merged dataset saved to', OUT)


if __name__ == '__main__':
    merge()

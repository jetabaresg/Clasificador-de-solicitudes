import json
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import classification_report
import joblib


def load_primary_dataset():
    # Prefer merged dataset with synthetic samples if exists
    p_merged = Path('Sistema_clasificador/data/dataset_with_synthetic.csv')
    p1 = Path('Sistema_clasificador/data/dataset_bitext_final_limpio.csv')
    p2 = Path('Sistema_clasificador/data/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv')
    if p_merged.exists():
        df = pd.read_csv(p_merged, encoding='utf-8', low_memory=False)
    elif p1.exists():
        df = pd.read_csv(p1, encoding='utf-8', low_memory=False)
    elif p2.exists():
        df = pd.read_csv(p2, encoding='utf-8', low_memory=False)
    else:
        raise FileNotFoundError('No dataset found')
    return df


def prepare_data(df, sample_size=5000, text_col='instruction', label_col='intent'):
    df = df.dropna(subset=[text_col])
    # normalize label column: if multi-label separated by ';', split
    y_raw = df[label_col].fillna('UNKNOWN').astype(str)
    y_split = y_raw.map(lambda s: [x.strip() for x in s.split(';') if x.strip()])
    X = df[text_col].astype(str)
    # sample for speed
    if sample_size and len(X) > sample_size:
        df_sample = df.sample(n=sample_size, random_state=42)
        X = df_sample[text_col].astype(str)
        y_split = df_sample[label_col].fillna('UNKNOWN').astype(str).map(lambda s: [x.strip() for x in s.split(';') if x.strip()])

    mlb = MultiLabelBinarizer()
    Y = mlb.fit_transform(y_split)
    return X.tolist(), Y, mlb


def embed_texts(texts, model_name='all-MiniLM-L6-v2'):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    emb = model.encode(texts, show_progress_bar=True, batch_size=64)
    return emb, model


def train_classifier(X_emb, Y):
    clf = OneVsRestClassifier(LogisticRegression(max_iter=1000))
    clf.fit(X_emb, Y)
    return clf


def evaluate(clf, X_emb, Y, mlb):
    preds = clf.predict(X_emb)
    report = classification_report(Y, preds, target_names=mlb.classes_, zero_division=0, output_dict=True)
    return report


def main():
    df = load_primary_dataset()
    X_texts, Y, mlb = prepare_data(df, sample_size=5000)
    print('Samples:', len(X_texts), 'Labels shape:', Y.shape)
    X_emb, embed_model = embed_texts(X_texts)
    clf = train_classifier(X_emb, Y)
    report = evaluate(clf, X_emb, Y, mlb)
    out = Path('reports')
    out.mkdir(exist_ok=True)
    # save artifacts
    joblib.dump(clf, out / 'baseline_clf.joblib')
    joblib.dump(mlb, out / 'baseline_mlb.joblib')
    # save embedding model name for inference
    with open(out / 'baseline_report.json', 'w', encoding='utf-8') as fh:
        json.dump({'report': report, 'classes': mlb.classes_.tolist()}, fh, ensure_ascii=False, indent=2)
    print('Training completo. Artifacts saved en reports/')


if __name__ == '__main__':
    main()

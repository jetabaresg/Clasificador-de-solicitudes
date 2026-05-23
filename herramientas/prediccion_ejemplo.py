from sentence_transformers import SentenceTransformer
import joblib
from pathlib import Path


ARTIFACTS_DIR = Path('reports')
CLF_PATH = ARTIFACTS_DIR / 'baseline_clf.joblib'
MLB_PATH = ARTIFACTS_DIR / 'baseline_mlb.joblib'


def load_artifacts():
    clf = joblib.load(CLF_PATH)
    mlb = joblib.load(MLB_PATH)
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    return clf, mlb, embed_model


def predict_texts(texts, top_k=3):
    clf, mlb, embed_model = load_artifacts()
    emb = embed_model.encode(texts)
    # try predict_proba, fallback to decision_function
    if hasattr(clf, 'predict_proba'):
        scores = clf.predict_proba(emb)
    else:
        scores = clf.decision_function(emb)

    results = []
    for row in scores:
        # row shape: (n_classes,) or list of arrays for OneVsRestClassifier
        import numpy as np
        arr = np.array(row)
        top_idx = arr.argsort()[::-1][:top_k]
        labels = [mlb.classes_[i] for i in top_idx]
        probs = arr[top_idx].tolist()
        results.append(list(zip(labels, probs)))
    return results


if __name__ == '__main__':
    sample = [
        "Necesito cancelar mi pedido 12345",
        "¿Cómo puedo obtener la factura de mi compra?",
        "No puedo ingresar a mi cuenta"
    ]
    preds = predict_texts(sample, top_k=2)
    for t, p in zip(sample, preds):
        print('\nInput:', t)
        for label, prob in p:
            print(f'  - {label}: {prob:.4f}')

"""
Intent Classifiers for AI Customer Support Agent.
Supports:
- Majority Baseline Classifier
- Keyword / Rule-Based Classifier
- Embedding Nearest-Neighbor (Centroid/KNN) Classifier
- TF-IDF + Calibrated Supervised Classifier
- Dense LSA Embedding (TruncatedSVD) + Supervised Classifier
- UNKNOWN / UNCERTAIN thresholding & confidence scoring
"""

import os
import re
import numpy as np
import joblib
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity


class BaseIntentClassifier:
    def __init__(self, confidence_threshold: float = 0.40):
        self.confidence_threshold = confidence_threshold
        self.classes_ = []

    def fit(self, texts: List[str], labels: List[str]):
        raise NotImplementedError

    def predict_one(self, text: str) -> Dict[str, Any]:
        res = self.predict_batch([text])
        return res[0]

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def save(self, filepath: str):
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str):
        return joblib.load(filepath)


class MajorityClassifier(BaseIntentClassifier):
    """Baseline 1: Always predicts the majority class from training data."""

    def __init__(self, confidence_threshold: float = 0.0):
        super().__init__(confidence_threshold)
        self.majority_intent = "OTHER / UNKNOWN"
        self.majority_confidence = 1.0

    def fit(self, texts: List[str], labels: List[str]):
        from collections import Counter
        counts = Counter(labels)
        self.majority_intent, top_count = counts.most_common(1)[0]
        self.majority_confidence = float(top_count / len(labels))
        self.classes_ = list(set(labels))
        return self

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        results = []
        for _ in texts:
            results.append({
                "predicted_intent": self.majority_intent,
                "raw_intent": self.majority_intent,
                "confidence": self.majority_confidence,
                "is_uncertain": False,
                "all_probabilities": {c: (1.0 if c == self.majority_intent else 0.0) for c in self.classes_}
            })
        return results


class RuleBasedClassifier(BaseIntentClassifier):
    """Baseline 2: Keyword and regex rule-based intent classifier."""

    INTENT_KEYWORDS = {
        "SOFTWARE_UPDATE_ISSUES": [
            r"\bupdate\b", r"\bos\b", r"\bsoftware\b", r"\bupgrade\b", r"\bfirmware\b",
            r"\binstallation\b", r"\bios\b", r"\bversion\b", r"\binstalling\b"
        ],
        "BATTERY_POWER_CHARGING": [
            r"\bbattery\b", r"\bcharge\b", r"\bcharging\b", r"\bcharger\b", r"\bpower\b",
            r"\bdrain\b", r"\bdraining\b", r"\bplug\b", r"\bcable\b"
        ],
        "ACCOUNT_LOGIN_SECURITY": [
            r"\blogin\b", r"\bpassword\b", r"\blocked\b", r"\bsign in\b", r"\blog in\b",
            r"\bpasscode\b", r"\b2fa\b", r"\bcredentials\b", r"\bunlocked\b", r"\bauth\b"
        ],
        "APP_CRASH_PERFORMANCE": [
            r"\bcrash\b", r"\bcrashes\b", r"\bcrashing\b", r"\bfreeze\b", r"\bfrozen\b",
            r"\bfreezing\b", r"\blag\b", r"\blagging\b", r"\bunresponsive\b", r"\bglitch\b"
        ],
        "BILLING_REFUND_SUBSCRIPTION": [
            r"\brefund\b", r"\bbill\b", r"\bbilling\b", r"\bcharge\b", r"\bcharged\b",
            r"\bpayment\b", r"\bsubscription\b", r"\bcancel\b", r"\bmembership\b", r"\breceipt\b"
        ],
        "ORDER_SHIPPING_DELIVERY": [
            r"\border\b", r"\bpackage\b", r"\bdelivery\b", r"\bshipment\b", r"\bshipping\b",
            r"\btrack\b", r"\btracking\b", r"\bdelivered\b", r"\bcourier\b", r"\bparcel\b", r"\barrive\b"
        ],
        "CONNECTIVITY_NETWORK_WIFI": [
            r"\bwifi\b", r"\bwi-fi\b", r"\bbluetooth\b", r"\bnetwork\b", r"\bsignal\b",
            r"\bcellular\b", r"\bsim\b", r"\boffline\b", r"\bpairing\b", r"\bconnect\b"
        ],
        "AUDIO_SPEAKER_MICROPHONE": [
            r"\bsound\b", r"\bvolume\b", r"\bspeaker\b", r"\bmic\b", r"\bmicrophone\b",
            r"\baudio\b", r"\bheadphone\b", r"\bheadphones\b", r"\bairpods\b"
        ],
        "DISPLAY_SCREEN_PHYSICAL": [
            r"\bscreen\b", r"\bdisplay\b", r"\bflicker\b", r"\bflickering\b", r"\bblack screen\b",
            r"\btouchscreen\b", r"\bcracked\b"
        ],
        "STORE_REPAIR_SERVICE": [
            r"\brepair\b", r"\bappointment\b", r"\bwarranty\b", r"\breplace\b", r"\bservice center\b",
            r"\breplacement\b", r"\bstore\b"
        ]
    }

    def __init__(self, confidence_threshold: float = 0.30):
        super().__init__(confidence_threshold)
        self.compiled_rules = {
            intent: [re.compile(kw, re.IGNORECASE) for kw in kws]
            for intent, kws in self.INTENT_KEYWORDS.items()
        }
        self.classes_ = list(self.INTENT_KEYWORDS.keys()) + ["OTHER / UNKNOWN"]

    def fit(self, texts: List[str], labels: List[str]):
        return self

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        results = []
        for text in texts:
            scores = {}
            for intent, regexes in self.compiled_rules.items():
                matches = sum(1 for r in regexes if r.search(text))
                scores[intent] = matches

            total_matches = sum(scores.values())
            if total_matches == 0:
                best_intent = "OTHER / UNKNOWN"
                conf = 1.0
                is_uncertain = False
            else:
                best_intent = max(scores, key=scores.get)
                match_count = scores[best_intent]
                conf = round(match_count / max(total_matches, 1), 4)
                if match_count == 1:
                    conf = 0.5
                is_uncertain = conf < self.confidence_threshold

            final_intent = "OTHER / UNKNOWN" if (is_uncertain and best_intent != "OTHER / UNKNOWN") else best_intent

            prob_dist = {c: 0.0 for c in self.classes_}
            if total_matches > 0:
                for k, v in scores.items():
                    prob_dist[k] = round(v / total_matches, 4)
            else:
                prob_dist["OTHER / UNKNOWN"] = 1.0

            results.append({
                "predicted_intent": final_intent,
                "raw_intent": best_intent,
                "confidence": conf,
                "is_uncertain": is_uncertain,
                "all_probabilities": prob_dist
            })
        return results


class EmbeddingKNNClassifier(BaseIntentClassifier):
    """Baseline 3: Simple Embedding Nearest-Neighbor (Centroid Cosine Similarity) Classifier."""

    def __init__(self, confidence_threshold: float = 0.35, n_components: int = 250):
        super().__init__(confidence_threshold)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=25000, sublinear_tf=True)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.class_centroids = {}
        self.classes_ = []

    def fit(self, texts: List[str], labels: List[str]):
        tfidf_mat = self.vectorizer.fit_transform(texts)
        dense_embeds = self.svd.fit_transform(tfidf_mat)

        norms = np.linalg.norm(dense_embeds, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        dense_embeds = dense_embeds / norms

        self.classes_ = sorted(list(set(labels)))

        for label in self.classes_:
            indices = [i for i, l in enumerate(labels) if l == label]
            if indices:
                label_embeds = dense_embeds[indices]
                centroid = np.mean(label_embeds, axis=0)
                c_norm = np.linalg.norm(centroid)
                if c_norm > 0:
                    centroid = centroid / c_norm
                self.class_centroids[label] = centroid

        return self

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        tfidf_mat = self.vectorizer.transform(texts)
        dense_embeds = self.svd.transform(tfidf_mat)
        norms = np.linalg.norm(dense_embeds, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        dense_embeds = dense_embeds / norms

        centroid_matrix = np.array([self.class_centroids[c] for c in self.classes_])
        sims = cosine_similarity(dense_embeds, centroid_matrix)

        results = []
        for i in range(len(texts)):
            row_sims = sims[i]
            best_idx = int(np.argmax(row_sims))
            raw_intent = self.classes_[best_idx]
            conf = float(row_sims[best_idx])

            exp_sims = np.exp((row_sims - np.max(row_sims)) * 5)
            probs = exp_sims / np.sum(exp_sims)
            prob_dict = {self.classes_[j]: round(float(probs[j]), 4) for j in range(len(self.classes_))}

            is_uncertain = conf < self.confidence_threshold
            final_intent = "OTHER / UNKNOWN" if (is_uncertain and raw_intent != "OTHER / UNKNOWN") else raw_intent

            results.append({
                "predicted_intent": final_intent,
                "raw_intent": raw_intent,
                "confidence": round(conf, 4),
                "is_uncertain": is_uncertain,
                "all_probabilities": prob_dict
            })
        return results


class TFIDFClassifier(BaseIntentClassifier):
    """Proposed Model A: TF-IDF Vectorizer + Calibrated Logistic Regression Classifier."""

    def __init__(self, confidence_threshold: float = 0.40, c_val: float = 2.0):
        super().__init__(confidence_threshold)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_features=30000,
            sublinear_tf=True
        )
        self.model = LogisticRegression(
            C=c_val,
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )
        self.classes_ = []

    def fit(self, texts: List[str], labels: List[str]):
        print(f"Fitting TF-IDF vectorizer on {len(texts):,} texts...")
        X = self.vectorizer.fit_transform(texts)
        print("Training Logistic Regression classifier...")
        self.model.fit(X, labels)
        self.classes_ = list(self.model.classes_)
        return self

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        X = self.vectorizer.transform(texts)
        probs_matrix = self.model.predict_proba(X)

        results = []
        for i in range(len(texts)):
            probs = probs_matrix[i]
            best_idx = int(np.argmax(probs))
            raw_intent = self.classes_[best_idx]
            conf = float(probs[best_idx])

            prob_dict = {self.classes_[j]: round(float(probs[j]), 4) for j in range(len(self.classes_))}
            is_uncertain = conf < self.confidence_threshold
            final_intent = "OTHER / UNKNOWN" if (is_uncertain and raw_intent != "OTHER / UNKNOWN") else raw_intent

            results.append({
                "predicted_intent": final_intent,
                "raw_intent": raw_intent,
                "confidence": round(conf, 4),
                "is_uncertain": is_uncertain,
                "all_probabilities": prob_dict
            })
        return results


class DenseEmbeddingClassifier(BaseIntentClassifier):
    """Proposed Model B: Dense Semantic LSA Embedding (TruncatedSVD 300d) + Supervised Logistic Regression."""

    def __init__(self, confidence_threshold: float = 0.40, n_components: int = 300, c_val: float = 3.0):
        super().__init__(confidence_threshold)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=35000, sublinear_tf=True)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.model = LogisticRegression(
            C=c_val,
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )
        self.classes_ = []

    def fit(self, texts: List[str], labels: List[str]):
        print(f"Extracting TF-IDF and fitting TruncatedSVD (300d) dense embeddings on {len(texts):,} texts...")
        tfidf_mat = self.vectorizer.fit_transform(texts)
        dense_embeds = self.svd.fit_transform(tfidf_mat)

        print("Fitting Supervised Logistic Regression on dense LSA embeddings...")
        self.model.fit(dense_embeds, labels)
        self.classes_ = list(self.model.classes_)
        return self

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        tfidf_mat = self.vectorizer.transform(texts)
        dense_embeds = self.svd.transform(tfidf_mat)
        probs_matrix = self.model.predict_proba(dense_embeds)

        results = []
        for i in range(len(texts)):
            probs = probs_matrix[i]
            best_idx = int(np.argmax(probs))
            raw_intent = self.classes_[best_idx]
            conf = float(probs[best_idx])

            prob_dict = {self.classes_[j]: round(float(probs[j]), 4) for j in range(len(self.classes_))}
            is_uncertain = conf < self.confidence_threshold
            final_intent = "OTHER / UNKNOWN" if (is_uncertain and raw_intent != "OTHER / UNKNOWN") else raw_intent

            results.append({
                "predicted_intent": final_intent,
                "raw_intent": raw_intent,
                "confidence": round(conf, 4),
                "is_uncertain": is_uncertain,
                "all_probabilities": prob_dict
            })
        return results

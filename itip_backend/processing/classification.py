import numpy as np # type: ignore

UNKNOWN_THRESHOLD = 0.45

def classify_entity(features_vector: list, model, classes: list[str]) -> dict:
    """
    Classify a thermal entity based on features.
    features_vector: Preprocessed numeric features.
    model: Trained scikit-learn / LightGBM model supporting predict_proba.
    classes: list of class names, e.g. ['industrial_fire', 'persistent_thermal_source', ...]
    """
    probabilities = model.predict_proba([features_vector])[0]
    
    top_idx = np.argmax(probabilities)
    top_prob = probabilities[top_idx]
    top_class = classes[top_idx]

    # Explicit thresholding for unknown class to prevent forced answers
    label = top_class if top_prob >= UNKNOWN_THRESHOLD else "unknown"

    return {
        "prediction": label,
        "confidence": round(float(top_prob), 3),
        "probabilities": {cls: round(float(prob), 3) for cls, prob in zip(classes, probabilities)}
    }

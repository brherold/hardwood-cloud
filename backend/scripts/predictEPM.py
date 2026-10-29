import numpy as np
import joblib
import warnings
import os

try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except Exception:
    pass

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")
warnings.filterwarnings("ignore", message=".*X does not have valid feature names.*")
warnings.filterwarnings("ignore", message=".*trying to unpickle estimator.*")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(BASE_DIR, "EPM_Model")

POSITIONS = ["PG", "SG", "SF", "PF", "C"]

MODEL_CACHE = {}

def _load_epm_models(pos):
    pos = pos.upper()
    if pos in MODEL_CACHE:
        return MODEL_CACHE[pos]

    model_off = joblib.load(os.path.join(MODEL_DIR, f"model_off_{pos}.pkl"))
    model_def = joblib.load(os.path.join(MODEL_DIR, f"model_def_{pos}.pkl"))

    y_off_pred = joblib.load(os.path.join(MODEL_DIR, f"y_off_pred_{pos}.pkl"))
    y_def_pred = joblib.load(os.path.join(MODEL_DIR, f"y_def_pred_{pos}.pkl"))

    MODEL_CACHE[pos] = {
        "model_off": model_off,
        "model_def": model_def,
        "y_off_mean": float(np.mean(y_off_pred)),
        "y_off_std": float(np.std(y_off_pred)),
        "y_def_mean": float(np.mean(y_def_pred)),
        "y_def_std": float(np.std(y_def_pred)),
    }
    return MODEL_CACHE[pos]

def predict_epm(pos, Poss, O_Poss, off_values, def_values):
    pos = pos.upper()
    data = _load_epm_models(pos)

    model_off = data["model_off"]
    model_def = data["model_def"]

    y_off_mean = data["y_off_mean"]
    y_off_std = data["y_off_std"]
    y_def_mean = data["y_def_mean"]
    y_def_std = data["y_def_std"]

    # Prevent divide-by-zero
    Poss = max(Poss, 1)
    O_Poss = max(O_Poss, 1)

    # Convert to NumPy arrays (faster than Python lists)
    off_array = np.array(off_values, dtype=float)
    def_array = np.array(def_values, dtype=float)

    # Convert to per 100 possessions
    off_per100 = off_array * 100 / Poss
    def_per100 = def_array * 100 / O_Poss

    # Drop last stat for PG/SG if not used
    if pos in ["PG", "SG"]:
        off_per100 = off_per100[:-1]
        def_per100 = def_per100[:-1]

    # Predict
    oepm = model_off.predict(off_per100.reshape(1, -1))[0]
    depm = model_def.predict(def_per100.reshape(1, -1))[0]

    # Normalize to target distribution
    target_mean = 0
    target_std = 2.5

    if y_off_std != 0:
        oepm_scaled = ((oepm - y_off_mean) / y_off_std) * target_std + target_mean
    else:
        oepm_scaled = target_mean

    if y_def_std != 0:
        depm_scaled = ((depm - y_def_mean) / y_def_std) * target_std + target_mean
    else:
        depm_scaled = target_mean

    epm_total = oepm_scaled + depm_scaled

    return (
        round(float(oepm_scaled), 1),
        round(float(depm_scaled), 1),
        round(float(epm_total), 1),
    )


# =====================================================
# Example Usage
# =====================================================
'''
if __name__ == "__main__":
    pos = "PF"
    Poss = 47.515
    O_Poss = 47.515

#off_features = ['FG_A','_2P_M','_3P_M','FT_M','AST','TO'](SF/PF/C) includes ['Off']
    off_values = [6.1, 3.15, 0, 1.2, 1.2, 1.1, 1.5]

#def_features = ['O_FG_A','O_2P_M','O_3P_M','STL','PF'] (SF/PF/C) includes ['Def']
    def_values = [4.95, 2.85, 0.4, 0.9, 1.7, 4.2]

    print(predict_epm(pos, Poss, O_Poss, off_values, def_values))
'''
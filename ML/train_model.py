import os, sys, json, warnings
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier

from sklearn.model_selection import (
    train_test_split, cross_val_score,
    StratifiedKFold, RandomizedSearchCV
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    classification_report, roc_curve
)
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')
sns.set_theme(style='whitegrid', palette='muted')

# --------------------------------------------------
# PATHS
# --------------------------------------------------
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH     = os.path.join(BASE_DIR, 'DATA', 'flood_data.csv')
MODEL_PATH    = os.path.join(BASE_DIR, 'ML',   'flood_model.pkl')
SCALER_PATH   = os.path.join(BASE_DIR, 'ML',   'scaler.pkl')
META_PATH     = os.path.join(BASE_DIR, 'ML',   'model_metadata.json')
REPORTS_DIR   = os.path.join(BASE_DIR, 'ML',   'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
data = pd.read_csv(DATA_PATH)

print('=' * 62)
print('  FLOOD PREDICTION ML PIPELINE')
print('  KIIT University, Bhubaneswar, Odisha')
print('=' * 62)
print()
print('Dataset  :', len(data), 'rows,', len(data.columns)-1, 'features')
print('Flood    :', data['flood'].sum(), '(' + str(round(data['flood'].mean()*100, 1)) + '%)')
print('No-flood :', (data['flood']==0).sum(), '(' + str(round((1-data['flood'].mean())*100, 1)) + '%)')

# --------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------
data['rainfall_water_index'] = data['rainfall'] * data['water_level']
data['flood_risk_index']     = (4 - data['elevation']) * (4 - data['drainage']) * data['rainfall'] / 1000.0
data['proximity_risk']       = 1.0 / (data['distance_to_river'] + 0.1)

print()
print('Feature Engineering -- 3 new derived features:')
print('  rainfall_water_index  = rainfall x water_level')
print('  flood_risk_index      = elevation x drainage x rainfall score')
print('  proximity_risk        = 1 / (distance_to_river + 0.1)')

FEATURES = [
    'rainfall', 'water_level', 'elevation', 'drainage',
    'humidity', 'soil_type', 'population_density',
    'distance_to_river', 'historical_flood_freq', 'drainage_capacity',
    'rainfall_water_index', 'flood_risk_index', 'proximity_risk'
]

X = data[FEATURES]
y = data['flood']

# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print()
print('Train set :', len(X_train), 'rows')
print('Test set  :', len(X_test),  'rows')

# --------------------------------------------------
# SCALING (for SVM, KNN, LR, MLP)
# --------------------------------------------------
scaler         = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)
joblib.dump(scaler, SCALER_PATH)

SCALED_MODELS = {'Logistic Regression', 'SVM', 'KNN', 'Neural Network'}

# --------------------------------------------------
# STEP 1 -- 7 MODEL COMPARISON  (5-Fold CV, F1)
# --------------------------------------------------
models = {
    'Logistic Regression' : LogisticRegression(random_state=42, max_iter=1000),
    'Random Forest'       : RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting'   : GradientBoostingClassifier(n_estimators=100, random_state=42),
    'XGBoost'             : XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss', verbosity=0),
    'SVM'                 : SVC(probability=True, random_state=42),
    'KNN'                 : KNeighborsClassifier(n_neighbors=5),
    'Neural Network'      : MLPClassifier(hidden_layer_sizes=(64, 32), random_state=42, max_iter=500),
}

print()
print('=' * 62)
print('  STEP 1 -- MODEL COMPARISON  (5-Fold CV, F1 Score)')
print('=' * 62)

cv         = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_results = {}

for name, mdl in models.items():
    X_cv   = X_train_scaled if name in SCALED_MODELS else X_train.values
    scores = cross_val_score(mdl, X_cv, y_train, cv=cv, scoring='f1', n_jobs=-1)
    cv_results[name] = {'mean': scores.mean(), 'std': scores.std()}
    line = '  ' + name.ljust(22) + ': F1 = ' + str(round(scores.mean(), 4)) + ' (+/- ' + str(round(scores.std(), 4)) + ')'
    print(line)

sorted_models = sorted(cv_results.items(), key=lambda x: x[1]['mean'], reverse=True)

print()
print('  Top 3 models:')
for i, (name, sc) in enumerate(sorted_models[:3], 1):
    print('    ' + str(i) + '. ' + name + ' -- F1 = ' + str(round(sc['mean'], 4)))

# -- Chart 1: Model Comparison --
fig, ax = plt.subplots(figsize=(10, 5))
names  = [x[0] for x in sorted_models]
means  = [x[1]['mean'] for x in sorted_models]
stds   = [x[1]['std']  for x in sorted_models]
colors = ['#2ecc71' if i == 0 else '#3498db' if i == 1 else '#e67e22' if i == 2 else '#95a5a6'
          for i in range(len(names))]
bars = ax.barh(names, means, xerr=stds, color=colors, alpha=0.85, capsize=4, edgecolor='white')
ax.set_xlabel('F1 Score (5-Fold CV)', fontsize=11)
ax.set_title('Model Comparison -- KIIT Flood Prediction', fontsize=13, fontweight='bold')
ax.set_xlim(0, 1.1)
for bar, val in zip(bars, means):
    ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
            str(round(val, 4)), va='center', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, 'model_comparison.png'), dpi=150, bbox_inches='tight')
plt.close()
print()
print('  Chart saved: model_comparison.png')

# --------------------------------------------------
# STEP 2 -- HYPERPARAMETER TUNING  (Top 3)
# --------------------------------------------------
param_grids = {
    'Logistic Regression' : {
        'C'        : [0.01, 0.1, 1, 10, 100],
        'solver'   : ['lbfgs', 'liblinear'],
        'max_iter' : [500, 1000],
    },
    'Random Forest' : {
        'n_estimators'     : [100, 200, 300],
        'max_depth'        : [None, 5, 10, 15],
        'min_samples_split': [2, 5, 10],
        'class_weight'     : ['balanced', None],
    },
    'Gradient Boosting' : {
        'n_estimators'  : [100, 200, 300],
        'learning_rate' : [0.05, 0.1, 0.2],
        'max_depth'     : [3, 5, 7],
        'subsample'     : [0.8, 1.0],
    },
    'XGBoost' : {
        'n_estimators'  : [100, 200, 300],
        'learning_rate' : [0.05, 0.1, 0.2],
        'max_depth'     : [3, 5, 7],
        'subsample'     : [0.8, 1.0],
    },
    'SVM' : {
        'C'      : [0.1, 1, 10],
        'kernel' : ['rbf', 'linear'],
        'gamma'  : ['scale', 'auto'],
    },
    'KNN' : {
        'n_neighbors': [3, 5, 7, 9, 11],
        'weights'    : ['uniform', 'distance'],
        'metric'     : ['euclidean', 'manhattan'],
    },
    'Neural Network' : {
        'hidden_layer_sizes' : [(64, 32), (128, 64), (64, 32, 16)],
        'learning_rate_init' : [0.001, 0.01],
        'alpha'              : [0.0001, 0.001],
    },
}

print()
print('=' * 62)
print('  STEP 2 -- HYPERPARAMETER TUNING  (Top 3 via RandomizedSearchCV)')
print('=' * 62)

top3_names   = [x[0] for x in sorted_models[:3]]
tuned_results = {}

for name in top3_names:
    print()
    print('  Tuning:', name, '...')
    base_model  = models[name]
    param_grid  = param_grids.get(name, {})
    X_cv        = X_train_scaled if name in SCALED_MODELS else X_train.values

    searcher = RandomizedSearchCV(
        base_model, param_grid,
        n_iter=20, cv=cv, scoring='f1',
        random_state=42, n_jobs=-1
    )
    searcher.fit(X_cv, y_train)

    tuned_results[name] = {
        'model' : searcher.best_estimator_,
        'score' : searcher.best_score_,
        'scaled': name in SCALED_MODELS,
    }
    print('    Best F1    :', round(searcher.best_score_, 4))
    print('    Best Params:', searcher.best_params_)

# --------------------------------------------------
# STEP 3 -- BEST MODEL SELECTED
# --------------------------------------------------
best_name  = max(tuned_results, key=lambda k: tuned_results[k]['score'])
best_info  = tuned_results[best_name]
best_model = best_info['model']
use_scaled = best_info['scaled']

print()
print('=' * 62)
print('  STEP 3 -- BEST MODEL: ' + best_name)
print('  Tuned F1 : ' + str(round(best_info['score'], 4)))
print('=' * 62)

X_tr = X_train_scaled if use_scaled else X_train.values
X_te = X_test_scaled  if use_scaled else X_test.values
best_model.fit(X_tr, y_train)

# --------------------------------------------------
# STEP 4 -- EVALUATION ON TEST SET
# --------------------------------------------------
y_pred = best_model.predict(X_te)
y_prob = best_model.predict_proba(X_te)[:, 1]

acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec  = recall_score(y_test, y_pred)
f1   = f1_score(y_test, y_pred)
auc  = roc_auc_score(y_test, y_prob)
cm   = confusion_matrix(y_test, y_pred)

print()
print('  Test Set Metrics:')
print('    Accuracy  :', round(acc, 4))
print('    Precision :', round(prec, 4))
print('    Recall    :', round(rec, 4))
print('    F1-Score  :', round(f1, 4))
print('    ROC-AUC   :', round(auc, 4))
print()
print('  Confusion Matrix:')
print('    TN=' + str(cm[0][0]) + '  FP=' + str(cm[0][1]))
print('    FN=' + str(cm[1][0]) + '  TP=' + str(cm[1][1]))
print()
print(classification_report(y_test, y_pred, target_names=['No Flood', 'Flood']))

# --------------------------------------------------
# STEP 5 -- VISUALIZATIONS
# --------------------------------------------------
print('Saving charts to ML/reports/ ...')

# Chart 2: Confusion Matrix heatmap
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(
    cm, annot=True, fmt='d', cmap='Blues',
    xticklabels=['No Flood', 'Flood'],
    yticklabels=['No Flood', 'Flood'],
    ax=ax, linewidths=0.8, annot_kws={'size': 14}
)
ax.set_title('Confusion Matrix -- ' + best_name, fontsize=13, fontweight='bold')
ax.set_ylabel('Actual', fontsize=11)
ax.set_xlabel('Predicted', fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, 'confusion_matrix.png'), dpi=150, bbox_inches='tight')
plt.close()

# Chart 3: ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
fig, ax = plt.subplots(figsize=(6, 5))
ax.plot(fpr, tpr, color='#e74c3c', lw=2.5,
        label='ROC Curve (AUC = ' + str(round(auc, 4)) + ')')
ax.plot([0, 1], [0, 1], color='gray', linestyle='--', lw=1)
ax.fill_between(fpr, tpr, alpha=0.08, color='#e74c3c')
ax.set_xlabel('False Positive Rate', fontsize=11)
ax.set_ylabel('True Positive Rate', fontsize=11)
ax.set_title('ROC Curve -- ' + best_name, fontsize=13, fontweight='bold')
ax.legend(loc='lower right', fontsize=10)
ax.set_xlim([0, 1])
ax.set_ylim([0, 1.02])
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, 'roc_curve.png'), dpi=150, bbox_inches='tight')
plt.close()

# Chart 4: Feature Importance (tree-based models)
if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    feat_df = pd.DataFrame({'feature': FEATURES, 'importance': importances})
    feat_df = feat_df.sort_values('importance', ascending=True)
    mean_imp = feat_df['importance'].mean()
    colors_fi = ['#e74c3c' if v >= mean_imp else '#3498db' for v in feat_df['importance']]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(feat_df['feature'], feat_df['importance'], color=colors_fi, alpha=0.85, edgecolor='white')
    ax.axvline(mean_imp, color='gray', linestyle='--', lw=1.5, label='Mean Importance')
    ax.set_xlabel('Feature Importance', fontsize=11)
    ax.set_title('Feature Importance -- ' + best_name, fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, 'feature_importance.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  feature_importance.png  -- saved')
elif hasattr(best_model, 'coef_'):
    importances = np.abs(best_model.coef_[0])
    feat_df = pd.DataFrame({'feature': FEATURES, 'importance': importances})
    feat_df = feat_df.sort_values('importance', ascending=True)
    mean_imp = feat_df['importance'].mean()
    colors_fi = ['#e74c3c' if v >= mean_imp else '#3498db' for v in feat_df['importance']]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(feat_df['feature'], feat_df['importance'], color=colors_fi, alpha=0.85, edgecolor='white')
    ax.axvline(mean_imp, color='gray', linestyle='--', lw=1.5, label='Mean')
    ax.set_xlabel('Coefficient Magnitude', fontsize=11)
    ax.set_title('Feature Weights -- ' + best_name, fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, 'feature_importance.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  feature_importance.png  -- saved (coef)')

print('  model_comparison.png    -- saved')
print('  confusion_matrix.png    -- saved')
print('  roc_curve.png           -- saved')

# --------------------------------------------------
# STEP 6 -- SAVE MODEL + METADATA
# --------------------------------------------------
joblib.dump(best_model, MODEL_PATH)

metadata = {
    'model_name'      : best_name,
    'trained_on'      : str(pd.Timestamp.now().date()),
    'dataset_rows'    : len(data),
    'n_features'      : len(FEATURES),
    'features'        : FEATURES,
    'accuracy'        : round(acc, 4),
    'precision'       : round(prec, 4),
    'recall'          : round(rec, 4),
    'f1_score'        : round(f1, 4),
    'roc_auc'         : round(auc, 4),
    'use_scaled_input': use_scaled,
    'location'        : 'KIIT University, Bhubaneswar, Odisha',
}
with open(META_PATH, 'w') as f:
    json.dump(metadata, f, indent=4)

print()
print('  Model saved    :', MODEL_PATH)
print('  Scaler saved   :', SCALER_PATH)
print('  Metadata saved :', META_PATH)
print()
print('=' * 62)
print('  PIPELINE COMPLETE')
print('=' * 62)
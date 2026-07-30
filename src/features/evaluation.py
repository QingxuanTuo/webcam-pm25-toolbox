import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import (
    KFold,
    train_test_split,
)


def random_split(
    df,
    test_size=0.2,
    random_state=42,
):
    development_df, test_df = train_test_split(
        df,
        test_size=test_size,
        shuffle=True,
        random_state=random_state,
    )

    return (
        development_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


def evaluate_regression(y_true, y_pred):
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "R2": r2_score(y_true, y_pred),
    }


def evaluate_feature_set(
    model,
    model_name,
    feature_set_name,
    feature_list,
    development_df,
    test_df,
    target,
    n_splits=5,
    random_state=42,
):
    X_dev = development_df[feature_list].reset_index(drop=True)
    y_dev = development_df[target].reset_index(drop=True)

    X_test = test_df[feature_list].reset_index(drop=True)
    y_test = test_df[target].reset_index(drop=True)

    kfold = KFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=random_state,
    )

    fold_results = []

    for fold, (train_idx, val_idx) in enumerate(
        kfold.split(X_dev),
        start=1,
    ):
        fold_model = clone(model)

        X_train = X_dev.iloc[train_idx]
        X_val = X_dev.iloc[val_idx]

        y_train = y_dev.iloc[train_idx]
        y_val = y_dev.iloc[val_idx]

        fold_model.fit(X_train, y_train)
        y_val_pred = fold_model.predict(X_val)

        fold_results.append(
            {
                "Fold": fold,
                **evaluate_regression(y_val, y_val_pred),
            }
        )

    fold_results = pd.DataFrame(fold_results)

    final_model = clone(model)
    final_model.fit(X_dev, y_dev)

    y_test_pred = final_model.predict(X_test)
    test_metrics = evaluate_regression(
        y_test,
        y_test_pred,
    )

    summary = pd.DataFrame(
        [
            {
                "Model": model_name,
                "Feature Set": feature_set_name,
                "Variables": len(feature_list),
                "CV MAE": fold_results["MAE"].mean(),
                "CV MAE Std": fold_results["MAE"].std(),
                "CV RMSE": fold_results["RMSE"].mean(),
                "CV RMSE Std": fold_results["RMSE"].std(),
                "CV R2": fold_results["R2"].mean(),
                "CV R2 Std": fold_results["R2"].std(),
                "Test MAE": test_metrics["MAE"],
                "Test RMSE": test_metrics["RMSE"],
                "Test R2": test_metrics["R2"],
            }
        ]
    )

    return summary, fold_results, y_test, y_test_pred
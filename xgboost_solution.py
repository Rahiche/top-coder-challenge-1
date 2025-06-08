#!/usr/bin/env python3

import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import xgboost as xgb

def load_data(filename):
    """Load data from JSON file and return features and targets"""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    features = []
    targets = []
    
    for case in data:
        input_data = case['input']
        days = input_data['trip_duration_days']
        miles = input_data['miles_traveled']
        receipts = input_data['total_receipts_amount']
        
        # Create feature vector with engineered features
        feature_vector = create_features(days, miles, receipts)
        features.append(feature_vector)
        targets.append(case['expected_output'])
    
    return np.array(features), np.array(targets)

def create_features(days, miles, receipts):
    """Engineer features from the basic inputs"""
    features = [
        # Basic features
        days,
        miles,
        receipts,
        
        # Polynomial features
        days ** 2,
        miles ** 2,
        receipts ** 2,
        
        # Interaction features
        days * miles,
        days * receipts,
        miles * receipts,
        days * miles * receipts,
        
        # Per-day features
        miles / days if days > 0 else 0,
        receipts / days if days > 0 else 0,
        
        # Logarithmic features (add small value to avoid log(0))
        np.log(days + 1),
        np.log(miles + 1),
        np.log(receipts + 1),
        
        # Exponential features (capped to avoid overflow)
        min(np.exp(days * 0.1), 1000),
        min(np.exp(miles * 0.01), 1000),
        min(np.exp(receipts * 0.01), 1000),
        
        # Root features
        np.sqrt(days),
        np.sqrt(miles),
        np.sqrt(receipts),
        
        # Trigonometric features (scaled)
        np.sin(days * 0.5),
        np.cos(days * 0.5),
        np.sin(miles * 0.01),
        np.cos(miles * 0.01),
        
        # Categorical-like features
        1 if days == 1 else 0,
        1 if days <= 3 else 0,
        1 if days >= 7 else 0,
        1 if miles < 50 else 0,
        1 if miles > 200 else 0,
        1 if receipts < 10 else 0,
        1 if receipts > 50 else 0,
        
        # Complex combinations
        (days + miles) / (receipts + 1),
        (miles * receipts) / (days + 1),
        days / (miles + 1),
        receipts / (miles + 1),
        
        # Day-specific patterns
        days % 7,  # Weekly pattern
        1 if days % 2 == 0 else 0,  # Even/odd days
        
        # Mile ranges
        miles // 10,  # Decade grouping
        miles % 10,   # Single digit
        
        # Receipt patterns
        int(receipts * 100) % 100,  # Cents pattern
        int(receipts) % 10,         # Dollar pattern
    ]
    
    return features

def train_xgboost_model(X_train, y_train, X_val, y_val):
    """Train XGBoost model with hyperparameter tuning"""
    
    # Create DMatrix for XGBoost
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)
    
    # XGBoost parameters
    params = {
        'objective': 'reg:squarederror',
        'eval_metric': 'mae',
        'max_depth': 12,
        'learning_rate': 0.01,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'min_child_weight': 1,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'random_state': 42,
        'verbosity': 0
    }
    
    # Train model
    model = xgb.train(
        params,
        dtrain,
        num_boost_round=5000,
        evals=[(dtrain, 'train'), (dval, 'val')],
        early_stopping_rounds=100,
        verbose_eval=False
    )
    
    return model

def predict_reimbursement(model, days, miles, receipts):
    """Predict reimbursement amount for given inputs"""
    features = create_features(days, miles, receipts)
    dtest = xgb.DMatrix([features])
    prediction = model.predict(dtest)[0]
    return round(prediction, 2)

def main():
    print("Loading training data...")
    X, y = load_data('public_cases.json')
    
    print(f"Loaded {len(X)} cases with {len(X[0])} features each")
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print("Training XGBoost model...")
    model = train_xgboost_model(X_train, y_train, X_val, y_val)
    
    # Evaluate on validation set
    dval = xgb.DMatrix(X_val)
    val_pred = model.predict(dval)
    val_mae = mean_absolute_error(y_val, val_pred)
    val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
    
    print(f"Validation MAE: {val_mae:.4f}")
    print(f"Validation RMSE: {val_rmse:.4f}")
    
    # Test on full public dataset
    print("\nTesting on full public dataset...")
    dpublic = xgb.DMatrix(X)
    public_pred = model.predict(dpublic)
    public_mae = mean_absolute_error(y, public_pred)
    public_rmse = np.sqrt(mean_squared_error(y, public_pred))
    
    print(f"Public MAE: {public_mae:.4f}")
    print(f"Public RMSE: {public_rmse:.4f}")
    
    # Show feature importance
    importance = model.get_score(importance_type='weight')
    print(f"\nTop 10 most important features:")
    sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for i, (feature, score) in enumerate(sorted_importance[:10]):
        print(f"{i+1}. {feature}: {score}")
    
    # Save model
    model.save_model('xgboost_reimbursement_model.json')
    print("\nModel saved as 'xgboost_reimbursement_model.json'")
    
    # Test with private cases if available
    try:
        print("\nGenerating predictions for private cases...")
        with open('private_cases.json', 'r') as f:
            private_data = json.load(f)
        
        private_predictions = []
        for case in private_data:
            pred = predict_reimbursement(
                model, 
                case['trip_duration_days'],
                case['miles_traveled'],
                case['total_receipts_amount']
            )
            private_predictions.append(pred)
        
        # Save predictions
        with open('private_predictions.txt', 'w') as f:
            for pred in private_predictions:
                f.write(f"{pred}\n")
        
        print(f"Generated {len(private_predictions)} predictions")
        print("Predictions saved to 'private_predictions.txt'")
        
    except FileNotFoundError:
        print("Private cases file not found, skipping private predictions")
    
    return model

if __name__ == "__main__":
    model = main()
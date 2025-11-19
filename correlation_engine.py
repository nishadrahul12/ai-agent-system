"""
Correlation Analysis Engine
Analyzes relationships between features and target variable
Automatically selects best model for analysis
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_squared_error
import xgboost as xgb
import warnings
from typing import Dict, List, Tuple
import logging

log = logging.getLogger(__name__)


warnings.filterwarnings('ignore')

class CorrelationAnalyzer:
    """
    Analyzes correlations between features and target using multiple models
    Selects best model based on R² score (accuracy priority)
    """
    
    def __init__(self):
        self.best_model = None
        self.best_score = -1
        self.model_results = {}
        self.feature_importance = {}
        
    def prepare_data(self, df: pd.DataFrame, target_col: str, feature_cols: List[str]) -> Tuple:
        """
        Prepare and validate data
        """
        try:
            # Extract target and features
            X = df[feature_cols].copy()
            y = df[target_col].copy()
            
            # Remove NaN values
            valid_idx = ~(X.isna().any(axis=1) | y.isna())
            X = X[valid_idx]
            y = y[valid_idx]
            
            # Convert to numeric
            X = X.apply(pd.to_numeric, errors='coerce')
            y = pd.to_numeric(y, errors='coerce')
            
            # Remove remaining NaN
            valid_idx = ~(X.isna().any(axis=1) | y.isna())
            X = X[valid_idx]
            y = y[valid_idx]
            
            if len(X) < 10:
                raise ValueError(f"Not enough valid data points. Need at least 10, got {len(X)}")
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
            
            return X_scaled, y, X, scaler
        
        except Exception as e:
            raise Exception(f"Data preparation error: {str(e)}")
    
    def train_linear_regression(self, X, y) -> Dict:
        """Train Linear Regression model"""
        try:
            model = LinearRegression()
            model.fit(X, y)
            score = cross_val_score(model, X, y, cv=5, scoring='r2').mean()
            
            return {
                'model_name': 'Linear Regression',
                'r2_score': score,
                'model': model,
                'importance': dict(zip(X.columns, np.abs(model.coef_)))
            }
        except Exception as e:
            return {'model_name': 'Linear Regression', 'r2_score': -1, 'error': str(e)}
    
    def train_ridge_regression(self, X, y) -> Dict:
        """Train Ridge Regression model"""
        try:
            model = Ridge(alpha=1.0)
            model.fit(X, y)
            score = cross_val_score(model, X, y, cv=5, scoring='r2').mean()
            
            return {
                'model_name': 'Ridge Regression',
                'r2_score': score,
                'model': model,
                'importance': dict(zip(X.columns, np.abs(model.coef_)))
            }
        except Exception as e:
            return {'model_name': 'Ridge Regression', 'r2_score': -1, 'error': str(e)}
    
    def train_lasso_regression(self, X, y) -> Dict:
        """Train Lasso Regression model"""
        try:
            model = Lasso(alpha=0.1, max_iter=1000)
            model.fit(X, y)
            score = cross_val_score(model, X, y, cv=5, scoring='r2').mean()
            
            return {
                'model_name': 'Lasso Regression',
                'r2_score': score,
                'model': model,
                'importance': dict(zip(X.columns, np.abs(model.coef_)))
            }
        except Exception as e:
            return {'model_name': 'Lasso Regression', 'r2_score': -1, 'error': str(e)}
    
    def train_random_forest(self, X, y) -> Dict:
        """Train Random Forest model"""
        try:
            model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            model.fit(X, y)
            score = cross_val_score(model, X, y, cv=5, scoring='r2').mean()
            
            return {
                'model_name': 'Random Forest',
                'r2_score': score,
                'model': model,
                'importance': dict(zip(X.columns, model.feature_importances_))
            }
        except Exception as e:
            return {'model_name': 'Random Forest', 'r2_score': -1, 'error': str(e)}
    
    def train_gradient_boosting(self, X, y) -> Dict:
        """Train Gradient Boosting model"""
        try:
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            score = cross_val_score(model, X, y, cv=5, scoring='r2').mean()
            
            return {
                'model_name': 'Gradient Boosting',
                'r2_score': score,
                'model': model,
                'importance': dict(zip(X.columns, model.feature_importances_))
            }
        except Exception as e:
            return {'model_name': 'Gradient Boosting', 'r2_score': -1, 'error': str(e)}
    
    def train_xgboost(self, X, y) -> Dict:
        """Train XGBoost model"""
        try:
            model = xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            model.fit(X, y)
            score = cross_val_score(model, X, y, cv=5, scoring='r2').mean()
            
            return {
                'model_name': 'XGBoost',
                'r2_score': score,
                'model': model,
                'importance': dict(zip(X.columns, model.feature_importances_))
            }
        except Exception as e:
            return {'model_name': 'XGBoost', 'r2_score': -1, 'error': str(e)}
    
    def train_svr(self, X, y) -> Dict:
        """Train Support Vector Regression model"""
        try:
            model = SVR(kernel='rbf', C=100, epsilon=0.1)
            model.fit(X, y)
            score = cross_val_score(model, X, y, cv=5, scoring='r2').mean()
            
            return {
                'model_name': 'Support Vector Regression',
                'r2_score': score,
                'model': model,
                'importance': dict(zip(X.columns, [0] * len(X.columns)))  # SVR doesn't have feature importance
            }
        except Exception as e:
            return {'model_name': 'Support Vector Regression', 'r2_score': -1, 'error': str(e)}
    
    def analyze_correlations(self, df: pd.DataFrame, target_col: str, feature_cols: List[str]) -> Dict:
        """
        Analyze correlations using multiple models
        Returns best model and feature importance
        """
        try:
            # Prepare data
            X, y, X_original, scaler = self.prepare_data(df, target_col, feature_cols)
            
            # Train all models
            models_to_train = [
                self.train_linear_regression,
                self.train_ridge_regression,
                self.train_lasso_regression,
                self.train_random_forest,
                self.train_gradient_boosting,
                self.train_xgboost,
                self.train_svr
            ]
            
            results = []
            for train_func in models_to_train:
                result = train_func(X, y)
                if 'r2_score' in result and result['r2_score'] > -1:
                    results.append(result)
                    self.model_results[result['model_name']] = result
            
            # Find best model
            best_result = max(results, key=lambda x: x['r2_score'])
            self.best_model = best_result['model']
            self.best_score = best_result['r2_score']
            self.feature_importance = best_result['importance']
            
            # Sort features by importance
            sorted_features = sorted(
                self.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Generate explanations
            explanations = self._generate_explanations(feature_cols, sorted_features)
            
            return {
                'status': 'success',
                'best_model': best_result['model_name'],
                'best_score': float(best_result['r2_score']),
                'score_percentage': float(best_result['r2_score'] * 100),
                'target': target_col,
                'features_ranked': [
                    {
                        'rank': i + 1,
                        'feature': feat,
                        'correlation_score': float(score),
                        'explanation': explanations.get(feat, 'Significant relationship detected')
                    }
                    for i, (feat, score) in enumerate(sorted_features)
                ],
                'all_models': [
                    {
                        'model_name': res['model_name'],
                        'r2_score': float(res['r2_score']),
                        'score_percentage': float(res['r2_score'] * 100)
                    }
                    for res in results
                ]
            }
        except Exception as e:
            log.error(f"Error in correlation analysis: {e}")
            return {'status': 'error', 'message': str(e)}

    
    def _generate_explanations(self, feature_cols: List[str], sorted_features: List[Tuple]) -> Dict:
        """
        Generate simple explanations for correlations
        """
        explanations = {}
        
        for i, (feature, score) in enumerate(sorted_features):
            if i == 0:
                explanations[feature] = "Strongest relationship with target - primary driver"
            elif i < len(sorted_features) // 2:
                explanations[feature] = "Strong correlation - significant impact detected"
            elif i < len(sorted_features) * 0.75:
                explanations[feature] = "Moderate relationship - noticeable influence"
            else:
                explanations[feature] = "Weak correlation - minor influence on target"
        
        return explanations


def analyze(df: pd.DataFrame, target_col: str, feature_cols: List[str]) -> Dict:
    """
    Main function to analyze correlations
    """
    analyzer = CorrelationAnalyzer()
    return analyzer.analyze_correlations(df, target_col, feature_cols)

import numpy as np
from scipy import stats

def detect_outliers(df, columns, method='iqr'):
    """
    Detect outliers in dataset
    Returns: outlier statistics and warnings
    """
    try:
        outlier_stats = {
            'has_outliers': False,
            'outlier_columns': [],
            'outlier_percentages': {},
            'severity': 'none',  # none, low, medium, high
            'warning_message': ''
        }
        
        total_outliers = 0
        total_points = 0
        
        for col in columns:
            if df[col].dtype in ['float64', 'int64']:
                data = df[col].dropna()
                
                if method == 'iqr':
                    Q1 = data.quantile(0.25)
                    Q3 = data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outlier_mask = (data < lower_bound) | (data > upper_bound)
                
                outlier_count = outlier_mask.sum()
                outlier_percentage = (outlier_count / len(data)) * 100
                total_outliers += outlier_count
                total_points += len(data)
                
                if outlier_count > 0:
                    outlier_stats['has_outliers'] = True
                    outlier_stats['outlier_columns'].append(col)
                    outlier_stats['outlier_percentages'][col] = round(outlier_percentage, 2)
        
        # Calculate overall severity
        if total_points > 0:
            overall_outlier_pct = (total_outliers / total_points) * 100
            
            if overall_outlier_pct > 20:
                outlier_stats['severity'] = 'high'
                outlier_stats['warning_message'] = f"⚠️ HIGH: Data contains {overall_outlier_pct:.1f}% outliers. This may significantly impact model accuracy. Consider data cleaning or robust regression methods."
            
            elif overall_outlier_pct > 10:
                outlier_stats['severity'] = 'medium'
                outlier_stats['warning_message'] = f"⚠️ MEDIUM: Data contains {overall_outlier_pct:.1f}% outliers. Models may be affected. Review the data distribution."
            
            elif overall_outlier_pct > 5:
                outlier_stats['severity'] = 'low'
                outlier_stats['warning_message'] = f"ℹ️ LOW: Data contains {overall_outlier_pct:.1f}% outliers. Normal for most datasets."
            
            else:
                outlier_stats['warning_message'] = "✅ Data quality is good. Very few outliers detected."
        
        return outlier_stats
    
    except Exception as e:
        log.error(f"Error detecting outliers: {e}")
        return {'has_outliers': False, 'error': str(e)}

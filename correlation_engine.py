"""
Correlation Analysis Engine
Analyzes relationships between features and target variable
Automatically selects best model for analysis
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
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


def detect_outliers(df: pd.DataFrame, columns: List[str]) -> Dict:
    """
    Detect outliers in specified columns using IQR method
    Returns warning severity: 'high', 'medium', 'low', 'none'
    """
    outliers_found = {}
    affected_columns = []
    
    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue
            
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        outlier_count = outlier_mask.sum()
        outlier_percentage = (outlier_count / len(df)) * 100
        
        if outlier_percentage > 0:
            affected_columns.append(col)
            outliers_found[col] = {
                'count': int(outlier_count),
                'percentage': round(outlier_percentage, 2),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound)
            }
    
    # Determine severity
    if not affected_columns:
        severity = 'none'
        warning_message = '✅ No outliers detected - Data is clean'
    else:
        avg_outlier_percentage = np.mean([v['percentage'] for v in outliers_found.values()])
        
        if avg_outlier_percentage > 10:
            severity = 'high'
            warning_message = f'⚠️ HIGH: {len(affected_columns)} columns have >10% outliers'
        elif avg_outlier_percentage > 5:
            severity = 'medium'
            warning_message = f'⚡ MEDIUM: {len(affected_columns)} columns have 5-10% outliers'
        else:
            severity = 'low'
            warning_message = f'ℹ️ LOW: {len(affected_columns)} columns have <5% outliers'
    
    return {
        'warning_message': warning_message,
        'severity': severity,
        'outlier_columns': affected_columns,
        'outlier_percentages': outliers_found,
        'total_affected_columns': len(affected_columns)
    }


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
    
    def train_linear_regression(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train linear regression and return results"""
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        
        self.feature_importance = dict(zip(range(len(model.coef_)), np.abs(model.coef_)))
        
        return {
            'model_name': 'Linear Regression',
            'model': model,
            'r2_score': r2,
            'importance': self.feature_importance
        }
    
    def train_ridge_regression(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train ridge regression and return results"""
        model = Ridge(alpha=1.0)
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        
        self.feature_importance = dict(zip(range(len(model.coef_)), np.abs(model.coef_)))
        
        return {
            'model_name': 'Ridge Regression',
            'model': model,
            'r2_score': r2,
            'importance': self.feature_importance
        }
    
    def train_lasso_regression(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train lasso regression and return results"""
        model = Lasso(alpha=0.1)
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        
        self.feature_importance = dict(zip(range(len(model.coef_)), np.abs(model.coef_)))
        
        return {
            'model_name': 'Lasso Regression',
            'model': model,
            'r2_score': r2,
            'importance': self.feature_importance
        }
    
    def train_random_forest(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train random forest and return results"""
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        
        self.feature_importance = dict(zip(range(len(model.feature_importances_)), 
                                          model.feature_importances_))
        
        return {
            'model_name': 'Random Forest',
            'model': model,
            'r2_score': r2,
            'importance': self.feature_importance
        }
    
    def train_gradient_boosting(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train gradient boosting and return results"""
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        
        self.feature_importance = dict(zip(range(len(model.feature_importances_)), 
                                          model.feature_importances_))
        
        return {
            'model_name': 'Gradient Boosting',
            'model': model,
            'r2_score': r2,
            'importance': self.feature_importance
        }
    
    def train_xgboost(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train XGBoost and return results"""
        model = xgb.XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        
        self.feature_importance = dict(zip(range(len(model.feature_importances_)), 
                                          model.feature_importances_))
        
        return {
            'model_name': 'XGBoost',
            'model': model,
            'r2_score': r2,
            'importance': self.feature_importance
        }
    
    def train_svr(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train SVR and return results"""
        model = SVR(kernel='rbf', C=100, epsilon=0.1)
        model.fit(X, y)
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        
        self.feature_importance = {}
        
        return {
            'model_name': 'Support Vector Regression',
            'model': model,
            'r2_score': r2,
            'importance': self.feature_importance
        }
    
    def prepare_data(self, df: pd.DataFrame, target_col: str, 
                    feature_cols: List[str]) -> Tuple[np.ndarray, np.ndarray, 
                                                       np.ndarray, StandardScaler]:
        """Prepare data for model training"""
        X = df[feature_cols].values
        y = df[target_col].values
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return X_scaled, y, X, scaler
    
    def _generate_explanations(self, feature_cols: List[str], 
                              sorted_features: List[Tuple]) -> Dict[str, str]:
        """
        Generate simple explanations for feature correlations
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
    
    def analyze_correlations(self, df: pd.DataFrame, target_col: str, 
                            feature_cols: List[str]) -> Dict:
        """
        Main function to analyze correlations
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
                if result['r2_score'] > -1:
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
            
            # Add outlier detection
            outlier_info = detect_outliers(df, feature_cols + [target_col])
            
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
                ],
                'outlier_detection': {
                    'warning_message': outlier_info['warning_message'],
                    'severity': outlier_info['severity'],
                    'affected_columns': outlier_info['outlier_columns'],
                    'outlier_details': outlier_info['outlier_percentages'],
                    'total_affected': outlier_info['total_affected_columns']
                }
            }
        except Exception as e:
            log.error(f"Error in correlation analysis: {e}")
            return {'status': 'error', 'message': str(e)}


# Module-level function for external use
def analyze(df: pd.DataFrame, target_col: str, feature_cols: List[str]) -> Dict:
    """
    Public API for correlation analysis
    """
    analyzer = CorrelationAnalyzer()
    
    # Reset state to ensure clean analysis
    analyzer.best_model = None
    analyzer.best_score = -1
    analyzer.model_results = {}
    analyzer.feature_importance = {}
    
    result = analyzer.analyze_correlations(df, target_col, feature_cols)
    
    # ADD THIS CODE BLOCK to the analyze() function:
    # Calculate correlations for new visualizations

    if result.get('status') == 'success':
        # 1. CORRELATION MATRIX - shows all feature correlations
        corr_matrix = df[feature_cols + [target_col]].corr()
        correlation_matrix_dict = corr_matrix.to_dict()
        
        # 2. FEATURE CORRELATIONS WITH TARGET - sorted by strength
        feature_target_corr = corr_matrix[target_col].drop(target_col).abs().sort_values(ascending=False)
        feature_correlations_dict = feature_target_corr.to_dict()
        
        # 3. ACTUAL vs PREDICTED - get predictions from best model
        X_all = df[feature_cols].values
        scaler = StandardScaler()
        X_scaled_all = scaler.fit_transform(X_all)
        y_predicted = analyzer.best_model.predict(X_scaled_all)
        y_actual = df[target_col].values
        
        # Add to result
        result['chart_data'] = {
            'models': [r['model_name'] for r in result.get('all_models', [])],
            'scores': [r['r2_score'] for r in result.get('all_models', [])],
            'features': [f['feature'] for f in result.get('features_ranked', [])],
            'importance': [f['correlation_score'] for f in result.get('features_ranked', [])],
            
            # NEW DATA FOR ENHANCED CHARTS
            'correlation_matrix': correlation_matrix_dict,
            'feature_correlations': feature_correlations_dict,
            'predictions': {
                'actual': y_actual.tolist(),
                'predicted': y_predicted.tolist()
            }
        }
    
    return result



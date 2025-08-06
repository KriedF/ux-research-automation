"""
Data Cleaning Utilities for UX Research Automation
Reusable functions for common data processing tasks
"""

import pandas as pd
import numpy as np
import re

def clean_survey_data(df):
    """
    Clean common issues in survey data exports
    
    Args:
        df: Raw survey DataFrame
    Returns:
        Cleaned DataFrame
    """
    # Remove completely empty rows
    df = df.dropna(how='all')
    
    # Clean column names (remove spaces, special characters)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Convert rating columns to numeric
    rating_cols = [col for col in df.columns if 'rating' in col or 'score' in col]
    for col in rating_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Clean text columns
    text_cols = df.select_dtypes(include=['object']).columns
    for col in text_cols:
        if col not in rating_cols:
            df[col] = df[col].astype(str).str.strip()
    
    return df

def standardize_ratings(df, rating_col, target_scale=5):
    """
    Standardize rating scales (e.g., convert 1-10 to 1-5)
    
    Args:
        df: DataFrame with rating column
        rating_col: Column name with ratings
        target_scale: Target scale (default 5)
    Returns:
        DataFrame with standardized ratings
    """
    if rating_col not in df.columns:
        return df
    
    current_max = df[rating_col].max()
    if current_max != target_scale:
        # Scale ratings proportionally
        df[f'{rating_col}_standardized'] = (df[rating_col] / current_max) * target_scale
        df[f'{rating_col}_standardized'] = df[f'{rating_col}_standardized'].round()
    
    return df

def detect_data_quality_issues(df):
    """
    Detect common data quality issues
    
    Args:
        df: DataFrame to check
    Returns:
        Dictionary of quality issues found
    """
    issues = {}
    
    # Check for missing data
    missing_pct = (df.isnull().sum() / len(df)) * 100
    high_missing = missing_pct[missing_pct > 20]
    if len(high_missing) > 0:
        issues['high_missing_data'] = high_missing.to_dict()
    
    # Check for duplicate responses
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        issues['duplicate_responses'] = duplicates
    
    # Check for outliers in rating columns
    rating_cols = [col for col in df.columns if 'rating' in col]
    for col in rating_cols:
        if col in df.columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))]
            if len(outliers) > len(df) * 0.05:  # More than 5% outliers
                issues[f'{col}_outliers'] = len(outliers)
    
    return issues

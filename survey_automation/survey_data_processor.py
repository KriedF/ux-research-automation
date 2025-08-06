```python
"""
Survey Data Processor - UX Research Automation
Automatically process survey exports from Qualtrics, SurveyMonkey, etc.
Converts raw survey data into clean analysis and visualizations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

class SurveyDataProcessor:
    def __init__(self, file_path):
        """
        Initialize survey processor with data file
        
        Args:
            file_path (str): Path to survey data CSV file
        """
        self.file_path = file_path
        self.data = None
        self.processed_data = None
        self.insights = {}
        
    def load_data(self):
        """Load survey data from CSV file"""
        try:
            self.data = pd.read_csv(self.file_path)
            print(f"✅ Successfully loaded {len(self.data)} survey responses")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def clean_data(self):
        """Clean and prepare survey data for analysis"""
        if self.data is None:
            print("❌ No data loaded. Run load_data() first.")
            return False
            
        # Remove empty responses
        initial_count = len(self.data)
        self.data = self.data.dropna(how='all')
        
        # Convert date columns
        if 'survey_date' in self.data.columns:
            self.data['survey_date'] = pd.to_datetime(self.data['survey_date'])
            
        # Standardize rating columns (handle different scales)
        rating_columns = [col for col in self.data.columns if 'rating' in col.lower()]
        for col in rating_columns:
            self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
            
        final_count = len(self.data)
        print(f"✅ Data cleaned: {initial_count} → {final_count} responses")
        
        self.processed_data = self.data
        return True
    
    def calculate_satisfaction_metrics(self):
        """Calculate key satisfaction metrics from survey data"""
        if self.processed_data is None:
            print("❌ No processed data. Run clean_data() first.")
            return None
            
        metrics = {}
        
        # Find rating columns
        rating_columns = [col for col in self.processed_data.columns if 'rating' in col.lower()]
        
        for col in rating_columns:
            if col in self.processed_data.columns:
                # Basic statistics
                metrics[col] = {
                    'mean': round(self.processed_data[col].mean(), 2),
                    'median': self.processed_data[col].median(),
                    'count': self.processed_data[col].count(),
                    'std': round(self.processed_data[col].std(), 2)
                }
                
                # Satisfaction rate (4-5 on 5-point scale)
                if self.processed_data[col].max() <= 5:
                    satisfied = self.processed_data[col] >= 4
                    metrics[col]['satisfaction_rate'] = round(
                        (satisfied.sum() / len(satisfied)) * 100, 1
                    )
                
                # Net Promoter Score style (9-10 promoters, 0-6 detractors on 10-point scale)
                if self.processed_data[col].max() <= 10:
                    promoters = self.processed_data[col] >= 9
                    detractors = self.processed_data[col] <= 6
                    nps = ((promoters.sum() - detractors.sum()) / len(self.processed_data[col])) * 100
                    metrics[col]['nps_score'] = round(nps, 1)
        
        self.insights['satisfaction_metrics'] = metrics
        return metrics
    
    def analyze_by_segments(self, segment_column):
        """Analyze satisfaction by user segments"""
        if segment_column not in self.processed_data.columns:
            print(f"❌ Column '{segment_column}' not found in data")
            return None
            
        segment_analysis = {}
        rating_columns = [col for col in self.processed_data.columns if 'rating' in col.lower()]
        
        for segment in self.processed_data[segment_column].unique():
            segment_data = self.processed_data[self.processed_data[segment_column] == segment]
            segment_metrics = {}
            
            for rating_col in rating_columns:
                if rating_col in segment_data.columns:
                    segment_metrics[rating_col] = {
                        'mean': round(segment_data[rating_col].mean(), 2),
                        'count': segment_data[rating_col].count(),
                        'satisfaction_rate': round(
                            ((segment_data[rating_col] >= 4).sum() / len(segment_data)) * 100, 1
                        ) if segment_data[rating_col].max() <= 5 else None
                    }
            
            segment_analysis[segment] = segment_metrics
        
        self.insights['segment_analysis'] = segment_analysis
        return segment_analysis
    
    def create_visualizations(self, output_path='survey_analysis_charts.png'):
        """Create automated visualizations of survey results"""
        if self.processed_data is None:
            print("❌ No processed data available for visualization")
            return False
            
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Survey Analysis Dashboard', fontsize=16, fontweight='bold')
        
        rating_columns = [col for col in self.processed_data.columns if 'rating' in col.lower()]
        
        if len(rating_columns) > 0:
            # 1. Rating Distribution
            if len(rating_columns) >= 1:
                self.processed_data[rating_columns[0]].hist(bins=5, ax=axes[0,0])
                axes[0,0].set_title(f'{rating_columns[0]} Distribution')
                axes[0,0].set_xlabel('Rating')
                axes[0,0].set_ylabel('Frequency')
            
            # 2. Satisfaction Rates by Feature (if multiple rating columns)
            if len(rating_columns) > 1:
                satisfaction_rates = []
                feature_names = []
                
                for col in rating_columns[:4]:  # Limit to 4 features for readability
                    if self.processed_data[col].max() <= 5:
                        rate = ((self.processed_data[col] >= 4).sum() / len(self.processed_data)) * 100
                        satisfaction_rates.append(rate)
                        feature_names.append(col.replace('_rating', '').title())
                
                if satisfaction_rates:
                    axes[0,1].bar(feature_names, satisfaction_rates)
                    axes[0,1].set_title('Satisfaction Rates by Feature')
                    axes[0,1].set_ylabel('Satisfaction %')
                    axes[0,1].tick_params(axis='x', rotation=45)
            
            # 3. Response Timeline (if date column exists)
            if 'survey_date' in self.processed_data.columns:
                daily_responses = self.processed_data.groupby(
                    self.processed_data['survey_date'].dt.date
                ).size()
                daily_responses.plot(ax=axes[1,0])
                axes[1,0].set_title('Survey Responses Over Time')
                axes[1,0].set_xlabel('Date')
                axes[1,0].set_ylabel('Number of Responses')
            
            # 4. Rating Correlation Matrix (if multiple ratings)
            if len(rating_columns) > 1:
                correlation_matrix = self.processed_data[rating_columns].corr()
                sns.heatmap(correlation_matrix, annot=True, ax=axes[1,1], cmap='coolwarm')
                axes[1,1].set_title('Rating Correlations')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Visualizations saved to {output_path}")
        
        return True
    
    def generate_executive_summary(self):
        """Generate executive summary of survey findings"""
        if not self.insights:
            print("❌ No insights calculated. Run analysis methods first.")
            return None
            
        summary = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_responses': len(self.processed_data),
            'key_findings': [],
            'recommendations': []
        }
        
        # Extract key findings from satisfaction metrics
        if 'satisfaction_metrics' in self.insights:
            metrics = self.insights['satisfaction_metrics']
            
            for feature, data in metrics.items():
                if 'satisfaction_rate' in data:
                    rate = data['satisfaction_rate']
                    if rate >= 80:
                        summary['key_findings'].append(f"✅ {feature}: {rate}% satisfaction (Excellent)")
                    elif rate >= 60:
                        summary['key_findings'].append(f"⚠️ {feature}: {rate}% satisfaction (Good)")  
                    else:
                        summary['key_findings'].append(f"❌ {feature}: {rate}% satisfaction (Needs Improvement)")
        
        # Generate recommendations based on findings
        low_satisfaction_features = []
        for feature, data in self.insights.get('satisfaction_metrics', {}).items():
            if 'satisfaction_rate' in data and data['satisfaction_rate'] < 70:
                low_satisfaction_features.append(feature)
        
        if low_satisfaction_features:
            summary['recommendations'].append(
                f"Priority improvement needed for: {', '.join(low_satisfaction_features)}"
            )
        
        return summary

def main():
    """Example usage of the Survey Data Processor"""
    print("🚀 Starting Survey Data Processing Automation")
    print("=" * 50)
    
    # Create sample data if it doesn't exist
    sample_data = {
        'user_id': [f'user_{i:03d}' for i in range(1, 51)],
        'voice_search_rating': np.random.choice([1,2,3,4,5], 50, p=[0.1,0.1,0.2,0.3,0.3]),
        'interface_rating': np.random.choice([1,2,3,4,5], 50, p=[0.05,0.1,0.15,0.35,0.35]),
        'recommendations_rating': np.random.choice([1,2,3,4,5], 50, p=[0.08,0.12,0.25,0.3,0.25]),
        'survey_date': pd.date_range('2024-07-01', periods=50, freq='D')[:50],
        'user_type': np.random.choice(['new', 'returning', 'power_user'], 50, p=[0.3,0.5,0.2])
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('survey_automation/sample_survey_data.csv', index=False)
    print("✅ Created sample survey data")
    
    # Initialize processor
    processor = SurveyDataProcessor('survey_automation/sample_survey_data.csv')
    
    # Run the automation pipeline
    if processor.load_data():
        if processor.clean_data():
            # Calculate metrics
            metrics = processor.calculate_satisfaction_metrics()
            print("\n📊 Satisfaction Metrics:")
            for feature, data in metrics.items():
                print(f"  {feature}: {data['satisfaction_rate']}% satisfied (avg: {data['mean']}/5)")
            
            # Segment analysis
            segments = processor.analyze_by_segments('user_type')
            print("\n👥 Segment Analysis:")
            for segment, data in segments.items():
                avg_satisfaction = np.mean([
                    data[col]['satisfaction_rate'] for col in data 
                    if data[col]['satisfaction_rate'] is not None
                ])
                print(f"  {segment}: {avg_satisfaction:.1f}% average satisfaction")
            
            # Create visualizations
            processor.create_visualizations('survey_analysis_dashboard.png')
            
            # Generate summary
            summary = processor.generate_executive_summary()
            print("\n📋 Executive Summary:")
            print(f"  Total Responses: {summary['total_responses']}")
            for finding in summary['key_findings']:
                print(f"  {finding}")
    
    print("\n🎉 Survey processing automation complete!")
    print("Time saved: ~2.5 hours of manual analysis → 30 seconds automated")

if __name__ == "__main__":
    main()

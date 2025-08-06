"""
Research Report Generator - UX Research Automation
Automatically generates professional research reports from data analysis
Saves hours of manual report formatting and chart creation
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os

class ResearchReportGenerator:
    def __init__(self, data_source):
        """
        Initialize report generator with data source
        
        Args:
            data_source: Path to data file or processed analysis results
        """
        self.data_source = data_source
        self.report_data = {}
        self.template_path = "report_automation/report_template.html"
        
    def load_analysis_results(self, analysis_results):
        """Load processed analysis results"""
        self.report_data = analysis_results
        return True
    
    def generate_charts(self, output_dir="report_automation/charts/"):
        """Generate charts for the research report"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        charts_created = []
        
        # Chart 1: Satisfaction Overview
        if 'satisfaction_metrics' in self.report_data:
            features = []
            satisfaction_rates = []
            
            for feature, metrics in self.report_data['satisfaction_metrics'].items():
                if 'satisfaction_rate' in metrics:
                    features.append(feature.replace('_rating', '').title())
                    satisfaction_rates.append(metrics['satisfaction_rate'])
            
            if features:
                plt.figure(figsize=(10, 6))
                bars = plt.bar(features, satisfaction_rates, color=['#2ecc71' if x >= 70 else '#e74c3c' for x in satisfaction_rates])
                plt.title('User Satisfaction by Feature', fontsize=16, fontweight='bold')
                plt.ylabel('Satisfaction Rate (%)')
                plt.ylim(0, 100)
                
                # Add percentage labels on bars
                for bar, rate in zip(bars, satisfaction_rates):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                            f'{rate}%', ha='center', va='bottom', fontweight='bold')
                
                plt.tight_layout()
                chart_path = os.path.join(output_dir, 'satisfaction_overview.png')
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                charts_created.append(chart_path)
                plt.close()
        
        return charts_created
    
    def create_html_report(self, output_path="research_report.html"):
        """Generate HTML research report"""
        
        # Basic HTML template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UX Research Report - Automated Generation</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; line-height: 1.6; color: #333; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { margin: 0; font-size: 28px; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .section { background: white; padding: 25px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section h2 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .metric-box { background: #f8f9fa; padding: 20px; border-left: 4px solid #3498db; margin: 15px 0; border-radius: 5px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .metric-label { color: #7f8c8d; font-size: 14px; }
        .recommendation { background: #e8f5e8; padding: 15px; border-left: 4px solid #27ae60; margin: 10px 0; border-radius: 5px; }
        .warning { background: #fef9e7; padding: 15px; border-left: 4px solid #f39c12; margin: 10px 0; border-radius: 5px; }
        .critical { background: #fdeaea; padding: 15px; border-left: 4px solid #e74c3c; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>UX Research Report</h1>
        <p>Automated Analysis Generated on {timestamp}</p>
        <p>Total Survey Responses Analyzed: {total_responses}</p>
    </div>
    
    <div class="section">
        <h2>📊 Executive Summary</h2>
        <p>This report presents automated analysis of user feedback data, highlighting key satisfaction metrics and actionable insights for product improvement.</p>
        
        <div class="metric-box">
            <div class="metric-value">{avg_satisfaction}%</div>
            <div class="metric-label">Average User Satisfaction</div>
        </div>
        
        <div class="metric-box">
            <div class="metric-value">{total_responses}</div>
            <div class="metric-label">Survey Responses Analyzed</div>
        </div>
    </div>
    
    <div class="section">
        <h2>🎯 Key Findings</h2>
        {findings_html}
    </div>
    
    <div class="section">
        <h2>💡 Recommendations</h2>
        {recommendations_html}
    </div>
    
    <div class="section">
        <h2>📈 Detailed Metrics</h2>
        {detailed_metrics_html}
    </div>
    
    <div class="section">
        <h2>🔧 Methodology</h2>
        <p><strong>Data Source:</strong> Survey responses collected through automated processing pipeline</p>
        <p><strong>Analysis Method:</strong> Automated statistical analysis with Python data processing</p>
        <p><strong>Satisfaction Calculation:</strong> Percentage of responses rated 4-5 on 5-point scale</p>
        <p><strong>Report Generation:</strong> Automated using Python research workflow tools</p>
    </div>
    
    <div class="section" style="background: #f8f9fa; text-align: center; color: #7f8c8d;">
        <p>This report was generated automatically using UX Research Automation tools</p>
        <p>Time saved: ~2 hours of manual report creation → 30 seconds automated generation</p>
    </div>
</body>
</html>
"""
        
        # Process data for template
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        total_responses = self.report_data.get('total_responses', 0)
        
        # Calculate average satisfaction
        if 'satisfaction_metrics' in self.report_data:
            satisfaction_rates = [
                metrics.get('satisfaction_rate', 0) 
                for metrics in self.report_data['satisfaction_metrics'].values()
                if 'satisfaction_rate' in metrics
            ]
            avg_satisfaction = round(sum(satisfaction_rates) / len(satisfaction_rates), 1) if satisfaction_rates else 0
        else:
            avg_satisfaction = 0
        
        # Generate findings HTML
        findings_html = ""
        if 'key_findings' in self.report_data:
            for finding in self.report_data['key_findings']:
                if '✅' in finding:
                    findings_html += f'<div class="recommendation">{finding}</div>'
                elif '⚠️' in finding:
                    findings_html += f'<div class="warning">{finding}</div>'
                elif '❌' in finding:
                    findings_html += f'<div class="critical">{finding}</div>'
                else:
                    findings_html += f'<p>{finding}</p>'
        
        # Generate recommendations HTML
        recommendations_html = ""
        if 'recommendations' in self.report_data:
            for rec in self.report_data['recommendations']:
                recommendations_html += f'<div class="recommendation">💡 {rec}</div>'
        
        # Generate detailed metrics HTML
        detailed_metrics_html = ""
        if 'satisfaction_metrics' in self.report_data:
            for feature, metrics in self.report_data['satisfaction_metrics'].items():
                feature_name = feature.replace('_rating', '').title()
                satisfaction_rate = metrics.get('satisfaction_rate', 0)
                mean_score = metrics.get('mean', 0)
                response_count = metrics.get('count', 0)
                
                detailed_metrics_html += f"""
                <div class="metric-box">
                    <h4>{feature_name}</h4>
                    <p><strong>Satisfaction Rate:</strong> {satisfaction_rate}%</p>
                    <p><strong>Average Score:</strong> {mean_score}/5</p>
                    <p><strong>Responses:</strong> {response_count}</p>
                </div>
                """
        
        # Fill template
        html_content = html_template.format(
            timestamp=timestamp,
            total_responses=total_responses,
            avg_satisfaction=avg_satisfaction,
            findings_html=findings_html,
            recommendations_html=recommendations_html,
            detailed_metrics_html=detailed_metrics_html
        )
        
        # Save report
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Research report generated: {output_path}")
        return output_path

def main():
    """Example usage of the Research Report Generator"""
    print("📋 Starting Automated Research Report Generation")
    print("=" * 50)
    
    # Sample analysis results (normally comes from data processing)
    sample_results = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_responses': 150,
        'satisfaction_metrics': {
            'voice_search_rating': {
                'mean': 3.2,
                'satisfaction_rate': 65.3,
                'count': 150
            },
            'interface_rating': {
                'mean': 4.1,
                'satisfaction_rate': 78.7,
                'count': 150
            },
            'recommendations_rating': {
                'mean': 3.8,
                'satisfaction_rate': 72.0,
                'count': 150
            }
        },
        'key_findings': [
            '✅ Interface: 78.7% satisfaction (Good performance)',
            '⚠️ Recommendations: 72.0% satisfaction (Room for improvement)', 
            '❌ Voice Search: 65.3% satisfaction (Needs immediate attention)'
        ],
        'recommendations': [
            'Prioritize voice search improvements - lowest satisfaction score',
            'Investigate interface success factors for other features',
            'Consider A/B testing recommendations algorithm improvements'
        ]
    }
    
    # Generate report
    generator = ResearchReportGenerator("sample_data")
    generator.load_analysis_results(sample_results)
    
    # Create charts
    charts = generator.generate_charts()
    print(f"✅ Generated {len(charts)} visualization charts")
    
    # Generate HTML report
    report_path = generator.create_html_report("automated_research_report.html")
    
    print("\n🎉 Report generation complete!")
    print(f"📄 Report saved to: {report_path}")
    print("⏱️ Time saved: ~2 hours of manual work → 30 seconds automated")

if __name__ == "__main__":
    main()

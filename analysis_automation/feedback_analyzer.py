"""
Feedback Analyzer - UX Research Automation
Automatically analyze open-ended user feedback using sentiment analysis
Categorizes themes and generates insights from qualitative data at scale
"""

from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import Counter
from datetime import datetime

class FeedbackAnalyzer:
    def __init__(self):
        """Initialize feedback analyzer"""
        self.feedback_data = None
        self.analysis_results = {}
        
    def load_feedback(self, feedback_list):
        """
        Load feedback data for analysis
        
        Args:
            feedback_list: List of feedback strings or pandas DataFrame
        """
        if isinstance(feedback_list, pd.DataFrame):
            self.feedback_data = feedback_list
        else:
            self.feedback_data = pd.DataFrame({'feedback': feedback_list})
        
        print(f"✅ Loaded {len(self.feedback_data)} feedback responses")
        return True
    
    def analyze_sentiment(self):
        """Perform sentiment analysis on all feedback"""
        if self.feedback_data is None:
            print("❌ No feedback data loaded")
            return None
            
        sentiments = []
        sentiment_scores = []
        
        for feedback in self.feedback_data['feedback']:
            if pd.isna(feedback):
                sentiments.append('neutral')
                sentiment_scores.append(0)
                continue
                
            blob = TextBlob(str(feedback))
            polarity = blob.sentiment.polarity
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'  
            else:
                sentiment = 'neutral'
                
            sentiments.append(sentiment)
            sentiment_scores.append(polarity)
        
        self.feedback_data['sentiment'] = sentiments
        self.feedback_data['sentiment_score'] = sentiment_scores
        
        # Calculate sentiment distribution
        sentiment_dist = pd.Series(sentiments).value_counts()
        sentiment_percentages = (sentiment_dist / len(sentiments) * 100).round(1)
        
        self.analysis_results['sentiment_analysis'] = {
            'distribution': sentiment_dist.to_dict(),
            'percentages': sentiment_percentages.to_dict(),
            'average_sentiment': round(sum(sentiment_scores) / len(sentiment_scores), 3)
        }
        
        print("✅ Sentiment analysis complete")
        return self.analysis_results['sentiment_analysis']
    
    def extract_themes(self, min_frequency=2):
        """Extract common themes from feedback using keyword analysis"""
        if self.feedback_data is None:
            print("❌ No feedback data loaded")
            return None
            
        # Common UX/product keywords to look for
        ux_keywords = [
            'easy', 'difficult', 'confusing', 'intuitive', 'simple', 'complicated',
            'fast', 'slow', 'quick', 'loading', 'responsive', 'laggy',
            'design', 'interface', 'layout', 'navigation', 'menu', 'button',
            'search', 'find', 'discover', 'browse', 'filter', 'sort',
            'recommendation', 'suggest', 'personalize', 'relevant', 'accurate',
            'bug', 'error', 'crash', 'broken', 'issue', 'problem',
            'love', 'hate', 'like', 'dislike', 'amazing', 'terrible', 'great', 'awful'
        ]
        
        # Extract keywords from all feedback
        all_keywords = []
        for feedback in self.feedback_data['feedback']:
            if pd.isna(feedback):
                continue
                
            # Clean and tokenize text
            text = str(feedback).lower()
            words = re.findall(r'\b\w+\b', text)
            
            # Find UX keywords
            found_keywords = [word for word in words if word in ux_keywords]
            all_keywords.extend(found_keywords)
        
        # Count keyword frequency
        keyword_counts = Counter(all_keywords)
        common_themes = {k: v for k, v in keyword_counts.items() if v >= min_frequency}
        
        # Categorize themes
        theme_categories = {
            'usability': ['easy', 'difficult', 'confusing', 'intuitive', 'simple', 'complicated'],
            'performance': ['fast', 'slow', 'quick', 'loading', 'responsive', 'laggy'],
            'design': ['design', 'interface', 'layout', 'navigation', 'menu', 'button'],
            'functionality': ['search', 'find', 'discover', 'browse', 'filter', 'sort'],
            'personalization': ['recommendation', 'suggest', 'personalize', 'relevant', 'accurate'],
            'technical_issues': ['bug', 'error', 'crash', 'broken', 'issue', 'problem'],
            'sentiment': ['love', 'hate', 'like', 'dislike', 'amazing', 'terrible', 'great', 'awful']
        }
        
        categorized_themes = {}
        for category, keywords in theme_categories.items():
            category_count = sum(common_themes.get(keyword, 0) for keyword in keywords)
            if category_count > 0:
                categorized_themes[category] = category_count
        
        self.analysis_results['theme_analysis'] = {
            'common_keywords': common_themes,
            'theme_categories': categorized_themes,
            'total_keywords_found': len(all_keywords)
        }
        
        print("✅ Theme extraction complete")
        return self.analysis_results['theme_analysis']
    
    def identify_priority_issues(self):
        """Identify priority issues based on negative sentiment and frequency"""
        if 'sentiment_analysis' not in self.analysis_results:
            print("❌ Run sentiment analysis first")
            return None
            
        # Find negative feedback
        negative_feedback = self.feedback_data[self.feedback_data['sentiment'] == 'negative']
        
        if len(negative_feedback) == 0:
            return {'message': 'No negative feedback found'}
        
        # Extract common issues from negative feedback
        negative_keywords = []
        for feedback in negative_feedback['feedback']:
            if pd.isna(feedback):
                continue
            text = str(feedback).lower()
            words = re.findall(r'\b\w+\b', text)
            negative_keywords.extend(words)
        
        # Focus on problem-related keywords
        problem_keywords = [
            'slow', 'confusing', 'difficult', 'complicated', 'broken', 'error', 
            'bug', 'crash', 'loading', 'laggy', 'terrible', 'awful', 'hate',
            'problem', 'issue', 'frustrating', 'annoying'
        ]
        
        negative_issues = Counter([kw for kw in negative_keywords if kw in problem_keywords])
        
        priority_issues = []
        for issue, count in negative_issues.most_common(5):
            percentage = (count / len(self.feedback_data)) * 100
            priority_issues.append({
                'issue': issue,
                'frequency': count,
                'percentage': round(percentage, 1)
            })
        
        self.analysis_results['priority_issues'] = priority_issues
        print("✅ Priority issues identified")
        return priority_issues
    
    def generate_insights_report(self):
        """Generate comprehensive insights report"""
        if not self.analysis_results:
            print("❌ No analysis results available")
            return None
            
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_feedback': len(self.feedback_data),
            'summary': {},
            'key_insights': [],
            'recommendations': []
        }
        
        # Sentiment summary
        if 'sentiment_analysis' in self.analysis_results:
            sentiment = self.analysis_results['sentiment_analysis']
            report['summary']['sentiment'] = sentiment['percentages']
            
            # Generate insights based on sentiment
            pos_pct = sentiment['percentages'].get('positive', 0)
            neg_pct = sentiment['percentages'].get('negative', 0)
            
            if pos_pct > 60:
                report['key_insights'].append(f"✅ Strong positive sentiment: {pos_pct}% of feedback is positive")
            elif neg_pct > 30:
                report['key_insights'].append(f"⚠️ High negative sentiment: {neg_pct}% of feedback is negative")
            
        # Theme insights
        if 'theme_analysis' in self.analysis_results:
            themes = self.analysis_results['theme_analysis']['theme_categories']
            top_theme = max(themes.items(), key=lambda x: x[1]) if themes else None
            
            if top_theme:
                report['key_insights'].append(f"🎯 Most discussed theme: {top_theme[0]} ({top_theme[1]} mentions)")
        
        # Priority issues
        if 'priority_issues' in self.analysis_results:
            issues = self.analysis_results['priority_issues']
            if issues and not isinstance(issues, dict):
                top_issue = issues[0]
                report['key_insights'].append(f"❌ Top user complaint: '{top_issue['issue']}' mentioned by {top_issue['percentage']}% of users")
                
                # Generate recommendations
                issue_type = top_issue['issue']
                if issue_type in ['slow', 'loading', 'laggy']:
                    report['recommendations'].append("Investigate performance optimization opportunities")
                elif issue_type in ['confusing', 'difficult', 'complicated']:
                    report['recommendations'].append("Consider UX/UI simplification and user testing")
                elif issue_type in ['broken', 'error', 'bug', 'crash']:
                    report['recommendations'].append("Prioritize bug fixes and technical stability improvements")
        
        return report
    
    def create_visualization(self, output_path='feedback_analysis.png'):
        """Create visualizations of feedback analysis"""
        if not self.analysis_results:
            print("❌ No analysis results to visualize")
            return False
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Automated Feedback Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Sentiment Distribution
        if 'sentiment_analysis' in self.analysis_results:
            sentiment_data = self.analysis_results['sentiment_analysis']['distribution']
            colors = {'positive': '#2ecc71', 'negative': '#e74c3c', 'neutral': '#95a5a6'}
            
            labels = list(sentiment_data.keys())
            values = list(sentiment_data.values())
            pie_colors = [colors.get(label, '#95a5a6') for label in labels]
            
            axes[0,0].pie(values, labels=labels, colors=pie_colors, autopct='%1.1f%%', startangle=90)
            axes[0,0].set_title('Sentiment Distribution')
        
        # 2. Theme Categories
        if 'theme_analysis' in self.analysis_results:
            themes = self.analysis_results['theme_analysis']['theme_categories']
            if themes:
                theme_names = list(themes.keys())
                theme_counts = list(themes.values())
                
                axes[0,1].bar(theme_names, theme_counts)
                axes[0,1].set_title('Themes Mentioned in Feedback')
                axes[0,1].tick_params(axis='x', rotation=45)
        
        # 3. Priority Issues
        if 'priority_issues' in self.analysis_results:
            issues = self.analysis_results['priority_issues']
            if issues and not isinstance(issues, dict):
                issue_names = [item['issue'] for item in issues[:5]]
                issue_counts = [item['frequency'] for item in issues[:5]]
                
                axes[1,0].bar(issue_names, issue_counts, color='#e74c3c')
                axes[1,0].set_title('Top User Complaints')
                axes[1,0].tick_params(axis='x', rotation=45)
        
        # 4. Sentiment Score Distribution
        if self.feedback_data is not None and 'sentiment_score' in self.feedback_data.columns:
            axes[1,1].hist(self.feedback_data['sentiment_score'], bins=20, alpha=0.7, color='#3498db')
            axes[1,1].set_title('Sentiment Score Distribution')
            axes[1,1].set_xlabel('Sentiment Score (-1 to 1)')
            axes[1,1].axvline(x=0, color='red', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Feedback analysis visualization saved to {output_path}")
        
        return True

def main():
    """Example usage of the Feedback Analyzer"""
    print("💬 Starting Automated Feedback Analysis")
    print("=" * 50)
    
    # Sample user feedback (normally loaded from CSV or database)
    sample_feedback = [
        "The interface is really intuitive and easy to use. Love the new design!",
        "Search function is too slow and often doesn't find what I'm looking for",
        "Great recommendations, very personalized and relevant to my interests",
        "App keeps crashing when I try to browse different categories",
        "Loading times are terrible, makes the whole experience frustrating",
        "Simple and clean layout, navigation is straightforward",
        "Voice search never understands what I'm saying, very confusing",
        "Amazing user experience, everything works perfectly",
        "Too many bugs and errors, needs better quality control",
        "Fast and responsive, great performance overall",
        "Difficult to find new content, browsing is complicated",
        "Love the personalized suggestions, very accurate",
        "Interface design is beautiful and modern",
        "Frequent crashes and technical issues are annoying",
        "Easy to use and understand, very intuitive",
        "Slow loading makes me want to use other apps instead",
        "Great job on the recent updates, much better now",
        "Search results are not relevant to what I'm looking for",
        "Smooth and fast, excellent performance",
        "Confusing navigation, hard to find what I want"
    ]
    
    # Initialize analyzer
    analyzer = FeedbackAnalyzer()
    analyzer.load_feedback(sample_feedback)
    
    # Run analysis pipeline
    print("\n📊 Running sentiment analysis...")
    sentiment_results = analyzer.analyze_sentiment()
    print(f"  Positive: {sentiment_results['percentages'].get('positive', 0)}%")
    print(f"  Negative: {sentiment_results['percentages'].get('negative', 0)}%")  
    print(f"  Neutral: {sentiment_results['percentages'].get('neutral', 0)}%")
    
    print("\n🎯 Extracting themes...")
    theme_results = analyzer.extract_themes()
    print(f"  Found {len(theme_results['theme_categories'])} main theme categories")
    for theme, count in theme_results['theme_categories'].items():
        print(f"  {theme}: {count} mentions")
    
    print("\n❌ Identifying priority issues...")
    priority_issues = analyzer.identify_priority_issues()
    for issue in priority_issues[:3]:
        print(f"  {issue['issue']}: mentioned by {issue['percentage']}% of users")
    
    # Generate comprehensive report
    report = analyzer.generate_insights_report()
    print(f"\n📋 Analysis Summary:")
    print(f"  Total feedback analyzed: {report['total_feedback']}")
    for insight in report['key_insights']:
        print(f"  {insight}")
    
    # Create visualizations
    analyzer.create_visualization('automated_feedback_analysis.png')
    
    print("\n🎉 Automated feedback analysis complete!")
    print("⏱️ Time saved: ~4 hours of manual analysis → 2 minutes automated")
    print("📈 Scale: Can process 1000+ feedback responses in same time")

if __name__ == "__main__":
    main()

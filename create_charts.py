#!/usr/bin/env python3
"""
Script to create interactive charts for the UAGC RFI Conversion Analysis Report
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import re
import os

def load_data():
    """Load and process the data files"""
    # Load the main pre/post data
    pre_post_data = pd.read_csv('data/Pre_vs_Post_Request_Information_Submits.csv')
    
    # Calculate conversion rates
    pre_post_data['conversion_rate_pre'] = (pre_post_data['conversions_pre'] / pre_post_data['sessions_pre'] * 100).round(2)
    pre_post_data['conversion_rate_post'] = (pre_post_data['conversions_post'] / pre_post_data['sessions_post'] * 100).round(2)
    pre_post_data['conversion_rate_change'] = (pre_post_data['conversion_rate_post'] - pre_post_data['conversion_rate_pre']).round(2)
    pre_post_data['conversions_change'] = pre_post_data['conversions_post'] - pre_post_data['conversions_pre']
    pre_post_data['sessions_change'] = pre_post_data['sessions_post'] - pre_post_data['sessions_pre']
    
    return pre_post_data

def create_overall_results_chart(data):
    """Create the main overall results comparison chart"""
    
    # Calculate totals
    total_sessions_pre = data['sessions_pre'].sum()
    total_sessions_post = data['sessions_post'].sum()
    total_conversions_pre = data['conversions_pre'].sum()
    total_conversions_post = data['conversions_post'].sum()
    
    # Calculate overall metrics
    sessions_change_pct = ((total_sessions_post - total_sessions_pre) / total_sessions_pre * 100)
    conversions_change_pct = ((total_conversions_post - total_conversions_pre) / total_conversions_pre * 100)
    
    overall_conv_rate_pre = (total_conversions_pre / total_sessions_pre * 100)
    overall_conv_rate_post = (total_conversions_post / total_sessions_post * 100)
    conv_rate_change_pp = overall_conv_rate_post - overall_conv_rate_pre
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Sessions Comparison', 'Key Events (RFI Submissions)', 
                       'Conversion Rate', 'Session Duration Change'],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Sessions comparison
    fig.add_trace(
        go.Bar(
            x=['Pre-Change', 'Post-Change'],
            y=[total_sessions_pre, total_sessions_post],
            name='Sessions',
            marker_color=['#305496', '#4CAF50'],
            text=[f'{total_sessions_pre:,}', f'{total_sessions_post:,}'],
            textposition='auto'
        ),
        row=1, col=1
    )
    
    # Key events comparison
    fig.add_trace(
        go.Bar(
            x=['Pre-Change', 'Post-Change'],
            y=[total_conversions_pre, total_conversions_post],
            name='Key Events',
            marker_color=['#305496', '#4CAF50'],
            text=[f'{total_conversions_pre}', f'{total_conversions_post}'],
            textposition='auto'
        ),
        row=1, col=2
    )
    
    # Conversion rates
    fig.add_trace(
        go.Bar(
            x=['Pre-Change', 'Post-Change'],
            y=[overall_conv_rate_pre, overall_conv_rate_post],
            name='Conversion Rate',
            marker_color=['#305496', '#4CAF50'],
            text=[f'{overall_conv_rate_pre:.2f}%', f'{overall_conv_rate_post:.2f}%'],
            textposition='auto'
        ),
        row=2, col=1
    )
    
    # Session duration (simulated data based on report)
    fig.add_trace(
        go.Bar(
            x=['Pre-Change', 'Post-Change'],
            y=[1859.5, 1595.9],
            name='Avg Session Duration (seconds)',
            marker_color=['#305496', '#ff9800'],
            text=['1859.5s', '1595.9s'],
            textposition='auto'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="RFI Conversion Analysis: Pre vs Post Implementation Results",
        title_x=0.5,
        font=dict(family="Arial", size=12),
        plot_bgcolor='white'
    )
    
    # Add annotations for key metrics
    fig.add_annotation(
        text=f"Sessions Growth: +{sessions_change_pct:.1f}%",
        xref="paper", yref="paper",
        x=0.25, y=0.95, showarrow=False,
        font=dict(size=14, color="#4CAF50")
    )
    
    fig.add_annotation(
        text=f"Key Events Growth: +{conversions_change_pct:.1f}%",
        xref="paper", yref="paper",
        x=0.75, y=0.95, showarrow=False,
        font=dict(size=14, color="#4CAF50")
    )
    
    return fig

def create_top_wins_chart(data):
    """Create chart showing top conversion rate improvements"""
    
    # Get top 10 improvements
    top_wins = data.nlargest(10, 'conversion_rate_change')[['page', 'conversion_rate_change']].copy()
    
    # Clean up page names for display
    top_wins['page_clean'] = top_wins['page'].str.replace('/online-degrees/', '').str.replace('/', ' › ')
    
    fig = go.Figure(data=[
        go.Bar(
            y=top_wins['page_clean'],
            x=top_wins['conversion_rate_change'],
            orientation='h',
            marker_color=['#4CAF50' if x > 0 else '#ff6b6b' for x in top_wins['conversion_rate_change']],
            text=[f'+{x:.2f}pp' if x > 0 else f'{x:.2f}pp' for x in top_wins['conversion_rate_change']],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Top 10 Pages by Conversion Rate Improvement",
        title_x=0.5,
        xaxis_title="Conversion Rate Change (percentage points)",
        yaxis_title="Page",
        height=500,
        font=dict(family="Arial", size=11),
        plot_bgcolor='white'
    )
    
    fig.update_yaxes(autorange="reversed")
    
    return fig

def create_wins_losses_summary(data):
    """Create a summary chart of wins vs losses"""
    
    wins = len(data[data['conversion_rate_change'] > 0])
    losses = len(data[data['conversion_rate_change'] < 0])
    ties = len(data[data['conversion_rate_change'] == 0])
    
    fig = go.Figure(data=[
        go.Pie(
            labels=['Wins', 'Losses', 'Ties'],
            values=[wins, losses, ties],
            marker_colors=['#4CAF50', '#ff6b6b', '#6c757d'],
            hole=0.4
        )
    ])
    
    fig.update_layout(
        title="Performance Summary: Wins vs Losses",
        title_x=0.5,
        height=400,
        font=dict(family="Arial", size=12),
        annotations=[dict(text=f'{wins + losses + ties}<br>Total Pages', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    return fig

def update_html_with_charts():
    """Update the HTML file to replace base64 images with interactive charts"""
    
    # Load data
    data = load_data()
    
    # Create charts
    overall_chart = create_overall_results_chart(data)
    top_wins_chart = create_top_wins_chart(data)
    summary_chart = create_wins_losses_summary(data)
    
    # Convert to HTML
    overall_html = overall_chart.to_html(include_plotlyjs='cdn', div_id="overall-results-chart")
    top_wins_html = top_wins_chart.to_html(include_plotlyjs=False, div_id="top-wins-chart")
    summary_html = summary_chart.to_html(include_plotlyjs=False, div_id="summary-chart")
    
    # Read the current HTML file
    with open('UAGC RFI Conversion Analysis Report.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace the base64 images with interactive charts
    # Find and replace the first large base64 image (overall results)
    base64_pattern = r'<img src="data:image/png;base64,[^"]+"\s*/?>'
    
    # Extract chart content safely
    overall_chart_content = overall_html.split("<body>")[1].split("</body>")[0]
    
    # Replace first occurrence (overall results chart)
    html_content = re.sub(
        base64_pattern,
        lambda m: f'<div class="chart-container">{overall_chart_content}</div>',
        html_content,
        count=1
    )
    
    # Replace second occurrence (top wins chart)
    html_content = re.sub(
        base64_pattern,
        lambda m: f'<div class="chart-container">{top_wins_html}</div>',
        html_content,
        count=1
    )
    
    # Add the summary chart after the table
    table_end = '</table>'
    if table_end in html_content:
        insertion_point = html_content.find(table_end) + len(table_end)
        chart_section = f'''
        
<h3>Performance Distribution</h3>
<p>The following chart shows the overall distribution of page performance after the RFI improvements were implemented:</p>
<div class="chart-container">
{summary_html}
</div>
'''
        html_content = html_content[:insertion_point] + chart_section + html_content[insertion_point:]
    
    # Add some CSS for better chart styling
    css_insert = '''
<style>
.chart-container {
    margin: 2rem 0;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    background: white;
}

.plotly-graph-div {
    width: 100% !important;
}
</style>
</head>'''
    
    html_content = html_content.replace('</head>', css_insert)
    
    # Write the updated HTML
    with open('UAGC RFI Conversion Analysis Report_updated.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("HTML report updated successfully!")
    print("New file created: UAGC RFI Conversion Analysis Report_updated.html")

if __name__ == "__main__":
    update_html_with_charts()

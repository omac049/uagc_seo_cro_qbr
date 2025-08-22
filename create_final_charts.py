#!/usr/bin/env python3
"""
Final script to create interactive charts for the UAGC RFI Conversion Analysis Report
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

def load_and_process_data():
    """Load and process the data"""
    print("Loading data...")
    
    # Load the main pre/post data
    data = pd.read_csv('data/Pre_vs_Post_Request_Information_Submits.csv')
    
    # Calculate conversion rates and changes
    data['conversion_rate_pre'] = (data['conversions_pre'] / data['sessions_pre'] * 100).round(4)
    data['conversion_rate_post'] = (data['conversions_post'] / data['sessions_post'] * 100).round(4)
    data['conversion_rate_change'] = (data['conversion_rate_post'] - data['conversion_rate_pre']).round(4)
    data['conversions_change'] = data['conversions_post'] - data['conversions_pre']
    data['sessions_change'] = data['sessions_post'] - data['sessions_pre']
    
    print(f"Loaded {len(data)} pages of data")
    return data

def create_executive_summary_chart(data):
    """Create the main executive summary chart with key metrics"""
    
    # Calculate totals
    total_sessions_pre = data['sessions_pre'].sum()
    total_sessions_post = data['sessions_post'].sum()
    total_conversions_pre = data['conversions_pre'].sum()
    total_conversions_post = data['conversions_post'].sum()
    
    # Calculate metrics
    sessions_change_pct = ((total_sessions_post - total_sessions_pre) / total_sessions_pre * 100)
    conversions_change_pct = ((total_conversions_post - total_conversions_pre) / total_conversions_pre * 100)
    overall_conv_rate_pre = (total_conversions_pre / total_sessions_pre * 100)
    overall_conv_rate_post = (total_conversions_post / total_sessions_post * 100)
    conv_rate_change_pp = overall_conv_rate_post - overall_conv_rate_pre
    
    # Create a 2x2 subplot with bar charts only
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Sessions Growth', 
            'RFI Submissions Growth', 
            'Overall Conversion Rate Improvement',
            'Page Performance Summary'
        ]
    )
    
    # 1. Sessions comparison
    fig.add_trace(
        go.Bar(
            x=['Pre-Implementation', 'Post-Implementation'],
            y=[total_sessions_pre, total_sessions_post],
            name='Sessions',
            marker_color=['#305496', '#4CAF50'],
            text=[f'{total_sessions_pre:,}', f'{total_sessions_post:,}'],
            textposition='auto',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # 2. Conversions comparison
    fig.add_trace(
        go.Bar(
            x=['Pre-Implementation', 'Post-Implementation'],
            y=[total_conversions_pre, total_conversions_post],
            name='RFI Submissions',
            marker_color=['#305496', '#4CAF50'],
            text=[f'{total_conversions_pre}', f'{total_conversions_post}'],
            textposition='auto',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # 3. Conversion rates
    fig.add_trace(
        go.Bar(
            x=['Pre-Implementation', 'Post-Implementation'],
            y=[overall_conv_rate_pre, overall_conv_rate_post],
            name='Conversion Rate',
            marker_color=['#305496', '#4CAF50'],
            text=[f'{overall_conv_rate_pre:.3f}%', f'{overall_conv_rate_post:.3f}%'],
            textposition='auto',
            showlegend=False
        ),
        row=2, col=1
    )
    
    # 4. Performance summary
    wins = len(data[data['conversion_rate_change'] > 0])
    losses = len(data[data['conversion_rate_change'] < 0])
    neutral = len(data[data['conversion_rate_change'] == 0])
    
    fig.add_trace(
        go.Bar(
            x=['Pages Improved', 'Pages Declined', 'No Change'],
            y=[wins, losses, neutral],
            name='Page Performance',
            marker_color=['#4CAF50', '#f44336', '#ff9800'],
            text=[wins, losses, neutral],
            textposition='auto',
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        title_text="<b>UAGC RFI Conversion Analysis: Key Performance Metrics</b>",
        title_x=0.5,
        title_font_size=18,
        font=dict(family="Arial", size=12),
        plot_bgcolor='white'
    )
    
    # Add key metrics as annotations
    fig.add_annotation(
        text=f"<b>Sessions Growth: +{sessions_change_pct:.1f}%</b>",
        xref="paper", yref="paper",
        x=0.25, y=0.95, showarrow=False,
        font=dict(size=14, color="#4CAF50"),
        bgcolor="rgba(76, 175, 80, 0.1)",
        bordercolor="#4CAF50"
    )
    
    fig.add_annotation(
        text=f"<b>RFI Growth: +{conversions_change_pct:.1f}%</b>",
        xref="paper", yref="paper",
        x=0.75, y=0.95, showarrow=False,
        font=dict(size=14, color="#4CAF50"),
        bgcolor="rgba(76, 175, 80, 0.1)",
        bordercolor="#4CAF50"
    )
    
    fig.add_annotation(
        text=f"<b>Conversion Rate: +{conv_rate_change_pp:.3f}pp</b>",
        xref="paper", yref="paper",
        x=0.25, y=0.45, showarrow=False,
        font=dict(size=14, color="#4CAF50"),
        bgcolor="rgba(76, 175, 80, 0.1)",
        bordercolor="#4CAF50"
    )
    
    fig.add_annotation(
        text=f"<b>Success Rate: {wins/len(data)*100:.1f}%</b>",
        xref="paper", yref="paper",
        x=0.75, y=0.45, showarrow=False,
        font=dict(size=14, color="#305496"),
        bgcolor="rgba(48, 84, 150, 0.1)",
        bordercolor="#305496"
    )
    
    return fig

def create_top_performers_chart(data):
    """Create chart showing top and bottom performing pages"""
    
    # Get top 12 and bottom 3
    top_performers = data.nlargest(12, 'conversion_rate_change')
    bottom_performers = data.nsmallest(3, 'conversion_rate_change')
    
    # Combine
    combined = pd.concat([top_performers, bottom_performers]).reset_index(drop=True)
    
    # Clean up page names for display
    combined['page_clean'] = combined['page'].str.replace('/online-degrees/', '').str.replace('/', ' › ')
    combined['page_short'] = combined['page_clean'].apply(lambda x: x[:50] + '...' if len(x) > 50 else x)
    
    # Create colors based on positive/negative changes
    colors = ['#4CAF50' if x >= 0 else '#f44336' for x in combined['conversion_rate_change']]
    
    fig = go.Figure(data=[
        go.Bar(
            y=combined['page_short'],
            x=combined['conversion_rate_change'],
            orientation='h',
            marker_color=colors,
            text=[f'+{x:.3f}pp' if x >= 0 else f'{x:.3f}pp' for x in combined['conversion_rate_change']],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Change: %{x:.3f} percentage points<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="<b>Top and Bottom Performing Pages by Conversion Rate Change</b>",
        title_x=0.5,
        xaxis_title="Conversion Rate Change (percentage points)",
        yaxis_title="Landing Page",
        height=600,
        font=dict(family="Arial", size=11),
        plot_bgcolor='white',
        yaxis=dict(autorange="reversed")
    )
    
    # Add vertical line at zero
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    return fig

def create_performance_distribution_chart(data):
    """Create a pie chart showing performance distribution"""
    
    wins = len(data[data['conversion_rate_change'] > 0])
    losses = len(data[data['conversion_rate_change'] < 0])
    neutral = len(data[data['conversion_rate_change'] == 0])
    
    fig = go.Figure(data=[
        go.Pie(
            labels=['Pages Improved', 'Pages Declined', 'No Change'],
            values=[wins, losses, neutral],
            marker_colors=['#4CAF50', '#f44336', '#ff9800'],
            hole=0.4,
            textinfo='label+percent+value',
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="<b>Distribution of Page Performance</b>",
        title_x=0.5,
        height=500,
        font=dict(family="Arial", size=12),
        annotations=[
            dict(
                text=f'<b>{wins + losses + neutral}</b><br>Total Pages',
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )
        ]
    )
    
    return fig

def find_and_replace_images(html_content):
    """Find base64 images and replace them with placeholders"""
    
    # Find all base64 image tags - more flexible pattern to handle attributes
    base64_pattern = r'<img[^>]*src="data:image/png;base64,[^"]+[^>]*/?>'
    matches = re.findall(base64_pattern, html_content)
    
    print(f"Found {len(matches)} base64 images")
    
    # Replace each image with a unique placeholder
    for i, match in enumerate(matches):
        placeholder = f"__CHART_PLACEHOLDER_{i}__"
        html_content = html_content.replace(match, placeholder, 1)
    
    return html_content, len(matches)

def update_html_with_charts():
    """Update the HTML file with interactive charts"""
    
    print("Processing data and creating charts...")
    data = load_and_process_data()
    
    # Create charts
    print("Creating executive summary chart...")
    executive_chart = create_executive_summary_chart(data)
    
    print("Creating top performers chart...")
    performers_chart = create_top_performers_chart(data)
    
    print("Creating performance distribution chart...")
    distribution_chart = create_performance_distribution_chart(data)
    
    print("Converting charts to HTML...")
    # Convert to HTML and extract just the div content
    executive_html = executive_chart.to_html(include_plotlyjs='cdn', div_id="executive-chart")
    performers_html = performers_chart.to_html(include_plotlyjs=False, div_id="performers-chart")
    distribution_html = distribution_chart.to_html(include_plotlyjs=False, div_id="distribution-chart")
    
    # Extract only the body content from the charts
    def extract_chart_div(html_string):
        if '<body>' in html_string and '</body>' in html_string:
            body_content = html_string.split('<body>')[1].split('</body>')[0]
            return body_content.strip()
        return html_string
    
    executive_div = extract_chart_div(executive_html)
    
    print("Reading original HTML file...")
    # Read the current HTML file
    with open('UAGC RFI Conversion Analysis Report.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("Finding and replacing images...")
    
    # Use safer replacement method
    html_content, num_images = find_and_replace_images(html_content)
    
    if num_images >= 3:
        # Replace placeholders with charts
        chart_containers = [
            f'<div class="chart-container executive-summary">{executive_div}</div>',
            f'<div class="chart-container top-performers">{performers_html}</div>',
            f'<div class="chart-container performance-distribution">{distribution_html}</div>'
        ]
        
        for i, chart_html in enumerate(chart_containers):
            placeholder = f"__CHART_PLACEHOLDER_{i}__"
            if placeholder in html_content:
                html_content = html_content.replace(placeholder, chart_html)
                print(f"Replaced chart {i+1}")
            else:
                print(f"Warning: Placeholder {i} not found")
    else:
        print(f"Warning: Expected 3 images, found {num_images}")
    
    # Add enhanced CSS
    enhanced_css = '''
<style>
.chart-container {
    margin: 2rem 0;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    background: white;
    border: 1px solid #e0e0e0;
}

.chart-container.executive-summary {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border: 2px solid #305496;
}

.chart-container.top-performers {
    background: linear-gradient(135deg, #e8f5e8 0%, #a8e6cf 100%);
}

.chart-container.performance-distribution {
    background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
}

.plotly-graph-div {
    width: 100% !important;
    border-radius: 8px;
}

.modebar {
    opacity: 0.7;
}

.modebar:hover {
    opacity: 1;
}

@media (max-width: 768px) {
    .chart-container {
        margin: 1rem 0;
        padding: 1rem;
    }
}

@media print {
    .chart-container {
        break-inside: avoid;
        box-shadow: none;
        border: 1px solid #ccc;
    }
}
</style>
</head>'''
    
    html_content = html_content.replace('</head>', enhanced_css)
    
    # Add summary statistics
    wins = len(data[data['conversion_rate_change'] > 0])
    avg_improvement = data[data['conversion_rate_change'] > 0]['conversion_rate_change'].mean()
    best_improvement = data['conversion_rate_change'].max()
    success_rate = wins / len(data) * 100
    
    summary_stats = f'''
<div class="summary-statistics" style="margin-top: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #305496;">
    <h3 style="color: #305496; margin-top: 0;">📊 Key Performance Indicators</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
        <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div style="font-size: 2rem; font-weight: bold; color: #4CAF50;">{wins}</div>
            <div style="color: #666;">Pages Improved</div>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div style="font-size: 2rem; font-weight: bold; color: #305496;">{best_improvement:.3f}pp</div>
            <div style="color: #666;">Best Improvement</div>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div style="font-size: 2rem; font-weight: bold; color: #ff9800;">{avg_improvement:.3f}pp</div>
            <div style="color: #666;">Avg Improvement</div>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div style="font-size: 2rem; font-weight: bold; color: #17a2b8;">{success_rate:.1f}%</div>
            <div style="color: #666;">Success Rate</div>
        </div>
    </div>
</div>
'''
    
    # Insert before closing body tag
    html_content = html_content.replace('</body>', summary_stats + '</body>')
    
    print("Saving enhanced HTML file...")
    # Write the updated HTML
    with open('UAGC RFI Conversion Analysis Report_enhanced.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Report enhancement complete!")
    print(f"📊 Replaced {num_images} base64 images with interactive charts")
    print(f"📈 Created 3 new interactive visualizations")
    print(f"📄 Enhanced file saved as: UAGC RFI Conversion Analysis Report_enhanced.html")

if __name__ == "__main__":
    try:
        update_html_with_charts()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

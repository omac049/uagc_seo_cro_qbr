#!/usr/bin/env python3
"""
Enhanced script to create comprehensive interactive charts for the UAGC RFI Conversion Analysis Report
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import re
import numpy as np

def load_and_process_data():
    """Load and process all data files"""
    print("Loading data...")
    
    # Load the main pre/post data
    pre_post_data = pd.read_csv('data/Pre_vs_Post_Request_Information_Submits.csv')
    
    # Calculate conversion rates and changes
    pre_post_data['conversion_rate_pre'] = (pre_post_data['conversions_pre'] / pre_post_data['sessions_pre'] * 100).round(4)
    pre_post_data['conversion_rate_post'] = (pre_post_data['conversions_post'] / pre_post_data['sessions_post'] * 100).round(4)
    pre_post_data['conversion_rate_change'] = (pre_post_data['conversion_rate_post'] - pre_post_data['conversion_rate_pre']).round(4)
    pre_post_data['conversions_change'] = pre_post_data['conversions_post'] - pre_post_data['conversions_pre']
    pre_post_data['sessions_change'] = pre_post_data['sessions_post'] - pre_post_data['sessions_pre']
    pre_post_data['percent_change_conversions'] = ((pre_post_data['conversions_post'] / pre_post_data['conversions_pre'] - 1) * 100).round(2)
    
    print(f"Loaded {len(pre_post_data)} pages of data")
    return pre_post_data

def create_executive_summary_chart(data):
    """Create the main executive summary chart"""
    
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
    
    # Create the main dashboard
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[
            'Sessions Impact', 
            'RFI Submissions Growth', 
            'Conversion Rate Improvement',
            'Distribution of Page Performance',
            'Top Performers',
            'Key Metrics Summary'
        ],
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
               [{"type": "domain"}, {"secondary_y": False}, {"type": "table"}]]
    )
    
    # 1. Sessions comparison
    fig.add_trace(
        go.Bar(
            x=['Pre-Implementation', 'Post-Implementation'],
            y=[total_sessions_pre, total_sessions_post],
            name='Sessions',
            marker_color=['#1f77b4', '#2ca02c'],
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
            marker_color=['#1f77b4', '#2ca02c'],
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
            marker_color=['#1f77b4', '#2ca02c'],
            text=[f'{overall_conv_rate_pre:.3f}%', f'{overall_conv_rate_post:.3f}%'],
            textposition='auto',
            showlegend=False
        ),
        row=1, col=3
    )
    
    # 4. Performance distribution pie chart
    wins = len(data[data['conversion_rate_change'] > 0])
    losses = len(data[data['conversion_rate_change'] < 0])
    neutral = len(data[data['conversion_rate_change'] == 0])
    
    fig.add_trace(
        go.Pie(
            labels=['Improved', 'Declined', 'No Change'],
            values=[wins, losses, neutral],
            marker_colors=['#2ca02c', '#d62728', '#ff7f0e'],
            hole=0.4,
            showlegend=False
        ),
        row=2, col=2
    )
    
    # 5. Top 5 performers
    top_5 = data.nlargest(5, 'conversion_rate_change')
    fig.add_trace(
        go.Bar(
            y=[page.split('/')[-1][:20] + '...' if len(page.split('/')[-1]) > 20 else page.split('/')[-1] 
               for page in top_5['page']],
            x=top_5['conversion_rate_change'],
            name='Top Performers',
            marker_color='#2ca02c',
            orientation='h',
            text=[f'+{x:.2f}pp' for x in top_5['conversion_rate_change']],
            textposition='auto',
            showlegend=False
        ),
        row=2, col=2
    )
    
    # 6. Key metrics table
    fig.add_trace(
        go.Table(
            header=dict(values=['Metric', 'Value', 'Change'],
                       fill_color='#f0f0f0',
                       align='left'),
            cells=dict(values=[
                ['Total Sessions', 'Total RFI Submissions', 'Overall Conversion Rate', 'Pages Improved', 'Average Improvement'],
                [f'{total_sessions_post:,}', f'{total_conversions_post}', f'{overall_conv_rate_post:.3f}%', f'{wins}', f'{data[data["conversion_rate_change"] > 0]["conversion_rate_change"].mean():.3f}pp'],
                [f'+{sessions_change_pct:.1f}%', f'+{conversions_change_pct:.1f}%', f'+{conv_rate_change_pp:.3f}pp', f'{wins}/{len(data)}', f'({wins/len(data)*100:.1f}% of pages)']
            ],
            fill_color=[['white']*5, ['lightgreen']*5, ['lightblue']*5],
            align='left')
        ),
        row=2, col=3
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="<b>UAGC RFI Conversion Analysis: Implementation Impact Dashboard</b>",
        title_x=0.5,
        title_font_size=20,
        font=dict(family="Arial", size=11),
        plot_bgcolor='white',
        showlegend=False
    )
    
    # Add annotations for key insights
    fig.add_annotation(
        text=f"<b>+{sessions_change_pct:.1f}%</b> Sessions Growth",
        xref="paper", yref="paper",
        x=0.15, y=0.98, showarrow=False,
        font=dict(size=12, color="#2ca02c"),
        bgcolor="rgba(44, 160, 44, 0.1)",
        bordercolor="#2ca02c"
    )
    
    fig.add_annotation(
        text=f"<b>+{conversions_change_pct:.1f}%</b> RFI Growth",
        xref="paper", yref="paper",
        x=0.5, y=0.98, showarrow=False,
        font=dict(size=12, color="#2ca02c"),
        bgcolor="rgba(44, 160, 44, 0.1)",
        bordercolor="#2ca02c"
    )
    
    return fig

def create_top_performers_chart(data):
    """Create detailed chart of top performing pages"""
    
    # Get top 15 improvements and worst 5 declines
    top_wins = data.nlargest(15, 'conversion_rate_change')
    top_losses = data.nsmallest(5, 'conversion_rate_change')
    
    # Combine for a comprehensive view
    combined = pd.concat([top_wins, top_losses]).reset_index(drop=True)
    
    # Clean up page names
    combined['page_clean'] = combined['page'].str.replace('/online-degrees/', '').str.replace('/', ' › ')
    combined['page_short'] = combined['page_clean'].apply(lambda x: x[:40] + '...' if len(x) > 40 else x)
    
    # Create the chart
    fig = go.Figure()
    
    # Add bars with different colors for positive/negative changes
    colors = ['#2ca02c' if x > 0 else '#d62728' for x in combined['conversion_rate_change']]
    
    fig.add_trace(go.Bar(
        y=combined['page_short'],
        x=combined['conversion_rate_change'],
        orientation='h',
        marker_color=colors,
        text=[f'+{x:.3f}pp' if x > 0 else f'{x:.3f}pp' for x in combined['conversion_rate_change']],
        textposition='auto',
        hovertemplate=
        '<b>%{y}</b><br>' +
        'Conversion Rate Change: %{x:.3f} percentage points<br>' +
        '<extra></extra>'
    ))
    
    fig.update_layout(
        title="<b>Top Performing and Declining Pages by Conversion Rate Change</b>",
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
    """Create comprehensive performance distribution analysis"""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Conversion Rate Change Distribution',
            'Pages by Performance Categories', 
            'Sessions vs Conversion Rate Change',
            'Top Categories by Average Improvement'
        ],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Histogram of conversion rate changes
    fig.add_trace(
        go.Histogram(
            x=data['conversion_rate_change'],
            nbinsx=30,
            name='Distribution',
            marker_color='lightblue',
            opacity=0.7,
            showlegend=False
        ),
        row=1, col=1
    )
    
    # 2. Performance categories
    big_wins = len(data[data['conversion_rate_change'] > 0.5])
    small_wins = len(data[(data['conversion_rate_change'] > 0) & (data['conversion_rate_change'] <= 0.5)])
    no_change = len(data[data['conversion_rate_change'] == 0])
    small_losses = len(data[(data['conversion_rate_change'] < 0) & (data['conversion_rate_change'] >= -0.5)])
    big_losses = len(data[data['conversion_rate_change'] < -0.5])
    
    categories = ['Big Wins\n(>0.5pp)', 'Small Wins\n(0-0.5pp)', 'No Change', 'Small Declines\n(0 to -0.5pp)', 'Big Declines\n(<-0.5pp)']
    values = [big_wins, small_wins, no_change, small_losses, big_losses]
    colors = ['#2ca02c', '#90EE90', '#ffdd44', '#FFA07A', '#d62728']
    
    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=values,
            textposition='auto',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # 3. Scatter plot: Sessions vs Conversion Rate Change
    fig.add_trace(
        go.Scatter(
            x=data['sessions_post'],
            y=data['conversion_rate_change'],
            mode='markers',
            marker=dict(
                size=8,
                color=data['conversion_rate_change'],
                colorscale='RdYlGn',
                showscale=False,
                opacity=0.6
            ),
            text=data['page'].str.split('/').str[-1],
            hovertemplate='<b>%{text}</b><br>Sessions: %{x}<br>Rate Change: %{y:.3f}pp<extra></extra>',
            showlegend=False
        ),
        row=2, col=1
    )
    
    # 4. Category analysis (extract categories from URLs)
    data['category'] = data['page'].str.extract(r'/online-degrees/([^/]+)/')
    category_stats = data.groupby('category')['conversion_rate_change'].agg(['mean', 'count']).reset_index()
    category_stats = category_stats[category_stats['count'] >= 3].nlargest(8, 'mean')
    
    if not category_stats.empty:
        fig.add_trace(
            go.Bar(
                x=category_stats['category'],
                y=category_stats['mean'],
                marker_color='teal',
                text=[f'{x:.3f}pp' for x in category_stats['mean']],
                textposition='auto',
                showlegend=False
            ),
            row=2, col=2
        )
    
    fig.update_layout(
        height=700,
        title_text="<b>Performance Analysis: Distribution and Patterns</b>",
        title_x=0.5,
        font=dict(family="Arial", size=11),
        plot_bgcolor='white'
    )
    
    return fig

def update_html_with_enhanced_charts():
    """Update the HTML file with all new interactive charts"""
    
    print("Processing data and creating charts...")
    data = load_and_process_data()
    
    # Create all charts
    executive_chart = create_executive_summary_chart(data)
    performers_chart = create_top_performers_chart(data)
    distribution_chart = create_performance_distribution_chart(data)
    
    print("Converting charts to HTML...")
    
    # Convert to HTML with different plotly inclusion strategies
    executive_html = executive_chart.to_html(include_plotlyjs='cdn', div_id="executive-dashboard")
    performers_html = performers_chart.to_html(include_plotlyjs=False, div_id="top-performers")
    distribution_html = distribution_chart.to_html(include_plotlyjs=False, div_id="performance-distribution")
    
    print("Reading HTML file...")
    # Read the current HTML file
    with open('UAGC RFI Conversion Analysis Report.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("Replacing images with interactive charts...")
    
    # Replace base64 images with interactive charts
    base64_pattern = r'<img src="data:image/png;base64,[^"]+"\s*/?>'
    
    # Count current images
    current_images = len(re.findall(base64_pattern, html_content))
    print(f"Found {current_images} base64 images to replace")
    
    # Replace first occurrence (executive summary chart)
    html_content = re.sub(
        base64_pattern,
        lambda m: f'<div class="chart-container executive-dashboard">{executive_html.split("<body>")[1].split("</body>")[0] if "<body>" in executive_html else executive_html}</div>',
        html_content,
        count=1
    )
    
    # Replace second occurrence (top performers chart)
    html_content = re.sub(
        base64_pattern,
        lambda m: f'<div class="chart-container top-performers">{performers_html}</div>',
        html_content,
        count=1
    )
    
    # Replace third occurrence (performance distribution)
    html_content = re.sub(
        base64_pattern,
        lambda m: f'<div class="chart-container performance-distribution">{distribution_html}</div>',
        html_content,
        count=1
    )
    
    # Add enhanced CSS for better styling
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

.chart-container.executive-dashboard {
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

/* Enhanced table styling */
.modebar {
    opacity: 0.7;
}

.modebar:hover {
    opacity: 1;
}

/* Responsive design */
@media (max-width: 768px) {
    .chart-container {
        margin: 1rem 0;
        padding: 1rem;
    }
}

/* Print styles */
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
    
    # Add summary statistics section after the main content
    summary_stats = f'''
<div class="summary-statistics" style="margin-top: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #305496;">
    <h3 style="color: #305496; margin-top: 0;">📊 Key Performance Indicators</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
        <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div style="font-size: 2rem; font-weight: bold; color: #2ca02c;">{len(data[data["conversion_rate_change"] > 0])}</div>
            <div style="color: #666;">Pages Improved</div>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div style="font-size: 2rem; font-weight: bold; color: #305496;">{data["conversion_rate_change"].max():.3f}pp</div>
            <div style="color: #666;">Best Improvement</div>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div style="font-size: 2rem; font-weight: bold; color: #ff7f0e;">{data[data["conversion_rate_change"] > 0]["conversion_rate_change"].mean():.3f}pp</div>
            <div style="color: #666;">Avg Improvement</div>
        </div>
        <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <div style="font-size: 2rem; font-weight: bold; color: #17a2b8;">{len(data[data["conversion_rate_change"] > 0])/len(data)*100:.1f}%</div>
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
    
    # Verify the replacement worked
    remaining_images = len(re.findall(base64_pattern, html_content))
    print(f"\n✅ Report enhancement complete!")
    print(f"📊 Replaced {current_images - remaining_images} base64 images with interactive charts")
    print(f"📈 Created {3} new interactive visualizations")
    print(f"📄 Enhanced file saved as: UAGC RFI Conversion Analysis Report_enhanced.html")
    print(f"📉 Remaining base64 images: {remaining_images}")
    
    if remaining_images > 0:
        print("⚠️  Some images were not replaced. You may need to check the HTML structure.")

if __name__ == "__main__":
    try:
        update_html_with_enhanced_charts()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

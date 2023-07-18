# bubbleplot.py
# @Brendan Baker

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import math

# Read in data
agg_sub = pd.read_csv('./data/bubbleplot_data.csv')


color_map = {
    'block chain': '#434A54',
    'natural language processing': '#8D8361',
    'big data and cloud computing': "#F3DE8A",
    'machine learning': "#EFB988",
    'reinforcement learning': '#EB9486',
    'neural networks': '#B58A90',
    'deep learning': '#9A8595',
    'data scientist': '#7E7F9A',
    'time series analysis': '#BCBCC9',
    'time series': '#BCBCC9',
    'data analyst': '#F9F8F8',
}

# Reference for bubble size
size_ref = 2*max(agg_sub['num_benefits'])/(65**2)

# Create the viz lists
# 1 value true for all 11 categories
viz_lists = [[True if i == j else False for i in range(11)]for j in range(10)] 

# Initialize the figure
fig = go.Figure()

# Loop through each search term
for i, topic in enumerate(agg_sub['category'].unique()):
    # Filter the dataframe by household
    topic_df = agg_sub[agg_sub['category'] == topic]
    
    # Create the customdata for the hover text
    customdata = topic_df[['title', 'company_name', 'location','category', 'num_qualifications', 'num_responsibilities', 'num_benefits']]
    
    fig.add_trace(
        go.Scatter(
            x=topic_df['num_qualifications'],
            y=topic_df['num_responsibilities'],
            customdata=customdata,
            hovertemplate = '<b>%{customdata[0]}</b><br>Company: %{customdata[1]}<br>Location: %{customdata[2]}<br>Search term: %{customdata[3]}<extra></extra><br><br>Number of benefits: %{customdata[6]}',
            name=topic,
            mode = 'markers',
            marker_size = topic_df['num_benefits'],
            marker = dict(color = color_map[topic], sizemode = 'area', sizeref=size_ref, 
                           line_width=2, line_color='darkgrey'),
        )
    )

# Full custom hovertemplate:
#'<b>%{customdata[0]}</b><br>Company: %{customdata[1]}<br>Location: %{customdata[2]}<br>Search term: %{customdata[3]}<extra></extra><br>Number of qualifications: %{customdata[4]}<br>Number of responsibilities: %{customdata[5]}<br>Number of benefits: %{customdata[6]}


fig.update_layout(
    title='Number of Listed Qualifications Versus Number of Listed Responsibilities:<br><br><sup>The size of bubble represents the number of listed benefits - Mouse over a bubble for more info!</sup>',
    xaxis=dict(
        title='Number of Listed Qualifications',
        gridcolor='white',
        gridwidth=2,
    ),
    yaxis=dict(
        title='Number of Listed Responsibilities',
        gridcolor='white',
        gridwidth=2,
    ),
    paper_bgcolor='#272838',
    plot_bgcolor='#272838',
    legend_title_text = 'Job Search Term',
    font=dict(size=16),
    height = 550
)


# Add a dropdown menu to filter by appliance
fig.update_layout(
    updatemenus=[
        go.layout.Updatemenu(
            type='dropdown',
            showactive=True,
            buttons=[
                {'label': 'All Search Terms', 'method': 'update', 'args': [{'visible': True},                                             ]},
                {'label': 'Blockchain', 'method': 'update', 'args': [{'visible': viz_lists[0]}, ]},
                {'label': 'NLP', 'method': 'update', 'args': [{'visible': viz_lists[1]}, ]},
                {'label': 'Big Data', 'method': 'update', 'args': [{'visible': viz_lists[2]}, ]},
                {'label': 'Data Analyst', 'method': 'update', 'args': [{'visible': viz_lists[3]}, ]},
                {'label': 'Machine Learning', 'method': 'update', 'args': [{'visible': viz_lists[4]}, ]},
                {'label': 'Reinforcement Learning', 'method': 'update', 'args': [{'visible': viz_lists[5]}, ]},
                {'label': 'Neural Networks', 'method': 'update', 'args': [{'visible': viz_lists[6]}, ]},
                {'label': 'Deep Learning', 'method': 'update', 'args': [{'visible': viz_lists[7]}, ]},
                {'label': 'Data Scientist', 'method': 'update', 'args': [{'visible': viz_lists[8]}, ]},
                {'label': 'Time Series', 'method': 'update', 'args': [{'visible': viz_lists[9]}, ]}
            ],
        x = 0.95,
        xanchor = 'left',
        y = 1.21,
        yanchor = 'top',
        )
    ]
)

fig.update_layout(legend= {'itemsizing': 'constant'})
fig.update_layout(font=dict(color='white'))
fig.show()


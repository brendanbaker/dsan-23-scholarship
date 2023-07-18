# corrplot.py
# @Brendan Baker

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# Load the data
agg_sub = pd.read_csv('./data/bubbleplot_data.csv')

job_types = agg_sub['category'].unique()

# Initialize the figure
fig = go.Figure()

# Calculate the overall correlation matrix for all job types
overall_corr_matrix = agg_sub[['num_qualifications', 'num_responsibilities', 'num_benefits']].corr().round(2)

# Add the overall correlation matrix as the first trace
fig.add_trace(go.Heatmap(
    z=overall_corr_matrix.values,
    x=['Qualifications', 'Responsibilities', 'Benefits'],
    y=['Qualifications', 'Responsibilities', 'Benefits'],
    text=overall_corr_matrix.values,
    texttemplate='%{text}',
    textfont=dict(color='black'),
    colorscale='Plasma',
    zmin=-1,
    zmax=1,
    hovertemplate='%{x} and %{y}<br>Correlation: %{z}<extra></extra>',
    visible=True,
    name='All Job Types'
))


# Create a heatmap for each job type
for job_type in job_types:
    filtered_data = agg_sub[agg_sub['category'] == job_type]
    corr_matrix = filtered_data[['num_qualifications', 'num_responsibilities', 'num_benefits']].corr().round(2)
    fig.add_trace(go.Heatmap(
        z=corr_matrix.values,
        x=['Qualifications', 'Responsibilities', 'Benefits'],
        y=['Qualifications', 'Responsibilities', 'Benefits'],
        text=corr_matrix.values,
        texttemplate='%{text}',
        textfont=dict(color='black'),
        colorscale='Plasma',
        zmin=-1,
        zmax=1,
        hovertemplate='%{x} and %{y}<br>Correlation: %{z}<extra></extra>',
        visible=False,
        name=job_type
    ))

fig.update_layout(
    title='Correlation Matrix of Responsibilities, Qualifications, and Benefits',
    xaxis=dict(
        title='',
        gridcolor='white',
        gridwidth=2,
    ),
    yaxis=dict(
        title='',
        gridcolor='#272838',
        gridwidth=2,
    ),
    paper_bgcolor='#272838',
    plot_bgcolor='#272838',
    font=dict(size=16),
    height=550
)

# Generate the dropdown buttons
# Generate the dropdown buttons
dropdown_buttons = [
    {
        'label': 'All Job Types',
        'method': 'update',
        'args': [
            {'visible': [True if i == 0 else False for i in range(len(job_types) + 1)]},  # Show only the first trace (overall correlation matrix)
            {'title': 'Correlation Matrix of Responsibilities, Qualifications, and Benefits'}
        ]
    }
]

for i, job_type in enumerate(job_types):
    capitalized_job_type = job_type.title()  # Capitalize the first letter of each word
    visible_list = [False] * (len(job_types) + 1)
    visible_list[i + 1] = True  # Adjust the index to account for the added trace
    dropdown_buttons.append(
        {
            'label': capitalized_job_type,
            'method': 'update',
            'args': [
                {'visible': visible_list},
                {'title': f'Correlation Matrix for {capitalized_job_type} Careers'}
            ]
        }
    )

fig.update_layout(
    updatemenus=[
        go.layout.Updatemenu(
            type='dropdown',
            showactive=True,
            buttons=dropdown_buttons,
            x=-0.23,
            xanchor='left',
            y=1.12,
            yanchor='top',
        )
    ]
)

fig.update_layout(font=dict(color='white'))
fig.update_layout(xaxis=dict(showgrid=False))
fig.update_layout(yaxis=dict(showgrid=False))
fig.show()
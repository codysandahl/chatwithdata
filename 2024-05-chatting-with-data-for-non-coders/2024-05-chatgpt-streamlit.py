# Streamlit dashboard using Plotly Express
# TO RUN:
#   streamlit run 2024-05-chatgpt-streamlit.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
data_dictionary = pd.read_csv('../datasets/CRM+Sales+Opportunities/data_dictionary.csv')
sales_teams = pd.read_csv('../datasets/CRM+Sales+Opportunities/sales_teams.csv')
sales_pipeline = pd.read_csv('../datasets/CRM+Sales+Opportunities/sales_pipeline.csv')
accounts = pd.read_csv('../datasets/CRM+Sales+Opportunities/accounts.csv')
products = pd.read_csv('../datasets/CRM+Sales+Opportunities/products.csv')

# Merge sales_teams with sales_pipeline
merged_data = pd.merge(sales_pipeline, sales_teams, on="sales_agent", how="left")

# Filter to include only 'Won' and 'Lost' deals
filtered_deals = merged_data[merged_data['deal_stage'].isin(['Won', 'Lost'])]

# Calculate win rates for each sales agent
agent_performance = filtered_deals.groupby(['sales_agent', 'deal_stage']).size().unstack(fill_value=0)
agent_performance['Total Deals'] = agent_performance['Won'] + agent_performance['Lost']
agent_performance['Win Rate (%)'] = (agent_performance['Won'] / agent_performance['Total Deals']) * 100

# Filter agents with win rate of 65% or higher
high_performing_agents = agent_performance[agent_performance['Win Rate (%)'] >= 65].reset_index()

# Merge to get manager information
high_performing_agents = pd.merge(high_performing_agents, sales_teams[['sales_agent', 'manager']], on='sales_agent', how='left')

# Count high-performing agents per manager
high_performers_count = high_performing_agents.groupby('manager').size().reset_index(name='Number of High Performing Agents')

# Sort the high_performers_count dataframe by 'Number of High Performing Agents' in descending order
high_performers_count = high_performers_count.sort_values(by='Number of High Performing Agents', ascending=False)

# Group by manager to get the total sales per team and sort by descending value
team_performance = filtered_deals[filtered_deals['deal_stage'] == 'Won'].groupby('manager')['close_value'].sum().reset_index()
team_performance = team_performance.sort_values(by='close_value', ascending=False)
# Create a new column 'color' and set its value based on the rank of 'close_value'
team_performance['color'] = ['green' if x < 3 else 'blue' for x in range(len(team_performance))]

# Create a bar chart of team performance
fig1 = px.bar(team_performance, x='manager', y='close_value', title='Sales Team Performance by Manager',
             labels={'close_value': 'Total Sales Value', 'manager': 'Manager'},
             hover_data={'close_value': ':.0f'},
             color='color', color_discrete_map="identity" # Use the explicit colors defined in the "color" column instead of using plotly's color mapping
        )
# Format the hover labels as dollars with commas
fig1.update_traces(hovertemplate='Total Sales Value: $%{y:,.0f}<extra></extra>')
# Format the y axis to be in the format $1.5M
fig1.update_yaxes(tickprefix="$")

# Create a bar chart of the number of high-performing agents per manager
fig2 = px.bar(high_performers_count, x='manager', y='Number of High Performing Agents', 
              title='High Performing Agents per Manager (Win Rate >= 65%)',
              labels={'Number of High Performing Agents': 'Number of High Performing Agents', 'manager': 'Manager'})

# Streamlit dashboard
st.title('Sales Team Performance Dashboard')

st.plotly_chart(fig1)
st.plotly_chart(fig2)

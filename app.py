import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page config
st.set_page_config(layout="wide", page_title="Security Analytics Dashboard")

# Generate or load data
@st.cache_data
def load_data():
    return pd.read_csv("synthetic_security_data.csv")

df = load_data()

# Sidebar filters
st.sidebar.title("Filters")

# Create filter sections with multiselect
selected_customers = st.sidebar.multiselect(
    "Customer ID",
    options=sorted(df['CUSTOMERID'].unique()),
    default=[]
)

selected_apps = st.sidebar.multiselect(
    "App ID",
    options=sorted(df['APPID'].unique()),
    default=[]
)

selected_os = st.sidebar.multiselect(
    "Operating System",
    options=sorted(df['OS'].unique()),
    default=[]
)

selected_builds = st.sidebar.multiselect(
    "Build Identifier",
    options=sorted(df['PROTECTEDBUILDIDENTIFIER'].unique()),
    default=[]
)

selected_countries = st.sidebar.multiselect(
    "Country",
    options=sorted(df['GEOIP_COUNTRYNAME'].unique()),
    default=[]
)

selected_timezones = st.sidebar.multiselect(
    "Timezone",
    options=sorted(df['GEOIP_TZ'].unique()),
    default=[]
)

# Filter data based on selections
filtered_df = df.copy()

if selected_customers:
    filtered_df = filtered_df[filtered_df['CUSTOMERID'].isin(selected_customers)]
if selected_apps:
    filtered_df = filtered_df[filtered_df['APPID'].isin(selected_apps)]
if selected_os:
    filtered_df = filtered_df[filtered_df['OS'].isin(selected_os)]
if selected_builds:
    filtered_df = filtered_df[filtered_df['PROTECTEDBUILDIDENTIFIER'].isin(selected_builds)]
if selected_countries:
    filtered_df = filtered_df[filtered_df['GEOIP_COUNTRYNAME'].isin(selected_countries)]
if selected_timezones:
    filtered_df = filtered_df[filtered_df['GEOIP_TZ'].isin(selected_timezones)]

# Main content
st.title("Security Analytics Dashboard")

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_events = filtered_df[[col for col in filtered_df.columns if col.startswith('COUNT_')]].sum().sum()
    st.metric("Total Security Events", f"{total_events:,}")

with col2:
    total_apps = filtered_df['APPID'].nunique()
    st.metric("Unique Applications", total_apps)

with col3:
    total_countries = filtered_df['GEOIP_COUNTRYNAME'].nunique()
    st.metric("Countries Affected", total_countries)

with col4:
    high_risk_events = filtered_df[[
        'COUNT_ROOTINGDETECTED', 
        'COUNT_DEBUGGERDETECTED',
        'COUNT_TAMPERINGDETECTED'
    ]].sum().sum()
    st.metric("High Risk Events", f"{high_risk_events:,}")


# Detailed data section
st.subheader("Filtered Data")
event_columns = [col for col in filtered_df.columns if col.startswith('COUNT_')]
agg_data = filtered_df.groupby(['CUSTOMERID', 'APPID', 'OS'])[event_columns].sum().reset_index()
st.dataframe(agg_data, height=200)

# Prepare data for multivariate time series plot
# Convert timestamp to datetime
filtered_df['INGESTTIME_HOUR'] = pd.to_datetime(filtered_df['INGESTTIME_HOUR'])

# Group by UIDs and timestamp
uid_cols = ['CUSTOMERID', 'APPID', 'OS', 'PROTECTEDBUILDIDENTIFIER', 'GEOIP_COUNTRYNAME', 'GEOIP_TZ']
event_cols = [col for col in filtered_df.columns if col.startswith('COUNT_')]

# Create a unique identifier for each combination of UIDs
filtered_df['UID_COMBO'] = filtered_df[uid_cols].apply(lambda x: '_'.join(x.astype(str)), axis=1)

# Group by timestamp and UID combination
grouped_df = filtered_df.groupby(['INGESTTIME_HOUR',])[event_cols].sum().reset_index()

# Create multivariate plot
st.subheader("Multivariate Time Series Analysis of Security Events")


fig = go.Figure()

    
for event in event_cols:
    fig.add_trace(go.Scatter(
        x=grouped_df['INGESTTIME_HOUR'],
        y=grouped_df[event],
        name=f"{event.replace('COUNT_', '')}",
        mode='lines+markers'
    ))

fig.update_layout(
    height=600,
    title="Security Events Over Time by UID Combination",
    xaxis_title="Time",
    yaxis_title="Event Count",
    hovermode='x unified',
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=1.05
    )
)

st.plotly_chart(fig, use_container_width=True)




# Charts row 1
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Security Events by Type")
    event_counts = filtered_df[[col for col in filtered_df.columns if col.startswith('COUNT_')]].sum()
    event_counts.index = [col.replace('COUNT_', '').title() for col in event_counts.index]
    
    fig1 = go.Figure(data=[
        go.Bar(x=event_counts.index, y=event_counts.values)
    ])
    fig1.update_layout(
        height=400,
        xaxis_tickangle=-45,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    st.subheader("Events Distribution by OS")
    os_events = filtered_df.groupby('OS')[[col for col in filtered_df.columns if col.startswith('COUNT_')]].sum()
    
    fig2 = go.Figure()
    for event_type in os_events.columns:
        fig2.add_trace(go.Bar(
            name=event_type.replace('COUNT_', '').title(),
            x=os_events.index,
            y=os_events[event_type],
        ))
    
    fig2.update_layout(
        barmode='stack',
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)

# Charts row 2
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("Geographical Distribution")
    country_events = filtered_df.groupby('GEOIP_COUNTRYNAME')[[col for col in filtered_df.columns if col.startswith('COUNT_')]].sum()
    country_total = country_events.sum(axis=1).sort_values(ascending=False).head(10)
    
    fig3 = go.Figure(data=[
        go.Bar(x=country_total.index, y=country_total.values)
    ])
    fig3.update_layout(
        height=400,
        xaxis_tickangle=-45,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig3, use_container_width=True)

with chart_col4:
    st.subheader("Events Timeline")
    filtered_df['INGESTTIME_HOUR'] = pd.to_datetime(filtered_df['INGESTTIME_HOUR'])
    hourly_events = filtered_df.groupby('INGESTTIME_HOUR')[[col for col in filtered_df.columns if col.startswith('COUNT_')]].sum()
    
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=hourly_events.index,
        y=hourly_events.sum(axis=1),
        mode='lines+markers'
    ))
    fig4.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig4, use_container_width=True)



# Calculate and display risk scores
st.subheader("Risk Analysis")
risk_col1, risk_col2 = st.columns(2)

with risk_col1:
    # Calculate risk score per app
    risk_weights = {
        'COUNT_ROOTINGDETECTED': 5,
        'COUNT_DEBUGGERDETECTED': 4,
        'COUNT_TAMPERINGDETECTED': 5,
        'COUNT_HOOKINGDETECTED': 4,
        'COUNT_OVERLAYDETECTED': 3,
        'COUNT_BOOTLOADERUNLOCKDETECTED': 3,
        'COUNT_EMULATORDETECTED': 2
    }
    
    risk_df = filtered_df.copy()
    for col, weight in risk_weights.items():
        risk_df[f'{col}_weighted'] = risk_df[col] * weight
    
    risk_scores = risk_df.groupby('APPID')[[f'{col}_weighted' for col in risk_weights.keys()]].sum()
    risk_scores['Total_Risk_Score'] = risk_scores.sum(axis=1)
    
    fig5 = go.Figure(data=[
        go.Bar(x=risk_scores.index, y=risk_scores['Total_Risk_Score'])
    ])
    fig5.update_layout(
        title="Risk Score by Application",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig5, use_container_width=True)

with risk_col2:
    # Time-based risk analysis
    risk_df['INGESTTIME_HOUR'] = pd.to_datetime(risk_df['INGESTTIME_HOUR'])
    time_risk = risk_df.groupby('INGESTTIME_HOUR')[[f'{col}_weighted' for col in risk_weights.keys()]].sum()
    time_risk['Total_Risk_Score'] = time_risk.sum(axis=1)
    
    fig6 = go.Figure(data=[
        go.Scatter(x=time_risk.index, y=time_risk['Total_Risk_Score'], mode='lines+markers')
    ])
    fig6.update_layout(
        title="Risk Score Timeline",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig6, use_container_width=True)
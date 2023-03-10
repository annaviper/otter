import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(
    page_title="Otter: Onboarding dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state='collapsed'
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


@st.cache_data
def get_data_from_excel(path: str):
    return pd.read_excel(path)


df = get_data_from_excel('data/data_clean.xlsx')
# df_gb = get_data_from_excel('data/data_groupby.xlsx')

# SIDEBAR
st.sidebar.header("Filters")

csm_status = st.sidebar.multiselect(
    "Select the CSM Status:",
    options=df['CSM Status Stage'].unique(),
    default=df['CSM Status Stage'].unique()
)

region = st.sidebar.multiselect(
    "Select the region:",
    options=df.Region.unique(),
    default=df.Region.unique()
)

st.sidebar.selectbox('Select data', ('q2', 'q3'))

highest_product = st.sidebar.multiselect(
    "Select the product level:",
    options=df['Highest Product'].unique(),
    default=df['Highest Product'].unique()
)

df_selection = df.query(
    "`CSM Status Stage` == @csm_status & Region == @region & `Highest Product` == @highest_product"
)

st.sidebar.markdown('''
---
Created with ❤️ by Anna.
''')

# MAIN PAGE
# ---------------------------- Row A
fontsize = 50
valign = "left"
sline = "CX Onboarding"
lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'

htmlstr = f"""<p style='background-color: rgb(154,216,225); 
                        color: rgb(0,0,0, 0.75); 
                        font-size: {fontsize}px; 
                        border-radius: 7px; 
                        padding-left: 12px; 
                        padding-top: 18px; 
                        padding-bottom: 18px; 
                        line-height:25px;'>
                        </style><BR><span style='font-size: {fontsize}px; 
                        margin-top: 0;'>{sline}</style></span></p>"""

st.markdown(lnk + htmlstr, unsafe_allow_html=True)

st.markdown("""
### Active users metrics
Users who have logged in
""")
col1, col2, col3, col4, col5, col6 = st.columns(6)

# Daily
daily_users = df_selection[df_selection['Last Product usage date'].notna()].groupby('Date')['Account ID'].nunique().reset_index()
today = daily_users.max()['Date']
dau_today = int(daily_users[daily_users['Date'] == today]['Account ID'])

# Yesterday
yesterday = today - pd.Timedelta(days=1)
dau_yesterday = int(daily_users[daily_users['Date'] == yesterday]['Account ID'])
before_yesterday = yesterday - pd.Timedelta(days=1)
before_yesterday = int(daily_users[daily_users['Date'] == before_yesterday]['Account ID'])

# Week
last_week = today - pd.Timedelta(days=7)
previous_week = last_week - pd.Timedelta(days=7)
dau_week = int(daily_users[daily_users['Date'] == last_week]['Account ID'])
previous_week = int(daily_users[daily_users['Date'] == previous_week]['Account ID'])

# Month
last_month = today - pd.Timedelta(days=30)
previous_month = last_month - pd.Timedelta(days=30)
dau_month = int(daily_users[daily_users['Date'] == last_month]['Account ID'])
previous_month = int(daily_users[daily_users['Date'] == previous_month]['Account ID'])

dau_average = round(daily_users['Account ID'].mean(), 1)

with col1:
    st.metric("DAU (today) ", dau_today, f"{round((dau_today - dau_yesterday)/dau_yesterday * 100, 1)}% vs yesterday ({dau_yesterday})")
col2.metric("DAU (yesterday)", dau_yesterday, f"{round((dau_yesterday - before_yesterday)/before_yesterday * 100, 1)}% vs day before ({before_yesterday})")
col3.metric("WAU (last 7 days)", dau_week, f"{round((dau_week - previous_week)/previous_week * 100, 1)}% vs week before ({previous_week})")
col4.metric("MAU (last 30 days)", dau_month, f"{round((dau_month - previous_month)/previous_month * 100, 1)}% vs month before ({previous_month})")
col5.metric("DAU (average)", dau_average)
col6.metric("Stickiness (DAU/MAU)", f"{round(dau_today/dau_month, 2)*100}%")

fig_growth = px.line(daily_users, x='Date', y='Account ID', title="<b>Daily Active Users</b>")
fig_growth.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))
fig_growth.update_yaxes(rangemode="tozero")
st.plotly_chart(fig_growth, use_container_width=True)

#---------------------------- ROW B
# CHURN ANALYTICS
c1, c2, c3 = st.columns(3)
with c1:
    # st.markdown('### Churn')
    # by_csm = df.groupby('CSM Status Stage').count()['Account ID'].reset_index()
    # churned_total = int(by_csm[by_csm['CSM Status Stage'] == 'Churned']['Account ID'])
    # no_churned_total = by_csm[by_csm['CSM Status Stage'] != 'Churned']['Account ID'].sum()
    # churn_data = pd.DataFrame({'churn': [churned_total], 'not_churn': [no_churned_total]}).T.reset_index()
    # fig_pie = px.pie(churn_data, names='index', values=0)
    # st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('### Churn by region')
    churn_by_region = df_selection[df_selection['CSM Status Stage'] == 'Churned'].groupby(['Region']).count()[
        'Account ID'].reset_index().rename(columns={'Account ID': 'total_users_churned'})
    not_churn_by_region = df_selection.groupby(['Region']).nunique()['Account ID'].reset_index().rename(
        columns={'Account ID': 'total_users'}).iloc[0:4]
    churn_by_region['total_users'] = not_churn_by_region['total_users']

    fig_churn_by_region = make_subplots(specs=[[{"secondary_y": True}]])
    fig_churn_by_region.add_trace(
        go.Bar(x=churn_by_region['Region'], y=churn_by_region['total_users_churned'], name="Churned"),
        secondary_y=False)
    fig_churn_by_region.add_trace(
        go.Scatter(x=churn_by_region['Region'], y=churn_by_region['total_users'], name="Total users", mode="lines"),
        secondary_y=True)
    fig_churn_by_region.update_xaxes(title_text="Region")

    # Set y-axes titles
    fig_churn_by_region.update_yaxes(title_text="Churn", secondary_y=False)
    fig_churn_by_region.update_yaxes(title_text="Total users", secondary_y=True)
    st.plotly_chart(fig_churn_by_region, use_container_width=True)
with c2:
    st.markdown('### Churn rate by product')
    churn_by_product = df_selection[df_selection['CSM Status Stage'] == 'Churned'].groupby(['Highest Product', 'CSM Status Stage']).count()[
        'Account ID'].reset_index()
    fig_churn_by_product = px.bar(churn_by_product, x='Highest Product', y='Account ID')
    st.plotly_chart(fig_churn_by_product, use_container_width=True)
with c3:
    st.markdown('### Churn by number of delivery partners')
    churn_by_partners = df[df['CSM Status Stage'] == 'Churned'].groupby(['# delivery partners']).count()[
        'Account ID'].reset_index()
    fig_churn_by_partners = px.bar(churn_by_partners, x='# delivery partners', y='Account ID')
    st.plotly_chart(fig_churn_by_partners, use_container_width=True)

#---------------------------- ROW C
col1, col2 = st.columns(2)
with col1:
    st.markdown("""### Users that have logged in""")
    logged_in = df_selection.groupby(['CSM Status Stage', 'has_logged_in']).count().sort_values(['Account ID', 'CSM Status Stage'], ascending=False).reset_index()
    fig = px.bar(logged_in, x="CSM Status Stage", y='Account ID', color="has_logged_in", barmode='group')
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.markdown("""### Users that have logged in""")
    logged_in = df_selection.groupby(['CSM Status Stage', 'has_logged_in']).count().sort_values(['Account ID', 'CSM Status Stage'], ascending=False).reset_index()
    fig = px.bar(logged_in, x="CSM Status Stage", y='Account ID', color="has_logged_in", barmode='group')
    st.plotly_chart(fig, use_container_width=True)

# ACTIVE BY REGION
# st.markdown('### Active by region')
# product_by_region = df_selection.groupby("Region").count()[['CSM Status Stage']].sort_values('CSM Status Stage',
#                                                                                              ascending=False)
# fig_product_by_region = px.bar(
#     product_by_region, x='CSM Status Stage', y=product_by_region.index,
#     title="<b>Product by region</b>",
#     # color_discrete_sequence=["#0083B8"] * len(product_by_region)
# )
# fig_product_by_region.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))
# st.plotly_chart(fig_product_by_region)
#
# # Row C
# fig_growth = px.line(
#     df_gb, x='year_month', y='growth',
#     title="<b>Growth rate</b>",
#     # color_discrete_sequence=["#0083B8"] * len(product_by_region)
# )
# fig_growth.update_layout(
#     plot_bgcolor="rgba(0,0,0,0)",
#     xaxis=(dict(showgrid=False))
# )
#
# fig_growth.update_yaxes(rangemode="tozero")
#
# st.plotly_chart(
#     fig_growth,
#     # use_container_width=True
# )
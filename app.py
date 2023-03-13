import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(
    page_title="Otter: Onboarding dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state='expanded'
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


@st.experimental_memo
def get_data_from_excel(path: str):
    return pd.read_excel(path)


df = get_data_from_excel('data/data_clean.xlsx')

# SIDEBAR
st.sidebar.header("Filters")

highest_product_unique = df['Highest Product'].unique()
highest_product = st.sidebar.multiselect("Select the product level:", options=highest_product_unique, default=highest_product_unique)

csm_unique = df[df['CSM Status Stage'].notna()]['CSM Status Stage'].unique()
csm_status = st.sidebar.multiselect(
    "Select the CSM status:", options=csm_unique, default=csm_unique)

region = st.sidebar.multiselect(
    "Select the region:",
    options=df.Region.unique(),
    default=df.Region.unique()
)

df_selection = df.query("`CSM Status Stage` == @csm_status & Region == @region & `Highest Product` == @highest_product")

# MAIN PAGE
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
### Active users metrics""")
st.caption('Users who have logged in')
col1, col2, col3, col4, col5, col6 = st.columns(6)

# Daily
daily_users = df_selection[df_selection['date_usage'].notna()].groupby('date_usage')['Account ID'].nunique().reset_index()
today = daily_users.max()['date_usage']
dau_today = int(daily_users[daily_users['date_usage'] == today]['Account ID'])

# Yesterday
yesterday = today - pd.Timedelta(days=1)
dau_yesterday = int(daily_users[daily_users['date_usage'] == yesterday]['Account ID'])
before_yesterday = yesterday - pd.Timedelta(days=1)
dau_before_yesterday = int(daily_users[daily_users['date_usage'] == before_yesterday]['Account ID'])

# Weekly
week = df_selection.copy()
week['date_w'] = pd.to_datetime(week['date_usage']) - pd.to_timedelta(7, unit='d')
week = week.groupby([pd.Grouper(key='date_w', freq='W-MON')])['Account ID'].nunique().reset_index().sort_values('date_w')[['date_w', 'Account ID']]
current_week = week.iloc[-1]['date_w']
dau_week = int(week.iloc[-1]['Account ID'])
wau_previous = int(week.iloc[-2]['Account ID'])

# Monthly
month = df_selection.copy()
month['date_usage'] = pd.to_datetime(month['date_usage'])
month = month.groupby(month.date_usage.dt.month)['Account ID'].nunique().reset_index().sort_values('date_usage')
mau = int(month.iloc[-1]['Account ID'])
mau_previous = int(month.iloc[-2]['Account ID'])

dau_average = round(daily_users['Account ID'].mean(), 1)

stickiness = (dau_today/mau) * 100

with col1:
    st.metric("DAU (today) ", dau_today, f"{round((dau_today - dau_yesterday)/dau_yesterday * 100, 1)}% vs yesterday ({dau_yesterday})")
    col2.metric("DAU (yesterday)", dau_yesterday, f"{round((dau_yesterday - dau_before_yesterday)/dau_before_yesterday * 100, 1)}% vs day before ({dau_before_yesterday})")
    col3.metric("WAU (last 7 days)", dau_week, f"{round((dau_week - wau_previous)/wau_previous * 100, 1)}% vs week before ({wau_previous})")
    col4.metric("MAU (last 30 days)", mau, f"{round((mau - mau_previous)/mau_previous * 100, 1)}% vs month before ({mau_previous})")
    col5.metric("DAU (average)", dau_average)
    col6.metric("Stickiness (DAU/MAU)", f"{round(stickiness, 2)}%")

fig_growth = px.line(daily_users, x='date_usage', y='Account ID', title="<b>Daily Active Users</b>")
fig_growth.update_yaxes(rangemode="tozero")
fig_growth.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1m",
                     step="month",
                     stepmode="backward"),
                dict(count=3,
                     label="3m",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="YTD",
                     step="year",
                     stepmode="todate"),
                dict(count=1,
                     label="1y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=False),
        type="date"
    )
)
st.plotly_chart(fig_growth, use_container_width=True)

#---------------------------- ROW B
col1, col2 = st.columns(2)
with col1:
    st.markdown("""### Logged-in users by CSM status""")
    logged_in = df_selection.groupby(['CSM Status Stage', 'has_logged_in']).count().sort_values(['Account ID', 'CSM Status Stage'], ascending=False).reset_index()
    fig = px.bar(logged_in, x="CSM Status Stage", y='Account ID', color="has_logged_in", barmode='group')
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.markdown("""### Users by product""")
    df_selection = df_selection[df_selection['Region'] != 'Unknown']
    gb = df_selection.groupby(['Region', 'Highest Product']).nunique().reset_index()
    fig_growth = px.bar(gb, x='Region', y='Account ID', color='Highest Product', barmode='group')
    fig_growth.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))
    fig_growth.update_yaxes(rangemode="tozero")

    st.plotly_chart(fig_growth, use_container_width=True)

# CHURN ANALYTICS
c1, c2, c3 = st.columns(3)
with c1:
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
    churn_by_partners = df_selection[df_selection['CSM Status Stage'] == 'Churned'].groupby(['# delivery partners']).count()[
        'Account ID'].reset_index()
    fig_churn_by_partners = px.bar(churn_by_partners, x='# delivery partners', y='Account ID')
    st.plotly_chart(fig_churn_by_partners, use_container_width=True)

st.markdown('''
---
Created with ❤️ by Anna.
''')

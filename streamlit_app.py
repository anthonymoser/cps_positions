import pandas as pd
import plotly.express as px
import streamlit as st 

st.set_page_config(layout="wide")
@st.cache
def get_data():
    df = pd.read_csv('position_metadata.csv')
    jobs = list(pd.read_csv('jobs.csv').job_title.sort_values())
    depts = sorted(list(pd.read_csv('depts.csv').department.dropna().sort_values()))
    return df, jobs, depts


def get_figure(data, selected_jobs, selected_depts, width, height):

    
    print("Generating figure")
    fig = px.bar(data, x='date', y='positions', color='status', barmode='stack', 
                color_discrete_map = {
                    'Filled': 'lightskyblue',
                    'Change in staff': 'dodgerblue',
                    'Open': 'tomato'
                },
                facet_row = 'department',
                facet_col = 'job_title',
                text='positions'
            )

    fig.update_layout(
        # title=f"{selected_jobs}",
        yaxis_title = 'Positions',
        xaxis={'categoryorder':'array', 'categoryarray':list(data.date.sort_values())},
        yaxis = {'categoryorder': 'array', 'categoryarray': ["Filled", "Change in staff", "Open"]},
        width = width,
        height = height
        )
    return fig 


def filter_data(df, selected_jobs, selected_depts, group_data = True):
    fig_width = 500 * max(len(selected_jobs),1)
    fig_height = 500 * max(len(selected_depts), 1)
    
    print("Filtering data")
    if len(selected_depts) >= 1 and len(selected_jobs) == 0:
        fig_width = 500
        if group_data is False:
            ff = df[ df.department.isin(selected_depts) ].groupby(['department', 'date', 'status']).positions.sum().reset_index()
            ff['job_title'] = "Combined jobs"
            
        elif group_data is False:
            ff = df[ df.department.isin(selected_depts) ].groupby(['date', 'status']).positions.sum().reset_index()
            ff['department'] = "Combined selection"
            ff['job_title'] = "Combined jobs"
            
    if len(selected_depts) == 0 and len(selected_jobs) > 0:
        fig_height = 500
        if group_data is False:
            ff = df[df.job_title.isin(selected_jobs)].groupby(['job_title', 'date', 'status']).positions.sum().reset_index()
            ff['department'] = "Combined depts"
        elif group_data is True:
            ff = df[df.job_title.isin(selected_jobs)].groupby(['date', 'status']).positions.sum().reset_index()
            ff['department'] = "Combined depts"
            ff['job_title'] = "Combined jobs"
        
    if len(selected_depts) > 0 and len(selected_jobs) > 0:
        ff = (
                df[(df.department.isin(selected_depts)) & (df.job_title.isin(selected_jobs))]
                    .groupby(['department', 'job_title', 'date', 'status'])
                    .positions.sum()
                    .reset_index()
        )

    return ff, fig_width, fig_height


df, jobs, depts = get_data()
selected_jobs = st.sidebar.multiselect("Choose job(s)", options=jobs)
selected_depts = st.sidebar.multiselect("Choose department(s)", options=depts)
add_graph = st.sidebar.button("Show graphs")
group_data = st.sidebar.checkbox("Group schools and positions", value=True)
if add_graph:
    print(selected_jobs, selected_depts)
    print(len(selected_jobs), len(selected_depts))
    data, width, height = filter_data(df, selected_jobs, selected_depts, group_data)
    
    
    fig = get_figure(data.sort_values('date'), selected_jobs, selected_depts, width, height)
    st.plotly_chart(fig)
    st.dataframe(data)


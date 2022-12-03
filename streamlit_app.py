import pandas as pd
import plotly.express as px
import streamlit as st 
import base64

st.set_page_config(layout="wide")
@st.cache
def get_data():
    df = pd.read_csv('data/position_metadata.csv')
    jobs = list(pd.read_csv('data/jobs.csv').job_title.sort_values())
    depts = sorted(list(pd.read_csv('data/depts.csv').department.dropna().sort_values()))
    tl = pd.read_csv('data/positions_over_time.csv')
    return df, jobs, depts, tl


def get_figure(data, width, height):

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


def filter_graph_data(df, selected_jobs, selected_depts, group_jobs = True, group_depts = True):

    print("Filtering data")

    groupby_fields = ['date', 'status']
    
    if group_depts is False and 0 < len(selected_depts) <= 5:
        groupby_fields.append('department')
    
    if group_jobs is False and 0 < len(selected_jobs) <= 5:
        groupby_fields.append('job_title')
    
    job_filter  = (df.job_title.isin(selected_jobs)) | (len(selected_jobs) == 0)
    dept_filter = (df.department.isin(selected_depts)) | (len(selected_depts) == 0)
    
    ff = ( df[(job_filter) & (dept_filter)]
            .groupby(groupby_fields).positions.sum()
            .reset_index() )
    
    if 'department' not in ff.columns:
        ff['department'] = "Combined selection" if len(selected_depts) > 0 else "District Totals"
    
    if 'job_title'  not in ff.columns:
        ff['job_title'] = "Combined jobs"

    fig_width =  800 * min(len(ff.job_title.unique()), 5)
    fig_height = 600 * min(len(ff.department.unique()), 5)

    return ff, fig_width, fig_height


def filter_jobs(df, selected_jobs):
    if len(selected_jobs) == 0:
        return df
    else:
        return df[df.job_title.isin(selected_jobs)]


def filter_depts(df, selected_depts):
    if len(selected_depts) == 0:
        return df
    else:
        return df[df.department.isin(selected_depts)]


def filter_source_data(tl, selected_jobs, selected_depts):
    
    df = ( tl
            .pipe(filter_jobs, selected_jobs)
            .pipe(filter_depts, selected_depts)
    )
    return df 


def get_table_download_link(df, download_filename, link_text="CSV"):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    # df.to_csv(f'data/{download_filename}', index=False)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="{download_filename}">{link_text}</a>'
    return href

full_source_url = "https://drive.google.com/file/d/18BUAV6KAPfx6um3h6BODCMrMOFAPmpLp/view?usp=share_link"

about_this_tool = f"""
# CPS Positions Over Time
This tool was built by Anthony Moser. The data unifies these [CPS employee position files](https://www.cps.edu/about/finance/employee-position-files/).  
Under the hood it's basically a pivot table of position_ids over the reporting dates (you can [download that data here]({full_source_url})).   
The categories represent a comparison of each reporting date to the one immediately prior.  

* "Filled" means the position continues to be filled by the staff member.
* "Change in staff" means the name listed in the position file has changed.
* "Open" means nobody is assigned to the role.

If you look at the source data, there's another category, "DNE" for "did not exist". 
That represents positions that had no reporting data for that period, as distinct from open positions.
"""

df, jobs, depts, tl = get_data()
selected_jobs       = st.sidebar.multiselect("Choose job(s)", options=jobs)
selected_depts      = st.sidebar.multiselect("Choose department(s)", options=depts)
add_graph           = st.sidebar.button("Show graphs")
group_jobs          = st.sidebar.checkbox("Group positions", value=True)
group_depts         = st.sidebar.checkbox("Group depts", value = True)
show_data           = st.sidebar.checkbox("Show source data", value = False)
compare_to_district = st.sidebar.checkbox("Compare to district", value = False)

st.markdown(about_this_tool)

if add_graph:

    data, width, height = filter_graph_data(df, selected_jobs, selected_depts, group_jobs, group_depts)
    fig = get_figure(data.sort_values('date'), width, height)
    st.plotly_chart(fig)
    
    if compare_to_district:
        data, width, height = filter_graph_data(df, selected_jobs, [], group_jobs, True)
        fig = get_figure(data.sort_values('date'), width, height)
        st.plotly_chart(fig)
        
    fsd = filter_source_data(tl, selected_jobs, selected_depts)
    if len(selected_depts) == 0 and len(selected_jobs) == 0:
        st.markdown(f'[Download the unfiltered data set]({full_source_url})')
    else:
        st.markdown(get_table_download_link(fsd, 'Filtered CPS Position Data.csv', 'Download filtered source data'), unsafe_allow_html=True)
    
    if show_data:
        st.write("Metadata")
        st.dataframe(data)
        
        st.write("Position file data")
        st.dataframe(fsd)
    
    



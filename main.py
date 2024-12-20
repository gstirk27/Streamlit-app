import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from my_plots import *
import streamlit as st

@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

@st.cache_data
def ohw(df):
    nunique_year = df.groupby(['name', 'sex'])['year'].nunique()
    one_hit_wonders = nunique_year[nunique_year == 1].index
    one_hit_wonder_data = df.set_index(['name', 'sex']).loc[one_hit_wonders].reset_index()
    return one_hit_wonder_data

data = load_name_data()
ohw_data = ohw(data)

st.title("US Names:)")

with st.sidebar:
    input_name = st.text_input('Enter a name:', 'John')
    name_data = data[data['name']==input_name].copy()
    year_input = st.slider('Year', min_value=1880,max_value=2023,value=2000)
    

tab1, tab2, tab3 = st.tabs(['Name Trends','Top Names','How Common'])
with tab1:
    fig = px.line(name_data, x='year',y='count',color='sex')
    st.plotly_chart(fig)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        n_names = st.radio('Number of names per sex', [3,5,10])
        fig2 = top_names_plot(data,year=year_input,n=n_names)
        st.plotly_chart(fig2)

    with col2: 
        st.write(f'Unique Names Table for {year_input}')
        output_table = unique_names_summary(data,year=year_input)
        st.dataframe(output_table)

with tab3:
    st.write(f'How common is the name {input_name}?')
    common_names = common_name_summary(name_data,input_name)
    st.write(common_names)

    st.subheader('Comparison ')
    name2 = st.text_input('Enter another name', 'Mary')
    name2_data = data[data['name']==name2].copy()
    second_name_info = common_name_summary(name2_data,name2)
    st.write(second_name_info)
    compare = name_comparison(name_data,name2_data,input_name,name2,year_input)
    st.write(compare)

    st.subheader("Name Frequencies")
    st.plotly_chart(name_frequencies_plot(data,year=year_input))

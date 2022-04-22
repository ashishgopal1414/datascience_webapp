# Core Packages
import io, os,sys, shutil, time
import numpy as np
from os import path
import missingno as msno

import streamlit as st

# EDA Packages
import pandas as pd
import numpy as numpy

# Data Viz Packages
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import seaborn as sns
import plotly.express as px
import missingno as msno
from pandas_profiling import ProfileReport
import io, os, shutil, re, time, pickle, pathlib, glob, base64, xlsxwriter
from io import BytesIO

## Disable Warning
st.set_option('deprecation.showfileUploaderEncoding', False)
# st.set_option('deprecation.showPyplotGlobalUse', False)
#%%

data_flag = 0

#%%
current_path = os.getcwd()

## Create sub directories if not created: "Raw Data" , "Batch Wise Data" , "Aggregated Data"
folder_names = [name for name in ["Raw Data" , "Modified Data"]]

for folder_name in folder_names:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
#%%

datafile_path = os.path.join(current_path, "Raw Data", "data.csv")
modifiedfile_path = os.path.join(current_path, "Modified Data", "data.csv")

data_df = pd.DataFrame()

################################################################################
# from typing import Dict
# @st.cache(allow_output_mutation=True)
# def get_static_store() -> Dict:
#     """This dictionary is initialized once and can be used to store the files uploaded"""
#     return {}

################################################################################

##@st.cache(suppress_st_warning=True)
def load_data():
    data_df = pd.DataFrame()
    if path.exists(datafile_path):
        data_df = pd.read_csv(datafile_path)
        if st.checkbox("Click to view data"):
            st.write(data_df)
    return data_df

################################################################################

def load_modified_data():
    data_df = pd.DataFrame()
    if (not os.path.exists(datafile_path)) & (os.path.exists(modifiedfile_path)):
        os.remove(modifiedfile_path)
    if path.exists(modifiedfile_path):
        data_df = pd.read_csv(modifiedfile_path)
        if st.checkbox("Click to view Modified data"):
            st.write(data_df)
    return data_df
################################################################################

def preprocess_data(data_df):
    st.write('---------------------------------------------------')
    if not data_df.empty:
        all_columns = data_df.columns.to_list()
        flag_preprocess = st.checkbox("Data Preprocess (Keep checked in to add steps)",value=True)
        if flag_preprocess:
            ## Receive a function to be called for Preprocessing
            df = data_df.copy()
            txt = st.text_area(
                "Provide lines of code in the given format to preprocess the data, otherwise leave it as commented",
                "## Consider the dataframe to be stored in 'df' variable\n" + \
                "## for e.g.\n" + \
                "## df['col_1'] = df['col_1'].astype('str')")
            if st.button("Finally, Click here to update the file"):
                exec(txt)
                if os.path.exists(modifiedfile_path):
                    os.remove(modifiedfile_path)
                df.to_csv(modifiedfile_path, index=False)
                st.success("New file created successfully under: {}".format(modifiedfile_path))
            if st.checkbox("Click to view Modified file"):
                if os.path.exists(modifiedfile_path):
                    st.write(pd.read_csv(modifiedfile_path))
                else:
                    st.markdown('**No Data Available to show!**.')

    else:
        st.markdown('**No Data Available to show!**.')
    st.write('---------------------------------------------------')

################################################################################
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index = True, sheet_name='Sheet1',float_format="%.2f")
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="Results.xlsx">Download Excel file</a>' # decode b'abc' => abc

def analysis_data(df):
    if not df.empty:
        df = df.copy()
        # st.write(df.shape)

        fig = px.bar(df, y='Variable', x='overall_SHAP_abs',
                     hover_data=['overall_SHAP_abs', 'overall_Corr'],
                     color='overall_Corr',
                     # labels={'pop': 'population of Canada'},
                     height=400,  orientation='h')
        # fig.show()
        st.plotly_chart(fig)
    else:
        st.markdown('**No Data Available to show!**.')

    st.write('---------------------------------------------------')








def main():
    """ Semi Supervised Machine Learning App with Streamlit """
    # static_store = get_static_store()
    # session = SessionState.get(run_id=0)

    st.title("Data Science Webapp")
    #st.text("By Ashish Gopal")

    activities_outer = ["Data Ingestion", "Others", "About"]
    choice_1_outer = st.sidebar.radio("Choose your Step:", activities_outer)

    data = pd.DataFrame()

    if choice_1_outer == "Data Ingestion":
        file_types = ["csv","txt"]

        activities_1 = ["1. Data Import", "2. Data Preprocess", "3. Data Analysis"]
        choice_1 = st.sidebar.selectbox("Select Activities", activities_1)

        if choice_1 == "1. Data Import":
            data = None
            show_file = st.empty()
            flag_uploaddata = st.checkbox("Click to Upload data", value=True)
            if flag_uploaddata:
                data = st.file_uploader("Upload Dataset : ",type=file_types)
            if not data:
                show_file.info("Please upload a file of type: " + ", ".join(file_types))
                if os.path.exists(datafile_path):
                    os.remove(datafile_path)
                return
            if data:
                if st.button("Click to delete data"):
                    if os.path.exists(datafile_path):
                        os.remove(datafile_path)
                        st.write('Raw File deleted successfully!')
                    elif os.path.exists(modifiedfile_path):
                        os.remove(modifiedfile_path)
                        st.write('Modified File deleted successfully!')
                    else:
                        st.write('No Files available for deletion!')
                    # static_store.clear()
                    data = None
                    # session.run_id += 1
                    return

                if data is not None:
                    df = pd.read_csv(data)
                    df.to_csv(datafile_path, index=False)
                    st.write('File loaded successfully!')
                if st.checkbox("Click to view data"):
                    if data is not None:
                        st.write(df)
                    else:
                        st.write('No Data available!')

        if choice_1 == "2. Data Preprocess":
            preprocess_data(load_data())

        if choice_1 == "3. Data Analysis":
            analysis_data(load_modified_data())


    if choice_1_outer == "Others":
        st.write('Coming Soon...')
        st.write('---------------------------------------------------')

    if choice_1_outer == "About":
        st.sidebar.header("About App")
        st.sidebar.info("Data Science Webapp")
        st.title("")
        st.title("")
        st.sidebar.header("About Developer")
        st.sidebar.info("https://www.linkedin.com/in/ashish-gopal-73824572/")
        st.subheader("About Me")
        st.text("Name: Ashish Gopal")
        st.text("Job Profile: Data Scientist")
        IMAGE_URL = "https://avatars0.githubusercontent.com/u/36658472?s=460&v=4"
        st.image(IMAGE_URL, use_column_width=True)
        st.markdown("LinkedIn: https://www.linkedin.com/in/ashish-gopal-73824572/")
        st.markdown("GitHub: https://github.com/ashishgopal1414")
        st.write('---------------------------------------------------')
if __name__ == '__main__':
	main()
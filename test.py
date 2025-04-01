import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px

url = "https://raw.githubusercontent.com/ankitverma4503/streamlit-dashboad-score/main/Assesment%20scores.xlsx"

# Fetch the file
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Load the Excel file from the content of the response
    file_data = BytesIO(response.content)
    
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(file_data, sheet_name="Overall Team's Score")
else:
    print("Failed to download the file.")

# Clean up column names (remove whitespaces, special characters)
df.columns = df.columns.str.strip()

# Add custom CSS to style the app
st.markdown("""
    <style>
        body {
            color: red !important;  /* Make all text red */
        }
        .main {
            background-color: #f0f8ff;
        }
        .sidebar .sidebar-content {
            background-color: #8faadc;
            color: white;
        }
        h1, h2, h3 {
            color: red !important;  /* Make headings red */
            font-family: 'Arial', sans-serif;
            font-weight: bold;
        }
        .stSelectbox {
            background-color: #8faadc;
            color: white;
        }
        .stButton>button {
            background-color: #3b5998;
            color: white;
            border: none;
            border-radius: 5px;
        }
        .stDataFrame {
            background-color: #ffffff;
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            padding: 10px;
        }
        .stMetric {
            background-color: #cce7ff; /* Light blue background for KPIs */
            color: black !important; /* Bold black text for KPIs */
            border-radius: 8px;
            padding: 15px;
            font-weight: bold; /* Make the text bold */
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); /* Optional shadow for better visibility */
        }
        .stPlotlyChart {
            border-radius: 10px;
            padding: 10px;
            background-color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# Add a page title with a custom design
st.title("Evaluation Result")

# Streamlit sidebar for page navigation with custom colors
pages = ['Individual Scores', 'Overall Team Results']
selection = st.sidebar.selectbox("Choose Page", pages)

if selection == 'Individual Scores':
    st.header("Individual Scores")

    # Dynamically identify the correct columns for 'Total marks', 'Interview Score', and 'EXAMS Score'
    total_column = [col for col in df.columns if 'Total' in col][0]  # Identifying Total column dynamically
    interview_column = [col for col in df.columns if 'Interview' in col][0]  # Identifying Interview column dynamically
    exam_column = [col for col in df.columns if 'EXAMS' in col][0]  # Identifying EXAMS column dynamically

    # Grade Categories for filtering (using the existing 'Performance Grading' column)
    grade_filter = st.selectbox("Filter by Performance Grading", ['All', 'Poor', 'Average', 'Good'])

    # Filter data based on selected grade filter
    if grade_filter != 'All':
        filtered_df = df[df['Performance Grading'] == grade_filter]
    else:
        filtered_df = df

    # Allow the user to select an individual from the filtered data
    individuals = filtered_df['Name'].unique()
    selected_individual = st.selectbox("Select Individual", individuals)

    # Filter the data based on the selected individual
    individual_data = filtered_df[filtered_df['Name'] == selected_individual]

    # Display the individual's data
    st.write(f"Scores for {selected_individual}:")
    individual_with_grade = individual_data[['Name', total_column, interview_column, exam_column, 'Performance Grading']]
    st.dataframe(individual_with_grade)

elif selection == 'Overall Team Results':
    st.header("Overall Team Results")

    # Dynamically identify the correct 'Total marks' column
    total_column = [col for col in df.columns if 'Total' in col][0]

    # Calculate key metrics for the team
    total_average = df[total_column].mean()
    total_max = df[total_column].max()
    total_min = df[total_column].min()

    # Display KPIs (Team Average, Max, Min) with customized styling
    st.subheader("Key Performance Indicators (KPIs)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Team Average", value=f"{total_average:.2f}")
    with col2:
        st.metric(label="Max Score", value=f"{total_max}")
    with col3:
        st.metric(label="Min Score", value=f"{total_min}")

    # Sort the dataframe by the total marks column before plotting
    sorted_df = df.sort_values(by=total_column, ascending=False)  # Sort in descending order

    # Create a bar chart of team members' total marks with soft pastel colors
    fig = px.bar(sorted_df, x='Name', y=total_column, title='Total Marks of Each Individual',
                 labels={'Name': 'Individual', total_column: 'Total Marks'},
                 color='Name', color_discrete_sequence=['#a8e0b4', '#f9c2a5', '#a3c4f3', '#f5e1a4', '#f5c9b1'])
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)

    # Filter table by score range (min to max)
    st.subheader("Filtered Team Members Table")

    # Select score range for filtering
    min_score, max_score = st.slider("Select score range", float(df[total_column].min()), float(df[total_column].max()), (float(df[total_column].min()), float(df[total_column].max())))

    # Grade Categories for filtering (using the existing 'Performance Grading' column)
    grade_filter = st.selectbox("Select Performance Grading", ['All', 'Poor', 'Average', 'Good'])

    # Apply filters to the dataframe
    filtered_df = df[(df[total_column] >= min_score) & (df[total_column] <= max_score)]
    
    if grade_filter != 'All':
        filtered_df = filtered_df[filtered_df['Performance Grading'] == grade_filter]

    # Display the filtered table with Name, Total Marks, and Performance Grading
    st.dataframe(filtered_df[['Name', total_column, 'Performance Grading']])

    # Identify top performers (Top 4 people by Total marks)
    st.subheader("Top Performers (Top 4)")  # Red text for title
    top_performers = df.nlargest(4, total_column)
    st.dataframe(top_performers[['Name', total_column, 'Performance Grading']])

import streamlit as st
import plotly.express as px
import pandas as pd
from openai import OpenAI

# Page config
st.set_page_config(
    page_title="HR Attrition Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data
df = pd.read_csv('Data_Set.csv')

# OpenAI client
client = OpenAI(api_key="YOUR_API_KEY_HERE")

# Dashboard title
st.title('📊 HR Attrition Analytics Dashboard')
st.write('An interactive dashboard analyzing employee attrition trends across departments, travel frequency, age, and education level.')
st.divider()

# Chart 1 - Pie Chart
st.subheader('Overall Attrition Rate')
attrition_counts = df['Attrition'].value_counts()
fig1 = px.pie(
    values=attrition_counts.values,
    names=attrition_counts.index,
    title='Overall Employee Attrition Rate',
    color_discrete_sequence=['#2ecc71', '#e74c3c']
)
st.plotly_chart(fig1)

# Chart 2 - Attrition by Department
st.subheader('Attrition by Department')
attrition_by_dept = df.groupby('Department')['Attrition'].apply(
    lambda x: (x == 'Yes').sum() / len(x) * 100
).round(1).reset_index()
attrition_by_dept.columns = ['Department', 'Attrition Rate (%)']
fig2 = px.bar(
    attrition_by_dept,
    x='Department',
    y='Attrition Rate (%)',
    title='Attrition Rate by Department',
    color='Attrition Rate (%)',
    color_continuous_scale='Reds'
)
st.plotly_chart(fig2)

# Chart 3 - Attrition by Business Travel
st.subheader('Attrition by Business Travel')
attrition_by_travel = df.groupby('BusinessTravel')['Attrition'].apply(
    lambda x: (x == 'Yes').sum() / len(x) * 100
).round(1).reset_index()
attrition_by_travel.columns = ['Business Travel', 'Attrition Rate (%)']
fig3 = px.bar(
    attrition_by_travel,
    x='Business Travel',
    y='Attrition Rate (%)',
    title='Attrition Rate by Business Travel Frequency',
    color='Attrition Rate (%)',
    color_continuous_scale='Blues'
)
st.plotly_chart(fig3)

# Chart 4 - Age Distribution
st.subheader('Age Distribution of Leavers vs Stayers')
fig4 = px.histogram(
    df,
    x='Age',
    color='Attrition',
    barmode='overlay',
    title='Age Distribution: Leavers vs Stayers',
    color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'},
    opacity=0.7
)
st.plotly_chart(fig4)

# Chart 5 - Attrition by Education
st.subheader('Attrition by Education Level')
edu_labels = {1: 'Below College', 2: 'College', 3: 'Bachelor', 4: 'Master', 5: 'Doctor'}
attrition_by_edu = df.groupby('Education')['Attrition'].apply(
    lambda x: (x == 'Yes').sum() / len(x) * 100
).round(1).reset_index()
attrition_by_edu.columns = ['Education', 'Attrition Rate (%)']
attrition_by_edu['Education'] = attrition_by_edu['Education'].map(edu_labels)
fig5 = px.bar(
    attrition_by_edu,
    x='Education',
    y='Attrition Rate (%)',
    title='Attrition Rate by Education Level',
    color='Attrition Rate (%)',
    color_continuous_scale='Purples'
)
st.plotly_chart(fig5)

st.divider()

# AI Insight Panel
st.subheader('🤖 AI Generated Insights')
st.write('Click the button below to generate AI insights based on the dashboard data')

# Build data summary to give AI context
overall_attrition = round(
    df[df['Attrition'] == 'Yes'].shape[0] / df.shape[0] * 100, 1
)
dept_attrition = attrition_by_dept.to_string(index=False)
travel_attrition = attrition_by_travel.to_string(index=False)
edu_attrition = attrition_by_edu.to_string(index=False)

data_context = f"""
You are a senior HR business analyst with access to the following workforce data:

Overall Attrition Rate: {overall_attrition}%

Attrition by Department:
{dept_attrition}

Attrition by Business Travel:
{travel_attrition}

Attrition by Education Level:
{edu_attrition}

Use this data to answer any questions the user asks. Be concise and professional,
as if presenting to senior leadership.
"""

if st.button('Generate AI Insights'):
    with st.spinner('Analyzing data...'):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": data_context},
                {"role": "user", "content": "Provide an executive summary of the key trends and 3 actionable recommendations to reduce attrition."}
            ]
        )
        insight = response.choices[0].message.content
        st.write(insight)

st.divider()

# Chat Interface
st.subheader('💬 Chat with Your Data')
st.write('Ask any question about the dashboard data and get an AI powered answer')

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

# Chat input
if prompt := st.chat_input('Ask a question about the data...'):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.write(prompt)

    with st.chat_message('assistant'):
        with st.spinner('Thinking...'):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": data_context},
                    *[{"role": m["role"], "content": m["content"]}
                      for m in st.session_state.messages]
                ]
            )
            reply = response.choices[0].message.content
            st.write(reply)
            st.session_state.messages.append({
                'role': 'assistant',
                'content': reply
            })
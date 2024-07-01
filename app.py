import streamlit as st
import pandas as pd

st.title('AGM App')

# Upload NRIC in Attendance file
st.header('Upload NRIC in Attendance File')
uploaded_attendance_file = st.file_uploader('Choose an Excel file for NRIC in Attendance', type=['xlsx'])

# Upload Response Data file
st.header('Upload Response Data File')
uploaded_response_file = st.file_uploader('Choose an Excel file for Response Data', type=['xlsx'])

if uploaded_attendance_file and uploaded_response_file:
    # Load the uploaded files into DataFrames
    attendance_df = pd.read_excel(uploaded_attendance_file, engine='openpyxl')
    response_df = pd.read_excel(uploaded_response_file, engine='openpyxl')

else:
    st.warning('Please upload both Excel files.')
    st.stop()



import pandas as pd
from collections import Counter

nric_col = 'nric'

# attendance_file = 'data/nric-in-attendance.xlsx'
# attendance_df = pd.read_excel(attendance_file)
# attendance_df = attendance_df[[nric_col]].dropna(axis=0)

# response_file = './data/responses.xlsx'
# response_df = pd.read_excel(response_file)

# do nric filtering

valid_nric = attendance_df.values.flatten()
invalid_nric = [nric for nric in response_df['nric'].values if nric not in valid_nric]

response_df_valid_nric_df = response_df[response_df['nric'].isin(valid_nric)]

# Get the count of each id
id_counts = response_df[nric_col].value_counts()

# Filter to get only duplicated ids (count > 1)
duplicated_ids = id_counts[id_counts > 1]

# Convert to list of tuples
duplicated_ids_list = list(duplicated_ids.items())

response_nric_dedup_df = response_df_valid_nric_df.sort_values(by=[nric_col, 'Timestamp'])

# Drop duplicates, keeping the last occurrence (latest timestamp)
final_df = response_nric_dedup_df.drop_duplicates(subset=[nric_col], keep='last')

questions = [c for c in final_df.columns if c not in ['Timestamp', nric_col]]
questions = [[q.split('. ')[0], q] for q in questions]
question_nums = [q[0] for q in questions]
question_counts = Counter(question_nums)

single_choice_questions = [q[0] for q in question_counts.items() if q[1] == 1]
multi_choice_questions_with_counts = [q for q in question_counts.items() if q[1] != 1]

unique_questions = [[q[0], q[1].split(' [')[0]] for q in questions]
unique_questions_dict = dict()
for q_num, full_q in unique_questions:
    if q_num not in unique_questions_dict:
        unique_questions_dict[q_num] = full_q
        
single_choice_questions_string = ""
for qn in single_choice_questions:
    single_choice_questions_string += f"\n{unique_questions_dict[qn]}"
    
multi_choice_questions_string = ""
for qn in multi_choice_questions_with_counts:
    multi_choice_questions_string += f"\n{unique_questions_dict[qn[0]]}"

output_string = (
    '## Question Overview\n\n'
    f"The single choice questions are: {single_choice_questions_string}\n\n"
    f"The multi choice questions are: \n{multi_choice_questions_string}\n\n"

    '## Response Overview\n\n'
    f'{len(response_df)} Responses received\n\n'
    '>> Invalid NRICs:\n'
    f'{invalid_nric}\n\n'
    f'{len(response_df_valid_nric_df)} Responses received from valid NRICs\n\n'
    ">> Duplicated NRICs and their counts:\n"
    f'{duplicated_ids_list}\n\n'
    f'{len(final_df)} Responses received from valid NRICs (deduplicated)\n'

)


results_string = '## Results\n\n'
for q_num, full_q in sorted(unique_questions_dict.items(), key=lambda x: x[0]):
    results_string += full_q + '\n\n'
    if q_num in single_choice_questions:
        counts = sorted(list(final_df[[full_q]].groupby(full_q).size().items()), key=lambda x: -x[1])
        for count in counts:
            results_string += 'Option: ' + count[0] + '\n'
            results_string += 'Count: ' + str(count[1]) + '\n'
            results_string += 'Percentage: ' + str(round(100 * count[1] / len(final_df), 1)) + ' % \n\n'
        results_string += f'The majority decision is {counts[0][0]} with {counts[0][1]} votes.\n'
    elif q_num in [x[0] for x in multi_choice_questions_with_counts]:
        question_cols = [q[1] for q in questions if q[0] == q_num]
        all_vals = final_df[question_cols].values.flatten()
        vals_counter = sorted(Counter(all_vals).items(), key=lambda x: -x[1])
        for counter in vals_counter:
            results_string += 'Option: ' + counter[0] + '\n'
            results_string += 'Count: ' + str(counter[1]) + '\n'
            results_string += 'Percentage: ' + str(round(100 * counter[1] / len(final_df), 1)) + ' % \n\n'
        num_choices = [x[1] for x in multi_choice_questions_with_counts if x[0] == q_num][0]
        results = vals_counter[:num_choices]
        results = [x[0] for x in results]
        results_string += f'The top {num_choices} options with the most votes are {results}\n'
    else:
        results_string += 'ERROR\n'

    results_string += '\n\n\n\n'

final_string = output_string + results_string

st.write(final_string)
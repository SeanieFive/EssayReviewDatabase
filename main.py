from flask import Flask, render_template, request, redirect
import pandas as pd
import os
from datetime import datetime
import webbrowser

app = Flask(__name__)

# Path to save the CSV file
csv_file_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'student_data.csv')

# Define the payout table
payout_table = {
    'Personal Statement': {'Draft 1': 25.00, 'Draft 2': 14.75, 'Draft 3+': 11.25},
    'UC PIQ': {'Draft 1': 18.00, 'Draft 2': 10.50, 'Draft 3+': 8.00},
    '50-300 words': {'Draft 1': 12.50, 'Draft 2': 7.50, 'Draft 3+': 5.75},
    '301-600 words': {'Draft 1': 21.00, 'Draft 2': 12.50, 'Draft 3+': 9.45},
    '601-750 words': {'Draft 1': 26.50, 'Draft 2': 15.75, 'Draft 3+': 12.00},
    'Activities Review': {'Draft 1': 40.00, 'Draft 2': 23.50, 'Draft 3+': 18.00}
}


def calculate_payout(essay_type, draft_number, status):
    """Calculate payout based on essay type, draft number, and status."""
    return payout_table.get(essay_type, {}).get(draft_number, 0) if status == 'Invoice' else 0


def format_date(date_string):
    """Convert from 'YYYY-MM-DD' to 'MM/DD/YYYY'."""
    return datetime.strptime(date_string, '%Y-%m-%d').strftime('%m/%d/%Y')


def save_to_csv(data, index=None):
    """Save data to a CSV file. Update existing row if index is provided, otherwise append."""
    df = pd.DataFrame([data])
    df['Date'] = df['Date'].apply(format_date)

    if os.path.exists(csv_file_path):
        existing_df = pd.read_csv(csv_file_path)
        if index is not None:
            existing_df.loc[index] = df.iloc[0]
        else:
            existing_df = pd.concat([existing_df, df], ignore_index=True)
        existing_df.to_csv(csv_file_path, index=False)
    else:
        df.to_csv(csv_file_path, index=False)


def load_data_from_csv():
    """Load data from the CSV file."""
    return pd.read_csv(csv_file_path).to_dict(orient='records') if os.path.exists(csv_file_path) else []


@app.route('/')
def index():
    """Render the index page with data from the CSV file."""
    data = load_data_from_csv()
    return render_template('index.html', data=data, enumerate=enumerate)


@app.route('/submit', methods=['POST'])
def submit():
    """Handle form submission and save data to the CSV file."""
    row_index = request.form.get('row_index')
    date = request.form['date']
    student_name = request.form['student_name']
    essay_type = request.form['essay_type']
    draft_number = request.form['draft_number']
    status = request.form['status']
    comments = request.form['comments']

    data = {
        'Date': date,
        'Student Name': student_name,
        'Essay Type': essay_type,
        'Draft Number': draft_number,
        'Status': status,
        'Comments': comments,
        'Payout': calculate_payout(essay_type, draft_number, status),
        'Edited': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    if row_index:
        df_existing = pd.read_csv(csv_file_path)
        if 0 <= int(row_index) < len(df_existing):
            data['Added'] = df_existing.at[int(row_index), 'Added']
            save_to_csv(data, index=int(row_index))
    else:
        data['Added'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['Edited'] = ''
        save_to_csv(data)

    return redirect('/')


if __name__ == '__main__':
    # Open the default web browser with the Flask app address
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(debug=True)

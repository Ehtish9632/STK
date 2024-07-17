from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from io import BytesIO

app = Flask(__name__)

# Directory for temporary files
TEMP_DIR = 'data/temp'
os.makedirs(TEMP_DIR, exist_ok=True)

# Function to generate test cases based on common web elements
def generate_test_cases(num_tests, url):
    test_cases = []
    for i in range(1, num_tests + 1):
        if i == 1:
            test_cases.append({
                'Test Case ID': f'TC{i}',
                'Description': f'Check if search input field exists on {url}',
                'Element Selector': 'input[type="text"], input[name="q"]',  # Common input field selectors
                'Action': 'verify_visibility',
                'Input Data': '',
                'Expected Result': 'Visible'
            })
        elif i == 2:
            test_cases.append({
                'Test Case ID': f'TC{i}',
                'Description': f'Check if search button exists on {url}',
                'Element Selector': 'button[type="submit"], button[name="search"]',  # Common button selectors
                'Action': 'verify_visibility',
                'Input Data': '',
                'Expected Result': 'Visible'
            })
        elif i == 3:
            test_cases.append({
                'Test Case ID': f'TC{i}',
                'Description': f'Perform a search action on {url}',
                'Element Selector': 'input[name="q"]',  # Example input field
                'Action': 'input',
                'Input Data': 'Selenium',
                'Expected Result': 'Search results are displayed.'
            })
        elif i == 4:
            test_cases.append({
                'Test Case ID': f'TC{i}',
                'Description': f'Click on the first link on {url}',
                'Element Selector': 'a[href]',  # Example link selector
                'Action': 'click',
                'Input Data': '',
                'Expected Result': 'Page navigates to the link.'
            })
        else:
            # Add more test cases or adjust as needed
            test_cases.append({
                'Test Case ID': f'TC{i}',
                'Description': f'Test Case {i} for {url}',
                'Element Selector': 'body',  # Placeholder for additional test cases
                'Action': 'verify_visibility',
                'Input Data': '',
                'Expected Result': 'Visible'
            })
    return test_cases

# Generate and save input Excel file
def save_input_excel(test_cases):
    input_file = os.path.join(TEMP_DIR, 'ui_ux_test_cases.xlsx')
    df = pd.DataFrame(test_cases)
    df.to_excel(input_file, index=False)
    return input_file

# Function to perform tests
def perform_tests(input_file, url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    results = []
    
    df = pd.read_excel(input_file)
    for index, row in df.iterrows():
        case = row.to_dict()
        driver.get(url)
        
        try:
            if case['Action'] == 'input':
                element = driver.find_element(By.CSS_SELECTOR, case['Element Selector'])
                element.send_keys(case['Input Data'])
                case['Actual Result'] = 'Input Successful'
                case['Status'] = 'Pass'
            elif case['Action'] == 'click':
                element = driver.find_element(By.CSS_SELECTOR, case['Element Selector'])
                element.click()
                case['Actual Result'] = 'Clicked'
                case['Status'] = 'Pass'
            elif case['Action'] == 'verify_text':
                element = driver.find_element(By.CSS_SELECTOR, case['Element Selector'])
                actual_text = element.text
                case['Actual Result'] = actual_text
                case['Status'] = 'Pass' if actual_text == case['Expected Result'] else 'Fail'
            elif case['Action'] == 'verify_visibility':
                element = driver.find_element(By.CSS_SELECTOR, case['Element Selector'])
                is_visible = element.is_displayed()
                case['Actual Result'] = 'Visible' if is_visible else 'Not Visible'
                case['Status'] = 'Pass' if is_visible == (case['Expected Result'].lower() == 'visible') else 'Fail'
            else:
                case['Actual Result'] = 'Action not implemented'
                case['Status'] = 'Fail'
        except Exception as e:
            case['Actual Result'] = str(e)
            case['Status'] = 'Fail'
        results.append(case)
    
    driver.quit()
    
    output_file = os.path.join(TEMP_DIR, 'ui_ux_test_results.xlsx')
    results_df = pd.DataFrame(results)
    results_df.to_excel(output_file, index=False)
    
    return output_file, results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    url = request.form['url']
    num_tests = int(request.form['num_tests'])
    
    test_cases = generate_test_cases(num_tests, url)
    input_file = save_input_excel(test_cases)
    
    return render_template('index.html', input_file=input_file, url=url)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    url = request.form['url']
    if file:
        input_file = os.path.join(TEMP_DIR, 'uploaded_test_cases.xlsx')
        file.save(input_file)
        output_file, results = perform_tests(input_file, url)
        
        # Render results in HTML
        return render_template('results.html', results=results, output_file=output_file)

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(TEMP_DIR, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

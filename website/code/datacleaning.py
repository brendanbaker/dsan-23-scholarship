# datacleaning.py
# @Brendan Baker

# The first step is to get the data into a usable format. 
# We have two folders, named DC and USA.  Each contains a number of JSON files
# The goal is to read the JSON files and create a single pandas dataframe per folder

import pandas as pd
import json
import re
import os 

def format_nested(data, key, colname, valname):
    '''
    Special function to format the nested job highlights data
    '''
    # Creating a list to store the dictionaries
    jobs_data = []

    # Iterate through each job in the data
    for job in data:
        # Get the job_highlights for the current job
        job_highlights = job[key]
        
        # Create a dictionary to store the highlights for the current job
        job_dict = {}
        
        # Iterate through the job_highlights and add them to the job_dict
        for highlight in job_highlights:
            
            # If title is not in the column names, skip
            if colname not in highlight:
                continue
            
            # Get the column name from the 'title' key
            column_name = highlight[colname]
            
            # Get the values from the 'items' key
            values = highlight[valname]
            
            # Add the values to the job_dict under the column name
            job_dict[column_name] = values
        
        # Append the job_dict to the jobs_data list
        jobs_data.append(job_dict)

    # Create a DataFrame using the jobs_data list
    df = pd.DataFrame(jobs_data)
    
    return(df)


def read_json_files(path, tag):
    json_files = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')] # Get all the json files in the folder
    df = pd.DataFrame()
    for index, js in enumerate(json_files):
        with open(os.path.join(path, js)) as json_file:
            json_text = json.load(json_file)
            if 'jobs_results' in json_text:
                temp_df = pd.DataFrame(json_text['jobs_results'])
                temp_text = json_text['jobs_results']
                
                # Expand job_highlights column
                if 'job_highlights' in temp_df:
                    job_highlights_df = format_nested(temp_text, 'job_highlights', 'title', 'items')
                    temp_df = pd.concat([temp_df, job_highlights_df], axis=1).drop(['job_highlights'], axis=1)
                
                # Expand related_links column
                if 'related_links' in temp_df:
                    related_links_df = pd.json_normalize(temp_df['related_links'])
                    related_links_df.columns = ['related_link_'+str(col) for col in related_links_df.columns]
                    temp_df = pd.concat([temp_df, related_links_df], axis=1).drop(['related_links'], axis=1)
                
                # Expand detected_extensions column
                if 'detected_extensions' in temp_df:
                    detected_extensions_df = pd.json_normalize(temp_df['detected_extensions'])
                    detected_extensions_df.columns = ['detected_extension_'+str(col) for col in detected_extensions_df.columns]
                    temp_df = pd.concat([temp_df, detected_extensions_df], axis=1).drop(['detected_extensions'], axis=1)
                
                # Strip extension from file name, then replace dashes with spaces, then remove any numbers
                temp_df['category'] = re.sub(r'\d+', '', re.sub(r'-', ' ', js.split('.')[0]))
                
                df = pd.concat([df, temp_df])
                
                
                
                # Add the tag to the dataframe
                df['tag'] = tag
                
            else:
                print(f"Skipping file {js}: 'jobs_results' key not found")
    return df


out1 = read_json_files('../data/DC/', "DC")
out2 = read_json_files('../data/USA/', "USA")

agg = pd.concat([out1, out2])

# Remove duplicate rows based on job_id
agg = agg.drop_duplicates(subset=['job_id'])

# Remove the beginning whitespace from the location column
agg['location'] = agg['location'].str.strip()

# Remove trailing whitespace from the category column
agg['category'] = agg['category'].str.strip()

# Combine time series and time series analysis into one category
agg['category'] = agg['category'].replace('time series analysis', 'time series')

# Write to CSV
agg.to_csv('./data/jobs.csv', index=False)

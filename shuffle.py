import pandas as pd
import numpy as np

# Read the CSV file
file_path = "sample honeywords.csv"
df = pd.read_csv(file_path)

# Initialize a new column to store the location of the true password
df['index'] = np.nan  # Add a new column named 'index' in the DataFrame

# Define a function to shuffle the true password and honeywords for each row
def shuffle_honeywords(row):
    # Get the honeywords and true password columns
    honeywords = row.iloc[5:26].values.tolist()  # Use .iloc for position-based indexing
    true_password = row.iloc[5]  # Use .iloc to get the true password

    # Add the true password to the honeywords list
    honeywords.append(true_password)

    # Shuffle the list
    np.random.shuffle(honeywords)

    # Find the new position of the true password
    true_password_index = honeywords.index(true_password)

    # Write the shuffled honeywords back to the original DataFrame
    row.iloc[5:26] = honeywords[:-1]

    # Return the new position (index)
    row['index'] = true_password_index + 1  # Use the column name 'index' instead of position
    return row

# Apply the shuffle function
df = df.apply(shuffle_honeywords, axis=1)

# Save the modified file
output_file_path = "shuffled_honeywords.csv"
df.to_csv(output_file_path, index=False)

print("Shuffling completed and saved to:", output_file_path)

"""
# Extract all true passwords and honeywords
all_honeywords = []
user_indices = []

# Cleaning function: Remove all spaces and invisible characters to ensure no issues
def clean_string(s):
    # Remove all invisible characters (including extra spaces, newlines, etc.) and convert to lowercase
    return ''.join(s.split()).strip().lower()

# Iterate over each row, extracting the true password and 20 honeywords
for i, row in df.iterrows():
    honeywords = row.iloc[5:26].values.tolist()  # Get the 20 honeywords for each row
    true_password = row.iloc[5]  # Get the true password
    honeywords.append(true_password)  # Add the true password to the honeywords list
    all_honeywords.extend(honeywords)  # Add the current user's honeywords to the global list
    user_indices.append((i, true_password))  # Record the user index and the original true password

# Shuffle all honeywords globally
np.random.shuffle(all_honeywords)

# Reassign the globally shuffled honeywords back to the original DataFrame
honeywords_per_user = 21  # Each user has 21 items (1 true password + 20 honeywords)

# Iterate and fill the new data
for i, row in df.iterrows():
    # Extract the user's new honeywords
    shuffled_honeywords = all_honeywords[i * honeywords_per_user:(i + 1) * honeywords_per_user]

    # Clean the true password and honeywords: remove spaces, newlines and convert to lowercase
    # (You can complete the cleaning process here if needed)
    # Example: shuffled_honeywords = [clean_string(h) for h in shuffled_honeywords]
"""
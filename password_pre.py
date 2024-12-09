import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# LSH hash function definition
class LSH:
    def __init__(self, num_hashes, input_dim, seed=42):
        self.num_hashes = num_hashes
        self.input_dim = input_dim
        np.random.seed(seed)
        self.hash_funcs = [self._generate_random_hash(self.input_dim) for _ in range(num_hashes)]

    def _generate_random_hash(self, input_dim):
        return np.random.randn(input_dim)

    def hash_password(self, password):
        return [1 if np.dot(self.hash_funcs[i], password) > 0 else 0 for i in range(self.num_hashes)]

# Preprocess and store hash values
def preprocess_hashes(csv_file, output_file, num_hashes=10, seed=42):
    # Read the CSV file, extracting only the 'Password' column
    try:
        df = pd.read_csv(csv_file, usecols=['Password'])
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")

    # Initialize the list to store hash results
    hashed_results = []

    # Process each password
    for pwd in df['Password']:
        process_password(pwd, hashed_results, num_hashes, seed)

    # Store hash results
    pd.DataFrame(hashed_results, columns=['Password', 'Hash']).to_csv(output_file, index=False)
    print(f"Hash results have been saved to {output_file}")

def process_password(pwd, hashed_results, num_hashes, seed):
    """Process each password and compute its hash"""
    pwd = str(pwd).strip()  # Ensure it's a string and remove extra whitespace
    if len(pwd) == 0:
        return  # Skip empty passwords

    try:
        # Initialize CountVectorizer
        vectorizer = CountVectorizer(analyzer='char', ngram_range=(1, 3), max_features=15, stop_words=None)
        lsh = LSH(num_hashes=num_hashes, input_dim=15, seed=seed)

        vector = vectorizer.fit_transform([pwd]).toarray()[0]
        if len(vector) < lsh.input_dim:
            vector = np.pad(vector, (0, lsh.input_dim - len(vector)), 'constant')
        elif len(vector) > lsh.input_dim:
            vector = vector[:lsh.input_dim]

        hashed_password = lsh.hash_password(vector)
        hashed_results.append((pwd, hashed_password))

    except Exception as e:
        print(f"Error processing password {pwd}: {e}")

# Example usage
if __name__ == "__main__":
    #preprocess_hashes('cleaned_merged_passwords（for official experiment）.csv', 'hashed_passwords.csv')
    preprocess_hashes('sample dataset.csv', 'sample dataset_hash.csv')

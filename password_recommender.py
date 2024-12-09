import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from Levenshtein import distance as levenshtein_distance
import ast

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

    def hamming_distance(self, hash1, hash2):
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

    def get_candidates_from_hashes(self, target_hash, hash_data, max_hamming_dist=2):
        candidates = []
        for index, row in hash_data.iterrows():
            stored_hash = row['Hash']
            hamming_dist = self.hamming_distance(stored_hash, target_hash)
            if hamming_dist <= max_hamming_dist:
                candidates.append(row['Password'])
        return candidates

# Calculate Levenshtein similarity (taking the inverse of the distance and normalizing to similarity)
def levenshtein_similarity(password1, password2):
    dist = levenshtein_distance(password1, password2)
    max_len = max(len(password1), len(password2))
    return 1 - dist / max_len if max_len > 0 else 0

# Calculate Jaccard similarity
def jaccard_similarity(password1, password2):
    set1 = set(password1)
    set2 = set(password2)
    return len(set1 & set2) / len(set1 | set2)

# Calculate N-gram similarity
def ngram_similarity(password1, password2, n=2):
    ngrams1 = set([password1[i:i + n] for i in range(len(password1) - n + 1)])
    ngrams2 = set([password2[i:i + n] for i in range(len(password2) - n + 1)])
    return len(ngrams1 & ngrams2) / len(ngrams1 | ngrams2)

# Calculate the final weighted similarity
def calculate_final_similarity(target_password, candidate_password, weights):
    s1 = levenshtein_similarity(target_password, candidate_password)
    s2 = jaccard_similarity(target_password, candidate_password)
    s3 = ngram_similarity(target_password, candidate_password)
    return weights[0] * s1 + weights[1] * s2 + weights[2] * s3

# Load stored hash results and query similar passwords
def recommend_similar_passwords_from_csv(target_password, csv_file, num_recommendations=5, num_hashes=10, seed=42, max_hamming_dist=2):
    try:
        hash_data = pd.read_csv(csv_file)
        hash_data['Hash'] = hash_data['Hash'].apply(lambda x: ast.literal_eval(x))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

    # Hash the target password
    vectorizer = CountVectorizer(analyzer='char', ngram_range=(1, 3), max_features=15)
    lsh = LSH(num_hashes=num_hashes, input_dim=15, seed=seed)

    target_vector = vectorizer.fit_transform([target_password]).toarray()[0]
    target_vector = np.pad(target_vector, (0, max(0, lsh.input_dim - len(target_vector))), 'constant')[:lsh.input_dim]
    target_hash = lsh.hash_password(target_vector)

    # Get candidate passwords
    candidates = lsh.get_candidates_from_hashes(target_hash, hash_data, max_hamming_dist=max_hamming_dist)
    if not candidates:
        print("No candidate passwords found")
        return []

    weights = [0.6, 0.2, 0.2]

    candidates_with_similarity = []
    seen_candidates = set()
    for candidate_pwd in candidates:
        if candidate_pwd == target_password or candidate_pwd in seen_candidates:
            continue
        final_similarity = calculate_final_similarity(target_password, candidate_pwd, weights)
        candidates_with_similarity.append((candidate_pwd, final_similarity))
        seen_candidates.add(candidate_pwd)

    candidates_with_similarity.sort(key=lambda x: x[1], reverse=True)
    return [c[0] for c in candidates_with_similarity[:num_recommendations]]

# Example usage
if __name__ == "__main__":
    target_pwd = 'password123'
    #csv_file = 'hashed_passwords.csv'
    csv_file = 'sample dataset_hash.csv'
    K = 5
    recommendations = recommend_similar_passwords_from_csv(target_pwd, csv_file, num_recommendations=K)
    print("Recommended passwords: ", recommendations)

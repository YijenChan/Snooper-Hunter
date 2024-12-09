from weak_generator import WeakPasswordGenerator  # Import the generator for weak passwords
from strong_generator import StrongPasswordGenerator
from pii_generator import PIIGenerator
from weakness_evaluation import evaluate_password_strength  # Import GPT API for weak password evaluation
import pandas as pd
import json


class HoneywordsMain:
    def __init__(self):
        # Initialize the various generators
        self.weak_password_generator = WeakPasswordGenerator("XYZ University")  # Initialize with a specific university name
        self.strong_password_generator = StrongPasswordGenerator("XYZ University")  # Pass the university name
        self.pii_generator = PIIGenerator("XYZ University")  # PII generation strategy

    def is_pii_record(self, record):
        """
        Check if the record contains PII information.
        """
        _, username, birthday, name, email = record
        return not (username == 'Nah' and birthday == 'Nah' and name == 'Nah' and email == 'Nah')

    def is_weak_password(self, password):
        """
        Use GPT to evaluate if the password is weak.
        """
        result = evaluate_password_strength(password)
        if result:
            return result["Tag"] == 1  # Tag 1 indicates a weak password
        return False  # If an error occurs, consider it a strong password by default

    def generate_honeywords(self, record):
        """
        Generate honeywords with explanations and labels in JSON format.
        record: (password, username, birthday, name, email)
        """
        password, username, birthday, name, email = record
        result = {
            "reason": "",
            "label": 0,
            "honeywords": []
        }

        # Check if the record contains PII information
        if self.is_pii_record(record):
            result["reason"] = "Record contains personal identifiable information (PII)"
            result["label"] = 3
            honeywords_result = self.pii_generator.generate(password, username, birthday, name, email)
            honeywords = honeywords_result.get('honeywords', []) if honeywords_result else []
            print("Generation strategy used: PII-based")
        elif self.is_weak_password(password):
            result["reason"] = "Password is weak, may follow common patterns"
            result["label"] = 1
            weak_password_result = self.weak_password_generator.generate(password)
            honeywords = weak_password_result.get('honeywords', []) if weak_password_result else []
            print("Generation strategy used: Weak password-based")
        else:
            result["reason"] = "Password is strong, meets security standards"
            result["label"] = 2
            strong_password_result = self.strong_password_generator.generate(password)
            honeywords = strong_password_result.get('honeywords', []) if strong_password_result else []
            print("Generation strategy used: Strong password-based")

        # Include the original password and ensure there are returned values
        result["honeywords"] = [password] + honeywords if honeywords else [password]
        return result


def process_csv(input_file, output_file):
    # Read CSV file
    df = pd.read_csv(input_file)

    # Iterate over each row to generate honeywords
    for index, row in df.iterrows():
        password = row['Password']
        username = row.get('Username', 'Nah')
        birthday = row.get('Birthday', 'Nah')
        name = row.get('Name', 'Nah')
        email = row.get('Email', 'Nah')

        # Reinitialize HoneywordsMain generator for each record
        generator = HoneywordsMain()
        # Generate honeywords
        record = (password, username, birthday, name, email)
        result = generator.generate_honeywords(record)

        # Extract honeywords and add to the columns starting from the 6th column
        honeywords = result.get("honeywords", [])
        for i, honeyword in enumerate(honeywords, start=1):
            col_name = f'Honeyword_{i}'
            df.at[index, col_name] = honeyword

        # Print log for the processed record
        print(
            f"Processed record {index + 1}: Password: {password}, Username: {username}, Birthday: {birthday}, Name: {name}, Email: {email}")

    # Save the result to a new CSV file
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Processing completed, results saved to {output_file}")


# Example usage 1
if __name__ == "__main__":
    input_file = 'sample_dataset.csv'  # Input file name
    output_file = 'sample_honeywords.csv'  # Output file name
    process_csv(input_file, output_file)


"""
# Example usage 2
if __name__ == "__main__":
    generator = HoneywordsMain()

    # Example records for testing
    target_record_with_pii = ("SsanCat3", "supercat", "1995/05/02", "ZhangSan", "hao123@example.com")
    target_record_weak_pwd = ("abc123xyz", "Nah", "Nah", "Nah", "Nah")
    target_record_strong_pwd = ("DavidLermajr.4894", "Nah", "Nah", "Nah", "Nah")

    # Generate and print results
    honeywords_result_pii = generator.generate_honeywords(target_record_with_pii)
    print("Result for record with PII:")
    print(json.dumps(honeywords_result_pii, indent=4, ensure_ascii=False))

    honeywords_result_weak = generator.generate_honeywords(target_record_weak_pwd)
    print("\nResult for weak password:")
    print(json.dumps(honeywords_result_weak, indent=4, ensure_ascii=False))

    honeywords_result_strong = generator.generate...
"""

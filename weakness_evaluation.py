import openai
import json

# Set API Key and custom API endpoint
openai.api_key = 'XXX'
openai.api_base = "XXX"  # your API endpoint


def evaluate_password_strength(password):
    """
    Call the ChatGPT API to evaluate the password strength and return the result in JSON format.
    """
    prompt = (f"Evaluate the password '{password}' for weakness. "
              f"Here are some recommended criteria: "
              "1) Weak if it contains fewer than 8 characters, 2) Weak if it only contains letters, "
              "3) Strong if it includes uppercase, lowercase, digits, and special characters. "
              "Apart from these criteria, you can evaluate on your own knowledge. Return the result in JSON format with two fields: 'Brief Reason' and 'Tag' (1 for weak, 2 for strong).")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a Cyberspace Security Expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0  # Set to 0 to reduce uncertainty
        )

        result = response['choices'][0]['message']['content'].strip()
        # Clean and parse JSON data
        if result.startswith("```json"):
            result = result.replace("```json", "").replace("```", "").strip()
        result_dict = json.loads(result)
        return result_dict

    except json.JSONDecodeError as e:
        print(f"Error parsing the JSON response from the LLM: {str(e)}")
        return None
    except Exception as e:
        print(f"Error calling the GPT API: {str(e)}")
        return None


# Example usage
if __name__ == "__main__":
    #password = "abc123xyz"
    password = "DavidLermajr.4894"
    #password = "Cyl6188872!"
    result = evaluate_password_strength(password)

    if result:
        print("GPT Password Evaluation Result:")
        print(json.dumps(result, indent=4))  # Pretty print the JSON result, each element on a new line

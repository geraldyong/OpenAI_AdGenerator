import os, random
from fastapi import HTTPException
from openai import OpenAI

# OpenAI API Key (ensure this is secured in a real-world app, like using environment variables)
client = OpenAI(
  api_key  = os.getenv('OPENAI_API_KEY')
)


# Function to read category areas and metadata keywords from a file
def read_category_areas(file_path: str) -> list[dict]:
  try:
    with open(file_path, "r") as file:
      return [
        {"keyword": line.split(",")[0].strip(), "area": line.split(",")[1].strip()}
          for line in file.readlines() if line.strip()
        ]
  except FileNotFoundError:
    raise HTTPException(status_code=500, detail="Category areas file not found.")
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error reading category areas: {str(e)}")


# Function to read customer segments from a file
def read_customer_segments(file_path: str) -> list[str]:
  try:
    with open(file_path, "r") as file:
      return [
        {"keyword": line.split(",")[0].strip(), "custseg": line.split(",")[1].strip()}
          for line in file.readlines() if line.strip()
        ]
  except FileNotFoundError:
    raise HTTPException(status_code=500, detail="CRITICAL: Customer segments file not found.")
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"CRITICAL: Error reading customer segments: {str(e)}")


# Randomly generate a prompt based on a category area and customer segment
def generate_random_prompt(cat_areas, cust_segs) -> tuple:
  category_area = random.choice(cat_areas)
  customer_segment = random.choice(cust_segs)
  prompt = f"Create an advertisement for {category_area['area']} targeting {customer_segment['custseg']}."
  return prompt, category_area['keyword'], customer_segment['keyword']


# Use OpenAI to generate advertisement text
def generate_ad_openai(prompt):
  return get_openai(prompt)


# Send a prompt to OpenAI and return the result.
def get_openai(prompt):
  response = client.chat.completions.create(
    messages = [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": prompt},
    ],
    model = "gpt-4-1106-preview"
  )

  # Extract generated ad text
  return response.choices[0].message.content.strip()


# Use OpenAI to extract metadata tags based on advertisement text
def get_metadata_from_ad_openai(ad_text: str, cat_areas, cust_segs) -> list[str]:
  prompt = (
    f"Here is an advertisement text: \"{ad_text}\".\n\n"
    "Here is a list of category areas:\n"
    f"{cat_areas}.\n\n"
    "Here is a list of customer segments:\n"
    f"{cust_segs}.\n\n"
    "Based on the advertisement text, determine the most relevant category areas\n"
    "and customer segments from the lists above.\n"
    "You can choose more than one category area and customer segment.\n"
    "Return the selected category areas and customer segments as a single comma separated list.\n"
    "Do not explain your steps.\n"
  )

  # Query OpenAI
  openai_response_text = get_openai(prompt)

  # OpenAI response structure for parsing purposes:
  try:
    metadata_tags = [tag.strip() for tag in openai_response_text.split(",")]
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"CRITICAL: Error parsing OpenAI response: {str(e)}")

  return metadata_tags


# Use OpenAI to generate a customer list of first and last names.
def generate_custnames_openai(num_cust: int) -> list[tuple[str, str]]:
  prompt = (
    f"Generate {num_cust} random names.\n"
    "For each name, separate the first and last name with a space.\n"
    "Put each name in a new line.\n"
    "List out the names. Do not explain your steps."
  )

  # Query OpenAI
  names_text = get_openai(prompt)

  # Split the names by line and then by comma to separate first and last names
  name_lines = names_text.split("\n")
  names = []
  for name_line in name_lines:
    #if " " in name_line:
    first_name, last_name = [part.strip() for part in name_line.split(" ")]
    names.append((first_name, last_name))

  return names
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load Helper Functions
from helper import *

# Initialize FastAPI app
app = FastAPI(
  title = "Advertisement Generator",
  description = "Using OpenAPI, generate sample advertisements based on certain areas and customer segments."
)

# Pydantic model for ad generation
class AdResponse(BaseModel):
  prompt: str
  ad_text: str
  metadata_tags: list[str]

# Pydantic model for metadata extraction request
class AdMetadataRequest(BaseModel):
  ad_text: str

# Pydantic model for metadata extraction response
class AdMetadataResponse(BaseModel):
  metadata_tags: list[str]

# Pydantic model for user generation
class CustList(BaseModel):
  first_name: str
  last_name: str
  category_areas: list[str]
  customer_segs: list[str]

# Pydantic model to capture number of users to generate
class CustReq(BaseModel):
  num_cust: int

# Load category areas and customer segments from the respective text files
category_areas_file = "category_areas.txt"
customer_segments_file = "customer_segments.txt"
category_areas = read_category_areas(category_areas_file)
customer_segments = read_customer_segments(customer_segments_file)


# Generating the ad and random prompt
@app.post("/generate_ad", response_model=AdResponse, 
          summary="Generate an advertisement.", tags=["Generate Ads"])
async def generate_ad():
  """
    Generates an advertisement by randomly selecting a topic area and a customer segment.
  """
  try:
    # Generate a random prompt
    prompt, metadata_keyword, customer_seg_keyword = generate_random_prompt(
      category_areas, customer_segments
    )

    # Generated ad with OpenAI
    ad_text = generate_ad_openai(prompt)

    # Use the keyword directly from the category area file as the metadata tag
    metadata_tags = [metadata_keyword, customer_seg_keyword]

    # Create the response object
    return AdResponse(prompt=prompt, ad_text=ad_text, metadata_tags=metadata_tags)

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"CRITICAL: Error generating advertisement: {str(e)}")
  

# Extracting metadata from the ad text
@app.post("/extract_metadata", response_model=AdMetadataResponse, 
          summary="Extract relevant metadata from an advertisement text.", tags=["Extract Metadata"])
async def extract_metadata(ad_request: AdMetadataRequest):
  """
    Given an advertisement text, read the advert and pick out relevant tags from a curated list of tags.
  """
  try:
    # Extract metadata (category area and customer segment) from ad text
    metadata_desc = get_metadata_from_ad_openai(
      ad_request.ad_text, 
      [item['area'] for item in category_areas],
      [item['custseg'] for item in customer_segments]
    )

    metadata_tags = []
    for catarea in category_areas:
      if catarea['area'] in metadata_desc:
        metadata_tags.append(catarea['keyword'])
    for custseg in customer_segments:
      if custseg['custseg'] in metadata_desc:
        metadata_tags.append(custseg['keyword'])

    # Create and return the response, after converting the tags into a set and list
    # (to remove duplicates via set conversion)
    return AdMetadataResponse(metadata_tags=list(set(metadata_tags)))

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"CRITICAL: Error extracting metadata: {str(e)}")


# Generating user list and perferences
@app.post("/generate_cust_list", response_model=list[CustList], 
          summary="Generate a customer list with their profile and interests.", tags=["Generate Customer List"])
async def generate_cust(cust_request: CustReq):
  """
    Generates a list of users and their applicable category areas and customer segments.
  """
  try:
    # Generate the names for the requested number of users by calling OpeNAI
    names = generate_custnames_openai(cust_request.num_cust)

    # Generate users with random category areas and customer segments
    customers = [generate_random_cust(first_name, last_name) for first_name, last_name in names]

    return customers

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error generating users: {str(e)}")
  

# Function to generate a random user with random category areas and customer segments
def generate_random_cust(first_name: str, last_name: str) -> CustList:
  # Select random number of category areas and customer segments
  random_category_areas = random.sample(category_areas, random.randint(1, len(category_areas)))
  random_customer_segments = random.sample(customer_segments, random.randint(1, len(customer_segments)))

  # Extract the keywords into a unique set of keywords, then converted into a list of strings.
  cat_areas_keywords = list({item['keyword'] for item in random_category_areas})
  cust_segs_keywords  = list({item['keyword'] for item in random_customer_segments})

  return CustList(
    first_name=first_name,
    last_name=last_name,
    category_areas=cat_areas_keywords,
    customer_segs=cust_segs_keywords
  )

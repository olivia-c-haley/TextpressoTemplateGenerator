import json
import streamlit as st
from openai import OpenAI


def make_json_query(user_query, textpresso_token, openai_token,
                    include_fulltext=False, include_all_sentences=False,
                    include_match_sentences=False, count=10):
    
    system_prompt = """
    You are a query reformatter that is knowledgeable of plant genetics. You take user input in string format, and reformat the entry into a JSON object.
    The JSON object is used to query Textpresso, which contains a corpus of plant genetics papers that users can query for specific traits, genes, etc. 

    The users may ask about crop traits (plant height, tassel number), gene regulatory elements (methylation, chromatin accessibility), etc. 
    
    You'll need to reformat their query, taking elements like keywords.  

    The contents of the JSON object are as follows: 
     token (string) : a valid access token to the Textpresso platform. 
     include_fulltext (boolean) : whether to return the fulltext and abstract of the documents. Default value is false.
     query (object) : the user query reformulated into a structured form. 
     include_all_sentences (boolean) : whether to return the text of all the sentences in the text. Default value is false. Restricted to specific tokens due to copyright.
     include_match_sentences (boolean) : whether to return the text of each matched sentence. Valid only for sentence searches. Default value is false
     since_num (int) : used for pagination. Skip the first results and return entries from the specified number. Note that the counter starts from 0 - i.e., the first document is number 0.
     count (int) : used for pagination. Return up to the specified number of results. Maximum value is 200

    In the query object, the following fields are possible. Note that the user may ask for multiple genes, traits, etc. so make sure to use AND and OR appropriately. 
    keywords (string) : (optional) the keywords to match in the text. Can contain logical operators AND and OR and grouping by round brackets
    exclude_keywords (string) : (optional) the keywords to exclude. Can contain logical operators AND and OR and grouping by round brackets
    year (string) : (optional) year of publication of the paper
    author (string) : (optional) the author(s) of the paper
    accession (string) : (optional) the accession of the paper
    journal (string) : (optional) the journal where the paper has been published
    paper_type (string) : (optional) the type of paper (e.g., research_article, review)
    exact_match_author (bool) : (optional) apply exact match on the author field
    exact_match_journal (bool) : (optional) apply exact match on the journal field
    categories_and_ed (bool) : (optional) use AND logical operator between the provided categories
    type (string) : the type of search to perform. Accepted values are: document to query the fulltext of documents and sentence to search in each sentence separately. Default value is document
    case_sensitive (boolean) : whether to perform a case sensitive search. Default value is false
    sort_by_year (boolean) : whether the results have to be sorted by publication date. Default value is false 

    Rules for keyword conversion:
      1. The species name (e.g., maize) should always be included with AND.
      2. All main concepts in the query should be connected with AND, unless the user explicitly mentions alternatives (like "or").
      3. Remove filler words ("the", "of", "in", etc.).
      4. Use parentheses to group related concepts for clarity.
      
    A valid output format is below: 
    {
      "token": "<ACCESS_TOKEN>",
      "query": {
          "keywords": "<user query reformulated into structured form>"
      },
      "include_fulltext": false,
      "include_all_sentences": false,
      "include_match_sentences": false,
      "since_num": 0,
      "count": 10
    }
    """

    # Initialize OpenAI client with the *user-provided* key
    client = OpenAI(api_key=openai_token)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )

    output_json = json.loads(response.choices[0].message.content)

    # Inject the correct values
    output_json["token"] = textpresso_token
    output_json["include_fulltext"] = include_fulltext
    output_json["include_all_sentences"] = include_all_sentences
    output_json["include_match_sentences"] = include_match_sentences
    output_json["count"] = count

    return output_json


# --- Streamlit UI ---
st.title("Query → JSON Reformatter")

# Input: user query
user_query = st.text_area("Enter your query:", "")

# Input: token
textpresso_token = st.text_input("Enter Textpresso access token:", type="password")
openai_token = st.text_input("Enter OpenAI access token:", type="password")

include_fulltext = st.checkbox("Include full text?", value=False)
include_all_sentences = st.checkbox("Include all sentences?", value=False)
include_match_sentences = st.checkbox("Include match sentences?", value=False)

# Number of results
count = st.number_input("Count", min_value=1, max_value=200, value=10)

if st.button("Generate JSON"):
    if user_query.strip() and openai_token.strip():
        result = make_json_query(user_query, textpresso_token, openai_token, count)
        st.json(result)   # Pretty JSON display
    else:
        st.warning("Please enter both a query and an access token.")

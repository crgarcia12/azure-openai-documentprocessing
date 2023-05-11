from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
# Set up the search client
search_url = os.environ["SEARCH_URL"]
index_name = os.environ["INDEX_NAME"]
admin_key = os.environ["ADMIN_KEY"]
credential = AzureKeyCredential(admin_key)
client = SearchClient(endpoint=search_url, index_name=index_name, credential=credential)

# Define the query function
def run_query(query):
    results = client.search(search_text=query)
    return results.get_results()

# Define the Streamlit app
def app():
    st.title("Azure Cognitive Search Query")
    query = st.text_input("Enter your query here:")
    if st.button("Search"):
        results = client.search(search_text=query)
        
        for result in results:
            st.write(result)

        st.write("Total number of documents found: {}\n".format(results.get_count()))

if __name__ == "__main__":
    app()

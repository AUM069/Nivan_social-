import streamlit as st
import json
import requests
from typing import Optional
import warnings
import pandas as pd
import re

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow is required. Please install it to use file upload functionality.")
    upload_file = None

# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "1b62669e-a172-4ece-8ad1-29334cfb2969"
FLOW_ID = "5dcd5e99-e53e-4e16-8c25-2e22e12db12e"
APPLICATION_TOKEN = "AstraCS:yndrsSOMtiCtHZmEzovAlGFa:d20ca989d241cf8edce9ac31b544a481c1fc6982b6a32b24705065faaa346ab6"

# Default tweaks from your code
DEFAULT_TWEAKS = {
    "ChatInput-zj2hP": {},
    "ParseData-taNai": {},
    "Prompt-6xBTw": {},
    "SplitText-iVesf": {},
    "ChatOutput-qjdEU": {},
    "AstraDB-T9TkM": {},
    "AstraDB-mE2N5": {},
    "File-htp6T": {},
    "MistalAIEmbeddings-gJ9co": {},
    "MistalAIEmbeddings-AP8Kv": {},
    "GroqModel-A6m0a": {}
}

def extract_tables_from_markdown(text):
    """Extract markdown tables and convert them to DataFrames."""
    sections = re.split(r'\*\*(.*?)\*\*', text)
    tables = {}

    current_section = None
    for i, section in enumerate(sections):
        if i % 2 == 0:  # Even indices contain the content
            if current_section and '|' in section:
                # Extract table content
                table_lines = [line.strip() for line in section.split('\n') if '|' in line]
                if table_lines:
                    # Parse headers
                    headers = [col.strip() for col in table_lines[0].split('|')[1:-1]]
                    # Skip the separator line
                    data = []
                    for line in table_lines[2:]:
                        row = [cell.strip() for cell in line.split('|')[1:-1]]
                        data.append(row)

                    # Create DataFrame
                    df = pd.DataFrame(data, columns=headers)
                    tables[current_section] = df
        else:  # Odd indices contain the section titles
            current_section = section.strip()

    return tables

def format_response(response_text):
    """Format the response with proper styling and tables."""
    try:
        # Extract tables from markdown
        tables = extract_tables_from_markdown(response_text)

        # Display each section with proper formatting
        sections = re.split(r'\*\*(.*?)\*\*', response_text)
        formatted_content = []

        current_section = None
        for i, section in enumerate(sections):
            if i % 2 == 0:  # Content
                if current_section and current_section in tables:
                    # Display table with Streamlit
                    st.subheader(current_section)
                    st.dataframe(
                        tables[current_section],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    # Display regular text content
                    cleaned_text = section.strip()
                    if cleaned_text:
                        st.markdown(cleaned_text)
            else:  # Section title
                current_section = section.strip()
                if not any(table_marker in section.lower() for table_marker in
                           ['data', 'metrics', 'types', 'results', 'calculations']):
                    st.markdown(f"**{section}**")

    except Exception as e:
        st.error(f"Error formatting response: {str(e)}")
        st.markdown(response_text)

def run_flow(
        message: str,
        tweaks: Optional[dict] = None
) -> dict:
    """Run a flow with a given message and optional tweaks."""
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{FLOW_ID}"

    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }

    if tweaks:
        payload["tweaks"] = tweaks

    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Error connecting to API: {str(e)}")

def main():
    st.set_page_config(page_title="Langflow RAG Interface", page_icon="🤖", layout="wide")

    # Title and description
    st.title(" Nivan ")
    st.markdown("lets talk about social media analytics .")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                format_response(message["content"])
            else:
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process the message
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = run_flow(
                        message=prompt,
                        tweaks=DEFAULT_TWEAKS
                    )

                    if isinstance(response, dict):
                        if "result" in response:
                            response_text = response["result"]
                        elif "outputs" in response and response["outputs"]:
                            response_text = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                        else:
                            response_text = json.dumps(response, indent=2)
                    else:
                        response_text = str(response)

                    format_response(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()


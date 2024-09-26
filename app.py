import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime


def fetch_arxiv_papers(topic: str, max_results: int = 3):
    """Fetch research papers from arXiv based on the given topic."""
    base_url = "http://export.arxiv.org/api/query?"
    query = f"search_query=all:{topic}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
    response = requests.get(base_url + query)

    if response.status_code != 200:
        st.error("Failed to fetch papers from arXiv. Please try again later.")
        return []

    root = ET.fromstring(response.content)
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
        authors = ", ".join([author.find('{http://www.w3.org/2005/Atom}name').text for author in
                             entry.findall('{http://www.w3.org/2005/Atom}author')])
        published = entry.find('{http://www.w3.org/2005/Atom}published').text
        link = entry.find('{http://www.w3.org/2005/Atom}id').text
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()

        papers.append({
            "title": title,
            "authors": authors,
            "year": datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ").year,
            "url": link,
            "summary": summary
        })

    return papers


def main():
    st.title("Research Paper Finder")
    st.write("Enter a topic to find genuine research papers from arXiv.")

    topic = st.text_input("Enter your research topic:")

    if st.button("Search"):
        if topic:
            with st.spinner("Searching for papers..."):
                papers = fetch_arxiv_papers(topic)

            if papers:
                st.subheader(f"Top Research Papers on '{topic}' :")
                for i, paper in enumerate(papers, 1):
                    with st.expander(f"{i}. {paper['title']} ({paper['year']})"):
                        st.write(f"**Authors:** {paper['authors']}")
                        st.write(f"**Year:** {paper['year']}")
                        st.write(f"**Summary:** {paper['summary']}")
                        st.markdown(f"[Read Paper]({paper['url']})")
            else:
                st.info("No papers found for the given topic. Try a different search term.")
        else:
            st.warning("Please enter a topic to search.")


if __name__ == "__main__":
    main()


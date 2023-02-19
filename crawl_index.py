from scholarly import scholarly
from es_gpt import ESGPT


def get_text_from_paper(x):
    title = x['bib'].get('title', '')
    abstract = x['bib'].get('abstract', '')
    return title + " " + abstract


# Create an instance of the ESGPT class
esgpt = ESGPT(index_name="papers")

# Search for papers by author ID, Sung Kim
author = scholarly.search_author_id("JE_m2UgAAAAJ")
papers = scholarly.fill(author, sections=['publications'])
# Index each paper in Elasticsearch
for paper in papers['publications']:
    print(paper)
    paper = scholarly.fill(paper, sections=[])
    paper_dict = paper['bib']
    id = paper['author_pub_id']

    # Index the paper in Elasticsearch
    text = get_text_from_paper(paper)
    esgpt.index(doc_id=id, doc=paper_dict, text=text)

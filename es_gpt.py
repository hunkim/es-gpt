import os
import json
import requests
import re
import pandas as pd

from elasticsearch import Elasticsearch

import tiktoken
import openai
from openai.embeddings_utils import distances_from_embeddings


ES_URL = os.environ["ES_URL"]
ES_USER = os.environ["ES_USER"]
ES_PASS = os.environ["ES_PASS"]
ES_CA_CERT = os.environ["ES_CA_CERT"]


class ESGPT:
    def __init__(self, index_name):
        self.es = Elasticsearch(ES_URL, http_auth=(ES_USER, ES_PASS),
                                ca_certs=ES_CA_CERT, verify_certs=True)
        self.index_name = index_name

        # FIXME: remove .strip()
        self.model_engine = os.environ["OPENAI_GPT_ENGINE"].strip()
        self.model_max_tokens = int(os.environ["OPENAI_GPT_MAX_TOKENS"])
        self.api_key = os.environ["OPENAI_API_KEY"]
        openai.api_key = self.api_key
        self.max_tokens = 1000

        # Load the cl100k_base tokenizer which is designed to work with the ada-002 model
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def index(self, doc_id, doc, text):
        doc["embeddings_dict_list"] = self._create_emb_dict_list(text)
        self.es.index(index=self.index_name,
                      id=doc_id,
                      document=doc)

    def search(self, query):
        es_query = {
            "query_string": {"query": query}
        }

        results = self.es.search(index=self.index_name, query=es_query)
        return results['hits']['hits']

    def _paper_results_to_text(self, results):
        text_result = ""
        for paper in results:
            title = paper["_source"].get("title", "")
            abstract = paper["_source"].get("abstract", "")
            paper_str = f"{title}:\n{abstract}\n\n"
            text_result += paper_str
        return text_result

    # Code from https://github.com/openai/openai-cookbook/blob/main/apps/web-crawl-q-and-a/web-qa.py
    # Function to split the text into chunks of a maximum number of tokens
    def _split_into_many(self, text):

        # Split the text into sentences
        sentences = text.split('. ')

        # Get the number of tokens for each sentence
        n_tokens = [len(self.tokenizer.encode(" " + sentence))
                    for sentence in sentences]

        chunks = []
        tokens_so_far = 0
        chunk = []

        # Loop through the sentences and tokens joined together in a tuple
        for sentence, token in zip(sentences, n_tokens):
            # If the number of tokens so far plus the number of tokens in the current sentence is greater
            # than the max number of tokens, then add the chunk to the list of chunks and reset
            # the chunk and tokens so far
            if tokens_so_far + token > self.max_tokens:
                chunks.append(". ".join(chunk) + ".")
                chunk = []
                tokens_so_far = 0

            # If the number of tokens in the current sentence is greater than the max number of
            # tokens, go to the next sentence
            if token > self.max_tokens:
                continue

            # Otherwise, add the sentence to the chunk and add the number of tokens to the total
            chunk.append(sentence)
            tokens_so_far += token + 1

        # Add the last chunk to the list of chunks
        if chunk:
            chunks.append(". ".join(chunk) + ".")

        return chunks

    def _create_emb_dict_list(self, long_text):
        shortened = self._split_into_many(long_text)

        embeddings_dict_list = []

        for text in shortened:
            n_tokens = len(self.tokenizer.encode(text))
            embeddings = openai.Embedding.create(
                input=text,
                engine='text-embedding-ada-002')['data'][0]['embedding']
            embeddings_dict = {}
            embeddings_dict["text"] = text
            embeddings_dict["n_tokens"] = n_tokens
            embeddings_dict["embeddings"] = embeddings
            embeddings_dict_list.append(embeddings_dict)

        return embeddings_dict_list

    def _create_context(self, question, df):
        """
        Create a context for a question by finding the most similar context from the dataframe
        """

        # Get the embeddings for the question
        q_embeddings = openai.Embedding.create(
            input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

        # Get the distances from the embeddings
        df['distances'] = distances_from_embeddings(
            q_embeddings, df['embeddings'].values, distance_metric='cosine')

        returns = []
        cur_len = 0

        # Sort by distance and add the text to the context until the context is too long
        for i, row in df.sort_values('distances', ascending=True).iterrows():

            # Add the length of the text to the current length
            cur_len += row['n_tokens'] + 4

            # If the context is too long, break
            if cur_len > self.max_tokens:
                break

            # Else add it to the text that is being returned
            returns.append(row["text"])

        # Return the context and the length of the context
        return "\n\n###\n\n".join(returns), cur_len

    def _gpt_api_call(self, query, input_token_len, context):
        body = {
            "model": self.model_engine,
            "prompt": f"Based on the context below\"\n\nContext: {context}\n\n---\n\nPlease provide concise answer for this questions: {query}",
            "max_tokens": self.model_max_tokens - input_token_len,
            "n": 1,
            "temperature": 0.5,
            "stream": True,
        }

        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {self.api_key}"}

        resp = requests.post("https://api.openai.com/v1/completions",
                             headers=headers,
                             data=json.dumps(body),
                             stream=True)
        return resp

    def gpt_answer(self, query, es_results=None, text_results=None):
        # Generate summaries for each search result
        if text_results:
            input_token_len = len(self.tokenizer.encode(text_results))
            if input_token_len < self.max_tokens:
                context = text_results
            else:
                emb_dict_list = self._create_emb_dict_list(text_results)
                df = pd.DataFrame(columns=["text", "n_tokens", "embeddings"])
                for emb_dict in emb_dict_list:
                    df = df.append(emb_dict, ignore_index=True)

                context, input_token_len = self._create_context(
                    question=query,
                    df=df)
        elif es_results:
            result_json_str = self._paper_results_to_text(es_results)
            if not result_json_str:
                result_json_str = "No results found"

            input_token_len = len(self.tokenizer.encode(result_json_str))
            if input_token_len < self.max_tokens:
                context = result_json_str
            else:
                # Create a pandas DataFrame from the list of embeddings dictionaries
                df = pd.DataFrame(columns=["text", "n_tokens", "embeddings"])

                # extract embeddings_dict from es_results and append to the dataframe
                for hit in es_results:
                    embeddings_dict_list = hit['_source']['embeddings_dict_list']
                    for embeddings_dict in embeddings_dict_list:
                        df = df.append(embeddings_dict, ignore_index=True)

                context, input_token_len = self._create_context(
                    question=query,
                    df=df)
        else:
            assert False, "Must provide either es_results or text_results"

        return self._gpt_api_call(query, input_token_len, context)


# Example usage
if __name__ == "__main__":
    esgpt = ESGPT("papers")
    query = "How to fix this bugs?"
    res = esgpt.search(query=query)
    res_str = esgpt._paper_results_to_text(res)

    # Pass ES results with precomputed embeddings
    res = esgpt.gpt_answer(query=query, es_results=res)
    print(res.text)

    # Pass text results and do embeddings on the fly
    # Note: This will be slower
    res = esgpt.gpt_answer(query=query, text_results=res_str)
    print(res.text)

import os
import openai
from sentence_transformers import SentenceTransformer


EMB_USE_OPENAI = os.getenv('EMB_USE_OPENAI', '0')


def _get_openai_embedding(input):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    return openai.Embedding.create(
        input=input, engine='text-embedding-ada-002')['data'][0]['embedding']


def _get_transformer_embedding(input):
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Sentences are encoded by calling model.encode()
    embedding = model.encode(input)
    return embedding


def get_embedding(input):
    if EMB_USE_OPENAI == '1':
        return _get_openai_embedding(input)
    else:
        return _get_transformer_embedding(input)


if __name__ == "__main__":
    print("Transformer: ", _get_transformer_embedding('hello world')[0])
    print("OpenAI: ", _get_openai_embedding('hello world'))

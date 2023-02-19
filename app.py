from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import json
from es_gpt import ESGPT

# Create an instance of the ESGPT class
es = ESGPT(index_name="papers")

# Create a FastAPI app
app = FastAPI()

# Define the search route


@app.get("/search")
async def search(q: str):
    # Perform a search for the query
    results = es.search(q)

    # Stream the search results to the client
    async def stream_response():
        for hit in results:
            yield "data: " + json.dumps(hit) + "\n\n"
        yield "[DONE]"

    return StreamingResponse(stream_response(), media_type="text/event-stream")

# Define the summary route


@app.post("/summary")
async def summary(Request: Request):

    payload = await Request.json()
    q = payload["q"]
    text_results = payload.get("text_results", "")

    if text_results:
        # Generate summaries of the search results
        resp = es.gpt_answer(q, text_results=text_results)
    else:
        es_results = es.search(q)
        resp = es.gpt_answer(q, es_results=es_results)

    if resp.status_code != 200:
        raise HTTPException(resp.status_code, resp.text)

    return StreamingResponse(resp.iter_content(1),
                             media_type="text/event-stream")
# Define the static files route
# Need to set html=True to serve index.html
# Need to put at the end of the routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Elasticsearch + GPT3 Answerer
This is a program that intercepts Elasticsearch results and sends them to GPT3 to provide reasonable answers, similar to Bing + ChatGPT. 

<img width="1650" alt="image" src="https://user-images.githubusercontent.com/901975/219938519-12c6d7af-2756-4e43-bf32-796ce7084a50.png">

It is designed to help users get more accurate and relevant answers to their queries, by leveraging the power of Elasticsearch and GPT3.

## Installation
To use this program, you will need to have access to both Elasticsearch and GPT3. You will also need to have Python installed on your system.

### All-in-one installation
To use the all-in-one installation, follow these steps:

Clone this repository to your local machine.
```bash
$ git clone 
```

Modify the .env with your Elasticsearch and GPT3 credentials and crawl_index.py file to index your documents.

Install the required dependencies by running the following command in your terminal:
```
$ make run
```

This will start the program and prompt you to enter a query. The program will then intercept the Elasticsearch results and send them to GPT3 to provide a reasonable answer. This method is very fast, as the program embeds the GPT3 answers during indexing.

### On-the-fly installation
To use the on-the-fly installation, follow these steps:

Add the following scripts to your search page. Specify the query, results, and gpt_answer output div IDs in your page:
```html
<script src="sse.js"></script>
<script src="es-gpt.js"></script>
<script>
window.addEventListener("load", function () {
    summarizeOnChange("query", "results", "gpt_answer");
});
</script>
```
Modify the .env with your Elasticsearch and GPT3 credentials and crawl_index.py file to index your documents.

Install the required dependencies by running the following command in your terminal:
```
$ make run
```

Run your search application and enter a query. The program will intercept the HTML results and send them to GPT3 to provide a reasonable answer. This method is convenient, but slower, as the program embeds the GPT3 answers on-the-fly.

## Contributing
We welcome contributions from the community! If you have ideas for how to improve the Elasticsearch + GPT3 Answerer, please open an issue or submit a pull request.

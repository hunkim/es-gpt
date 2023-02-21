# Elasticsearch + GPT3 Answerer
Want to turn your (elastic) search into something as hot as Bing + ChatGPT? Look no further than the Elasticsearch + GPT3 Answerer! Our program intercepts Elasticsearch results and sends them to GPT3 to provide accurate and relevant answers to your queries. Plus, it's just plain fun to use!

## Features
* ntercept Elasticsearch results and send them to GPT3 for more accurate answers
* Two installation options: all-in-one and on-the-fly
* Live demo available to see the program in action

<img width="1650" alt="image" src="https://user-images.githubusercontent.com/901975/219938519-12c6d7af-2756-4e43-bf32-796ce7084a50.png">

It is designed to help users get more accurate and relevant answers to their queries, by leveraging the power of Elasticsearch and GPT3.

## Live Demo
![ezgif-2-48b3807122](https://user-images.githubusercontent.com/901975/219939314-a8f8f63e-75f6-4805-a743-2b03ab410e0c.gif)

Check out our live demo at https://es-gpt.sung.devstage.ai/ to see the Elasticsearch + GPT3 Answerer in action! Please note that the site may be unstable and we are currently using the text-ada-001 model for proof of concept, so the GPT answer may be poor. However, this demo shows the concept of how the Elasticsearch + GPT3 Answerer works.

## How it works
See this diagram. 

<img width="1489" alt="image" src="https://user-images.githubusercontent.com/901975/219938678-7f0b5dc3-226f-41e0-a59f-247547d54b9c.png">

## Installation
To use the Elasticsearch + GPT3 Answerer, you'll need to have access to both Elasticsearch and GPT3, as well as Python installed on your system. We offer two installation options:

### All-in-one installation
To use the all-in-one installation, follow these steps:

Clone this repository to your local machine.
```bash
$ git clone https://github.com/hunkim/es-gpt.git
$ cd es-gpt
```

Modify the .env for your Elasticsearch and GPT3 credentials and crawl_index.py file to index your documents.
```bash
$make crawl
```

Then, this will run the backend server:
```bash
$ make run
```

Then, visit the backend server. The web page will then intercept the Elasticsearch results and send them to GPT3 to provide a reasonable answer. This method is very fast, as the program embeds documents during indexing.

### On-the-fly installation
To use the on-the-fly installation, follow these steps:

Add the following scripts to your search page. See `static/p.html`. Specify the query, results, and gpt_answer output div IDs in your original search page:
```html
<script src="sse.js"></script>
<script src="es-gpt.js"></script>
<script>
window.addEventListener("load", function () {
    summarizeOnChange("query", "results", "gpt_answer");
});
</script>
```
Modify the .env with your Elasticsearch and GPT3 credentials.
Install the required dependencies by running the following command in your terminal:
```
$ make run
```

Run your search web enter a query. The program will intercept the HTML results and send them to GPT3 to provide a reasonable answer. This method is convenient, but slower, as the program embeds the search results and query on-the-fly.

## Contributing
We welcome contributions from the community! If you have ideas for how to improve the Elasticsearch + GPT3 Answerer, please open an issue or submit a pull request. We love hearing from fellow search enthusiasts!

## License
This program is licensed under the MIT License

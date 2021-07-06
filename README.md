# Custom Entity Modules

## Create virtual environment

- This step is optional and is required in-case a virtual environment needs to be created
- Note: the modules have been tested on python 3.6

```bash
virtualenv -p /usr/bin/python3.6 <env_name> 
source path_to_<env_name>/bin/activate

pip install -U sentence-transformers
pip install dateparser
pip install textdistance
pip install stanza

OR
pip install -r requirements.txt
```


## Yes/No Entity module

- This semantic search is based on BERT sentence embedding i.e. a comparison of the input user query with the phrases present in the dataset (since this is BERT based, it takes time to load the model)

- Following this [link](https://github.com/UKPLab/sentence-transformers)

- Using the multilingual model : `distiluse-base-multilingual-cased`

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('distiluse-base-multilingual-cased')
```

Running instructions:
```bash
python get_yes_no.py --query="<query text>"
```


## Age entity module

- This module is built on top of the [dateparser library](https://github.com/scrapinghub/dateparser)

- This module essentially calculates the date from the user's response and then subtracts it (and takes the absolute value) to get the user age

```bash
python get_age.py --query="<query_text>"
```

## Number entity module

- This module is built on top of [Stanza](https://github.com/stanfordnlp/stanza) NLP library
- It uses PoS tags for Hindi language using the Stanza library

```bash
python get_number.py --query="<query_text>"
```
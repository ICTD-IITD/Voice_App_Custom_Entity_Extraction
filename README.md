# Custom Entity Modules

[Thesis link](https://drive.google.com/file/d/1Iqbk6gGcmyeDgbJYupHoMIFgOwvqdb1r/view)

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

## Name module
The name module is based on a 5 gram approach in which an SVM model predicts the probability of the center word (i.e. 3rd word from beginning) as the name of a person.

Environment setup for Name module:
```bash
source path_to_<env_name>/bin/activate
sudo apt install libpq-dev python3-dev
sudo apt-get install python-numpy libicu-dev
pip install pyicu
pip install polyglot
pip install pycld2
pip install Morfessor
polyglot download embeddings2.hi
polyglot download ner2.hi
cd Name/libsvm-3.23/
rm svm-scale svm-train svm-predict svm.o
make
cd python/
make
cd ../../../ (go back to home dir)
```

```bash
from Name import main
pred_name = main.get_name("<query_text>")
```

## Location module
- The README file for the location module is inside the location folder

## DoB module
- This module is a heuristic based DoB extraction approach. The heuristics were developed after manual analysis of how users spoke their date of birth.

```bash
python get_dob.py --query="<query_text>"
```

## Voice survey App
- The code and documentation for the voice survey app is inside the voice_survey_android_app folder


> The code for these modules is also present in a single Jupyter Notebook <em>finalEvalForPaper.ipynb</em>

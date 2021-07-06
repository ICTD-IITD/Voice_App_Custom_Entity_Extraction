"""
This script takes the user query as input and computes a
semantic search between the words in the Yes list and No
list to return if the user wanted to say 'Yes' or 'No' to the
question (or perhaps 'Maybe').

Reference : https://github.com/UKPLab/sentence-transformers/blob/master/examples/applications/semantic_search.py
"""
import argparse
import os
import sys
import torch

from sentence_transformers import SentenceTransformer, util

embedder = SentenceTransformer('distiluse-base-multilingual-cased')

def get_edit_distance_score():
    return

def get_semantic_score(query):
    """
        0 : No
        1 : Yes
        2 : Maybe
    """

    mapping_codes = {
        0:'No',
        1:'Yes'
    }

    # Corpus with example sentences
    corpus = {'हाँजी बिलकुल है': 1,
              'हाँजी': 1,
              'हाँ': 1,
              'हाँ घर में गर्वभती महिला है': 1,
              'नहीं': 0,
              'बिलकुल नहीं': 0,
              'नहीं घर में गर्वभती महिला नहीं है': 0,
              }

    corpus_questions = list(corpus.keys())
    corpus_embeddings = embedder.encode(corpus_questions, convert_to_tensor=True)

    # Find the closest 1 sentences of the corpus for query sentence based on cosine similarity
    top_k = 1       # NOTE: Provide as a command line argument
    query_embedding = embedder.encode(args.query, convert_to_tensor=True)
    cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    cos_scores = cos_scores.cpu()

    # Use torch.topk to find the highest 5 scores
    top_results = torch.topk(cos_scores, k=top_k)

    print("\n\n======================\n\n")
    print("Query:", query)
    # print("\nTop most similar sentences in corpus:")

    # for score, idx in zip(top_results[0], top_results[1]):
    #     print(corpus_questions[idx], "(Score: %.4f)" % (score))

    print("Final Answer : {}".format(mapping_codes[corpus[corpus_questions[top_results[1]]]]))

    return top_results[0]

def main(query):
    semantic_score = get_semantic_score(query)
    print("Semantic score : {}".format(semantic_score))
    # edit_distance_score = get_edit_distance_score()

    # avg_score = (semantic_score+edit_distance_score)/2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, help="User query",
        required=True)
    args = parser.parse_args()
    main(args.query)
    

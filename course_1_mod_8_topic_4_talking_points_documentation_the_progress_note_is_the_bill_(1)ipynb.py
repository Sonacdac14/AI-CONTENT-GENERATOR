# -*- coding: utf-8 -*-
"""Course 1 Mod 8 Topic 4 Talking Points Documentation the progress note is the bill (1)ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WmcTHdxXF41mR4SZ4thfe0FPinXO1vFH
"""

!mkdir elct

!cat /content/sonali/Course 2 Mod 2 Topic list and Reading list (2).docx

!pip install --upgrade pip
!pip install git+https://github.com/deepset-ai/haystack.git

import logging

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

from haystack.utils import clean_wiki_text, convert_files_to_docs, fetch_archive_from_http, print_answers
from haystack.nodes import FARMReader, TransformersReader

! wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.9.2-linux-x86_64.tar.gz -q
! tar -xzf elasticsearch-7.9.2-linux-x86_64.tar.gz
! chown -R daemon:daemon elasticsearch-7.9.2
import os
from subprocess import Popen, PIPE, STDOUT

es_server = Popen(
    ["elasticsearch-7.9.2/bin/elasticsearch"], stdout=PIPE, stderr=STDOUT, preexec_fn=lambda: os.setuid(1)  # as daemon
)
# wait until ES has started
! sleep 30

from haystack.document_stores import ElasticsearchDocumentStore

document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", index="document")

doc_dir = "/content/elct"
docs = convert_files_to_docs(dir_path=doc_dir, clean_func=clean_wiki_text, split_paragraphs=True)

print(docs[:3])
document_store.write_documents(docs)

from haystack.nodes import BM25Retriever

retriever = BM25Retriever(document_store=document_store)

reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

from haystack.pipelines import ExtractiveQAPipeline

pipe = ExtractiveQAPipeline(reader, retriever)

prediction = pipe.run(
    query="Chief complaint ?", params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}}
)

from pprint import pprint

pprint(prediction['answers'])

from haystack.pipelines import DocumentSearchPipeline
pipeline = DocumentSearchPipeline(retriever)
query = ' Medicare Risk Adjustment  '
result = pipeline.run(query, params={"Retriever": {"top_k": 10}})

from haystack.utils import print_documents

print_documents(result, max_text_len=100, print_name=True, print_meta=True)

[x.to_dict() for x in result["documents"]]
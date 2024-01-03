import spacy 
from spacy.tokens import Doc
# from spacy.tokens import Example

from spacy_experimental.coref.coref_component import DEFAULT_COREF_MODEL
from spacy_experimental.coref.coref_util import DEFAULT_CLUSTER_PREFIX

import re


# setup ?
files = ['11532192.txt']
text = []

for file in files:
    data = [l.strip() for l in open(file)]
    data = " ".join(data)
    text.append(data)


# https://medium.com/@dipuakagourav/coreference-resolution-of-the-person-entity-c83146a48bd8

class coref_resolution:
  def __init__(self,text):
    self.text = text
  
  def get_coref_clusters(self,):
    self.nlp = spacy.load("en_core_web_trf")
    nlp_coref = spacy.load("en_coreference_web_trf")

    nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
    nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])

    self.nlp.add_pipe("coref", source=nlp_coref)
    self.nlp.add_pipe("span_resolver", source=nlp_coref)

    self.doc = self.nlp(self.text)
    self.tokens = [str(token) for token in self.doc]
    coref_clusters = {key : val for key , val in self.doc.spans.items() if re.match(r"coref_clusters_*",key)}

    return coref_clusters
  
  def find_span_start_end(self,coref_clusters):

    cluster_w_spans = {}
    for cluster in coref_clusters:
      cluster_w_spans[cluster] = [(span.start, span.end, span.text) for span in coref_clusters[cluster]]
    
    return cluster_w_spans
  
  def find_person_start_end(self, coref_clusters,cluster_w_spans):
    # nlp = spacy.load("en_core_web_trf")
    coref_clusters_with_name_spans = {}
    for key, val in coref_clusters.items():
      temp = [0 for i in range(len(val))]
      person_flag = False
      for idx, text in enumerate(val):
        doc = self.nlp(str(text))
        for word in doc.ents:
          # find the absolute token position of PERSON entity
          if word.label_ == 'PERSON':
            temp[idx] = (word.start, word.end, word.text)
            person_flag = True
        for token in doc:
          # find the absolute token position of the pronouns and references
          if token.pos_ == 'PRON':
            temp[idx] = (token.i,token.i+1,token)
      if len(temp) > 0:
        # replace the absolute token positions with the relative token positions in the entire corpus
        if person_flag:
          orig = cluster_w_spans[key]
          for idx, tup in enumerate(orig):
            if isinstance(tup, tuple) and isinstance(temp[idx], tuple):
              orig_start, orig_end, text = tup
              offset_start, offset_end, _ = temp[idx]
              orig_start += offset_start
              orig_end = orig_start + (offset_end - offset_start) 
              orig[idx] = (orig_start, orig_end, text)
          coref_clusters_with_name_spans[key] = orig

    return coref_clusters_with_name_spans
  
  def replace_refs_w_names(self,coref_clusters_with_name_spans):
    tokens = self.tokens
    special_tokens = ["my","his","her","mine"]
    for key, val in coref_clusters_with_name_spans.items():
      if len(val) > 0 and isinstance(val, list):
        head = val[0]
        head_start, head_end, _ = head
        head_name = " ".join(tokens[head_start:head_end])
        for i in range(1,len(val)):
          coref_token_start, coref_token_end, _ = val[i]
          count = 0
          for j in range(coref_token_start, coref_token_end):
            if tokens[j].upper() == "I":
                count += 1
                continue
            if count == 0:
              if tokens[j].lower() in special_tokens:
                if head_name[-1].lower() == "s":
                  tokens[j] = str(head_name)+"'"
                else:
                  tokens[j] = str(head_name)+"'s"
              else:
                tokens[j] = head_name
            else:
              tokens[j] = ""
            count += 1

    return tokens
  
  def main(self,):

    coref_clusters = self.get_coref_clusters()
    coref_w_spans = self.find_span_start_end(coref_clusters)
    coref_clusters_with_name_spans = self.find_person_start_end(coref_clusters,coref_w_spans)
    tokens = self.replace_refs_w_names(coref_clusters_with_name_spans)

    return " ".join(tokens)

# run "coref_resolution..."

sample = text[0]
obj = coref_resolution(sample)
coref_clusters = obj.get_coref_clusters()
print(coref_clusters)
cluster_w_spans = obj.find_span_start_end(coref_clusters)
print(cluster_w_spans)



# nlp = spacy.load('en_core_web_sm')
# nlp.print_pipe # includes ['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer', 'ner']

# sample example object lol
# coref = nlp.add_pipe("experimental_coref")
#coref.initiialize(lambda:examples, nlp=nlp)

# results = [nlp(file) for file in files]
# print([file._.coref_clusters for file in results])


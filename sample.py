import compare
import spacy
import scispacy
import xml.etree.ElementTree as ET

#nlp = spacy.load("en_core_sci_scibert")
nlp = spacy.load("en_core_web_trf")
nlp_coref = spacy.load("en_coreference_web_trf")
nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])
nlp.add_pipe("coref", source=nlp_coref)
nlp.add_pipe("span_resolver", source=nlp_coref)

# fileName = "11532192"
fileList = ['11319941', '11532192', '11597317', '11604102', '11897010']

for fileName in fileList:
    text = " ".join([l.strip() for l in open(f'{fileName}.txt')]) # open file and format text as one continuous paragraph...
    doc = nlp(text)
    tokens = [str(token) for token in doc]

    pred = compare.pred_corefs(doc)
    actual = compare.read_xml(f'{fileName}.xml', doc)

    compare.print_sents(doc, pred, f'{fileName}_pred')
    compare.print_sents(doc, actual, f'{fileName}_actual')

# this prints dict nicely formatted :D
# print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in pred.items()) + "}")
# run the coreference resolver, compare results with actual annotations from xml file!
# make this somewhat scalable so we can replace "filename" and use this script on diff. files
# the goal of this script is so i can open terminal
# set a filename
# run this script to preformat my predicted/actual corefs
# then print corefs[1].actual; corefs[1].predicted to get a comparison.. ?
# and see wht's wrong w predicted .. ? 
import spacy
import xml.etree.ElementTree as ET
import re

class Mention:
    def __init__(self, nodeID):
        self.nodeID = nodeID
        self.annoID = ''
        self.start = ''
        self.end = ''
        self.text = ''


    def __repr__(self):
        return f'{self.text} START @ {self.start}'
    
    def __eq__(self, mention):
        return True if mention.start == self.start else False


def read_xml(fileName, doc):
    char_offsets = [token.idx for token in doc]

    tree = ET.parse(fileName)
    root = tree.getroot()

    coref_clusters = {}

    for triple in root.iter('triple'): # go thru all edges...
        # create "mention" objects 
        subject_key = triple.get('subject')
        node = Mention(triple.get('object'))
        node.annoID = root.find(f'./document/graph-space/vertex/[@id="{node.nodeID}"]').attrib['annotation']
        node.start = int(root.find(f'./document/annotation/[@id="{node.annoID}"]')[1].attrib['start'])
        while node.start not in char_offsets:
            node.start += 1
        node.start = char_offsets.index(int(node.start))
        node.end = root.find(f'./document/annotation/[@id="{node.annoID}"]')[1].attrib['end']
        # node.end = char_offsets.index(int(node.end))
        node.text = root.find(f'./document/annotation/[@id="{node.annoID}"]')[1].text

        if subject_key in coref_clusters: # if subject node alr exists 
            coref_clusters[subject_key].append(node)
        else:
            subject = Mention(subject_key)
            subject.annoID = root.find(f'./document/graph-space/vertex/[@id="{subject.nodeID}"]').attrib['annotation']
            subject.start = int(root.find(f'./document/annotation/[@id="{subject.annoID}"]')[1].attrib['start'])
            while subject.start not in char_offsets:
                subject.start += 1
            subject.start = char_offsets.index(int(subject.start))
            subject.end = int(root.find(f'./document/annotation/[@id="{subject.annoID}"]')[1].attrib['end'])
            subject.text = root.find(f'./document/annotation/[@id="{subject.annoID}"]')[1].text
            coref_clusters[subject_key] = [subject]
            coref_clusters[subject_key].append(node)

    return coref_clusters


def pred_corefs(doc):

    counter = 0
    coref_clusters = {}

    for key, val in doc.spans.items():
        if re.match(f"coref_clusters_*", key):
            coref_clusters[counter] = []
            for item in val:
                node = Mention(counter)
                node.start = int(item.start)
                node.end = int(item.end)
                node.text = item.text
                coref_clusters[counter].append(node)
            counter += 1
        
    return coref_clusters

def print_sents(doc, corefs, fileName):
    with open(fileName, 'w') as f:
        for key, mentions in corefs.items():
            f.write(f'{key}\n')
            for mention in mentions:
                f.write(f'{mention.text} : {doc[mention.start].sent}\n')


def conll_format(doc, corefs, fileName):
    with open(fileName, 'a') as f:
        counter = 0
        lines = []
        for token in doc:
            lines[counter] = f"{fileName}\t0\t{counter}\t{token.text}\t{token.pos}\t-\t-\t-\t-\t-\t-\t-\t-"
            counter +=1
        
        for key, mentions in corefs.items():
            for mention in mentions:
                lines[mention.start] = f"{fileName}\t0\t{counter}\t{token.text}\t{token.pos}\t-\t-\t-\t-\t-\t-\t-\t({key}"
                lines[mention.end] = f"{fileName}\t0\t{counter}\t{token.text}\t{token.pos}\t-\t-\t-\t-\t-\t-\t-\t{key})"


            f.write(f'{fileName},\t0\t{counter}')


def test():
        
    # set up
    nlp = spacy.load("en_core_web_trf")
    nlp_coref = spacy.load("en_coreference_web_trf")
    nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
    nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])
    nlp.add_pipe("coref", source=nlp_coref)
    nlp.add_pipe("span_resolver", source=nlp_coref)

    fileName = "11532192"

    text = " ".join([l.strip() for l in open(f'{fileName}.txt')]) # open file and format text as one continuous paragraph...
    doc = nlp(text)
    tokens = [str(token) for token in doc]

    # each document has an associated PRED and ACTUAL
    # PRED contains coref info as read by pred_corefs thingy
    # ACTUAL contains read_xml info
    # Then you can compare the two because they are in the same format

    pred = pred_corefs(doc)
    actual = read_xml(f'{fileName}.xml', doc)

    # for comparing you should...
    # iterate through clusters in coref_clusters
    # find "head" of cluster in coref_clusters
    # find corresponding group from XML
    # print whole coreference chain (INCLUDING START AND END) from
    # pred and actual
    # automatically check if they are the same....

    # ACTUALLY, why don't we make this a function we can call ?
    # so it takes 


    for actual_cluster, actual_mentions in actual:
        head = actual_mentions[0]
        for pred_cluster, pred_mentions in pred:
            pass
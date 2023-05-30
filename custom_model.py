import pandas as pd
import streamlit as st
import spacy
from spacy import displacy, Language
import spacy
from spacy.matcher import Matcher
from spacy.pipeline import EntityRuler
import pandas as pd
import streamlit as st
from spacy import displacy


def load_model_():
    return spacy.load("fr_core_news_lg")


def testPattern3(user_input):
    dfs = [pd.read_csv('data/H{}.csv'.format(i)) for i in range(7)]
    labels = ['NoH{}'.format(i) for i in range(7)]
    nlp = load_model_()
    nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
    ruler = nlp.get_pipe("entity_ruler")

    for df, label in zip(dfs, labels):
        for concept in df["Concept"]:
            pattern = [{"LOWER": word} for word in concept.lower().split()]
            ruler.add_patterns([{"label": label, "pattern": pattern}])
            pattern_plural = pattern.copy()
            pattern_plural[-1]["LOWER"] += "s"
            ruler.add_patterns([{"label": label, "pattern": pattern_plural}])

    doc = nlp(user_input)

    # Display the entities
    for ent in doc.ents:
        st.text(f"{ent.text}  <<-->>  {ent.label_}")

    label_colors = {"NoH6": "red", "NoH5": "blue", "NoH4": "green", "NoH3": "purple", "NoH2": "orange", "NoH1": "orange"}
    html = displacy.render(doc, style="ent", options={"colors": label_colors}, jupyter=False)
    st.markdown(html, unsafe_allow_html=True)

    nlp.to_disk("herelles3")


def testPattern4(user_input):
    dfs = [pd.read_csv('data/H{}.csv'.format(i)) for i in range(7)]
    labels = ['Nomc_H{}'.format(i) for i in range(7)]
    #nlp = spacy.load('en_core_web_sm')
    nlp = load_model_()
    nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
    ruler = nlp.get_pipe("entity_ruler")

    for df, label in zip(dfs, labels):
        for concept in df["Concept"]:
            doc = nlp(concept.lower())
            pattern = [{"LEMMA": token.lemma_} for token in doc]
            ruler.add_patterns([{"label": label, "pattern": pattern}])

    doc = nlp(user_input)

    @Language.component("lowercase_component")
    def lowercase_component(doc):
        # This will lowercase the text of the Doc and return a new Doc
        return nlp.make_doc(doc.text.lower())

    # Then you add this component before the entity ruler in the pipeline:
    #nlp.add_pipe("lowercase_component", before="entity_ruler")


    # Display the entities

    label_colors = {"Nomc_H6": "red", "Nomc_H5": "blue", "Nomc_H4": "green", "Nomc_H3": "purple", "Nomc_H2": "orange", "Nomc_H1": "orange"}
    html = displacy.render(doc, style="ent", options={"colors": label_colors}, jupyter=False)
    st.markdown(html, unsafe_allow_html=True)

    nlp.to_disk("herelles3v2")



def load_herelles_model_():
    return spacy.load("herelles3v2")

def testPattern_trigger(user_input):
    df = pd.read_csv("data/plu_trigger.csv")
    nlp = load_herelles_model_()

    if 'entity_ruler' not in nlp.pipe_names:
        nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})

    ruler = nlp.get_pipe("entity_ruler")

    for verb in df["Verbs"]:  # Change to the name of your verbs column
        doc = nlp(verb.lower())
        pattern = [{"LEMMA": token.lemma_} for token in doc]
        ruler.add_patterns([{"label": "Trig_PLU", "pattern": pattern}])

    doc = nlp(user_input)

    #label_colors = {"Nomc_H6": "red", "Nomc_H5": "blue", "Nomc_H4": "green", "Nomc_H3": "purple", "Nomc_H2": "orange", "Nomc_H1": "orange", "Nomc_H0": "brown", "Trig_PLU": "yellow" }
    #html = displacy.render(doc, style="ent", options={"colors": label_colors}, jupyter=False)
    #st.markdown(html, unsafe_allow_html=True)
    nlp.to_disk("herelles3Tv2")

"""
if __name__ == "__main__":
    st.title("Entity matching with custom rules")
    user_input = st.text_area("Enter your text here", "")
    if st.button('Match entities'):
        if user_input:
            #testPattern4(user_input)
            testPattern_trigger(user_input)
        else:
            st.write("Please input some text.")"""

import spacy
import pandas as pd



def load_model_():
    return spacy.load("fr_core_news_sm")

def build_model():
    dfs = [pd.read_csv('data/H{}_extend.csv'.format(i)) for i in range(7)]
    labels = ['Nomc_H{}'.format(i) for i in range(7)]
    nlp = load_model_()
    nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
    ruler = nlp.get_pipe("entity_ruler")

    for df, label in zip(dfs, labels):
        for concept in df["Concept"]:
            doc = nlp(concept.lower())
            pattern = [{"LEMMA": token.lemma_} for token in doc]
            ruler.add_patterns([{"label": label, "pattern": pattern}])

    nlp.to_disk("herellesmdextend")

def load_herelles_model_():
    return spacy.load("herellesmdextend")


def addPattern_trigger():
    df = pd.read_csv("data/plu_trigger_extend.csv")
    nlp = load_herelles_model_()

    if 'entity_ruler' not in nlp.pipe_names:
        nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})

    ruler = nlp.get_pipe("entity_ruler")

    for verb in df["Verbs"]:  # Change to the name of your verbs column
        doc = nlp(verb.lower())
        pattern = [{"LEMMA": token.lemma_} for token in doc]
        ruler.add_patterns([{"label": "Trig_PLU", "pattern": pattern}])
    nlp.to_disk("herellesmdfullextend")


if __name__ == "__main__":
    print("build model")
    #build_model()
    #addPattern_trigger()

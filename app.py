import streamlit as st
import spacy
from spacy import displacy
from collections import Counter
import plotly.graph_objects as go
import json
import base64
from bs4 import BeautifulSoup
from spacy.tokens import Doc


st.set_page_config(layout="wide")

# Create a session state
if 'session_state' not in st.session_state:
    st.session_state['session_state'] = {}
state = st.session_state

# Load the model
@st.cache_data
def load_model():
    return spacy.load("herellesmdfull")

nlp = load_model()  # Load the model globally

# Load and process text
@st.cache_data
def process_text(user_input):
    _doc = nlp(user_input)
    return _doc.to_bytes(), json.dumps(_doc.to_json())  # Return the bytes and JSON representation

def handle_uploaded_file(file):
    sections = file.read().decode("utf-8").split(">>>")
    labelled_sections = []
    for i, section in enumerate(sections, 1):
        lines = section.strip().split('\n', 1)
        if len(lines) > 1:
            label, text = lines
            labelled_sections.append((label.strip(), text.strip(), i))  # Also store segment number
    return labelled_sections


# Parse text into labelled sections
def parse_text(text):
    sections = text.split(">>>")
    labelled_sections = []
    for i, section in enumerate(sections, 1):
        lines = section.strip().split('\n', 1)
        if len(lines) > 1:
            label, text = lines
            labelled_sections.append((label.strip(), text.strip(), i))  # Also store segment number
    return labelled_sections

def get_table_download_link_json___(entities):
    """
    Generates a link to download the entities JSON
    """
    json_data = json.dumps(entities)  # Convert entities dictionary to JSON
    b64 = base64.b64encode(json_data.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/json;base64,{b64}" download="entities.json" target="_blank">Download entities JSON</a>'
    return href

def get_table_download_link_json(entities_cache):
    """
    Generates a link to download the entities JSON
    """
    entities = {}
    for entity_dict in entities_cache.values():
        entities.update(entity_dict)
    json_data = json.dumps(entities)  # Convert entities dictionary to JSON
    b64 = base64.b64encode(json_data.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/json;base64,{b64}" download="entities.json" target="_blank">Download entities JSON</a>'
    return href



def get_entities_json(doc, labels):
    """
    Convert entity information to a dictionary
    """
    ent_dic = {ent.text: (ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ent.label_ in labels and len(ent.text)>2}
    print(ent_dic)
    return ent_dic# {ent.text: (ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ent.label_ in labels and len(ent.text)>2}

def display__(doc, selected_labels, segment_number):
    label_colors = {"Nomc_H6": "red", "Nomc_H5": "blue", "Nomc_H4": "green", "Nomc_H3": "purple", "Nomc_H2": "orange",
                    "Nomc_H1": "orange", "Nomc_H0": "brown",  "LOC":"cyan", "GPE": "lime",  "PER": "pink", "Trig_PLU": "olive" }

    options = {"colors": label_colors, "ents": selected_labels}
    html = displacy.render(doc, style="ent", options=options, jupyter=False)
    st.markdown(f"Segment ID: {segment_number}", unsafe_allow_html=True)
    st.markdown(html, unsafe_allow_html=True)
    st.markdown("\n\n----------------------\n\n", unsafe_allow_html=True)

def display___(doc, selected_labels, segment_number):
    label_colors = {"Nomc_H6": "red", "Nomc_H5": "blue", "Nomc_H4": "green", "Nomc_H3": "purple", "Nomc_H2": "orange",
                    "Nomc_H1": "orange", "Nomc_H0": "brown",  "LOC":"cyan", "GPE": "lime",  "PER": "pink", "Trig_PLU": "olive" }

    options = {"colors": label_colors, "ents": selected_labels}
    html = displacy.render(doc, style="ent", options=options, jupyter=False)

    # Parse HTML with BeautifulSoup and remove short entities
    soup = BeautifulSoup(html, 'html.parser')
    for mark in soup.find_all('mark'):
        if len(mark.text.strip()) <= 2:  # Strip whitespace before checking length
            mark.decompose()

    st.markdown(f"Segment ID: {segment_number}", unsafe_allow_html=True)
    st.markdown(str(soup), unsafe_allow_html=True)
    st.markdown("\n\n----------------------\n\n", unsafe_allow_html=True)


def display(doc, selected_labels, segment_number):
    #doc = Doc(doc.vocab, words=[t.text for t in doc], spaces=[t.whitespace_ for t in doc])

    label_colors = {"Nomc_H6": "red", "Nomc_H5": "blue", "Nomc_H4": "green", "Nomc_H3": "purple", "Nomc_H2": "orange",
                    "Nomc_H1": "orange", "Nomc_H0": "brown",  "LOC":"cyan", "GPE": "lime",  "PER": "pink", "Trig_PLU": "olive" }

    options = {"colors": label_colors, "ents": selected_labels}

    # Filter out entities with a text length of less than 3
    ents = [ent for ent in doc.ents if len(ent.text) > 2]
    doc.ents = ents

    html = displacy.render(doc, style="ent", options=options, jupyter=False)

    st.markdown(f"Segment ID: {segment_number}", unsafe_allow_html=True)
    st.markdown(html, unsafe_allow_html=True)
    st.markdown("\n\n----------------------\n\n", unsafe_allow_html=True)




if __name__ == '__main__':
    st.title("Herelles rules Visualization")
    input_option = st.radio("Choose an input method:", ('Upload a .txt file', 'Enter text manually'))
    text = None
    if input_option == 'Upload a .txt file':
        uploaded_file = st.file_uploader("Choose a .txt file", type="txt")
        if uploaded_file is not None:
            text = uploaded_file.read().decode("utf-8")
    else:
        text = st.text_area("Enter your text here:")
    labelled_sections = []
    if text:  # Only proceed if there is text input
        labelled_sections = parse_text(text)

        # Filter out "False" text segments
        labelled_sections = [(label, text, segment_number) for label, text, segment_number in labelled_sections if label != "False"]

    segment_labels = [label for label, _, _ in labelled_sections]
    segment_labels = list(set(segment_labels))

    entities_cache = {}
    segments_cache = {}
    #entities = {}  # Initialize entities dictionary

    with st.sidebar:
        selected_segment = st.selectbox("Select a text segment", options=segment_labels, index=0)
        st.markdown("""
    <style>
        span[data-baseweb="tag"][aria-label="Nomc_H0, close by backspace"]{
            background-color: brown;
        }
        span[data-baseweb="tag"][aria-label="Nomc_H1, close by backspace"]{
            background-color: black;
        }
        span[data-baseweb="tag"][aria-label="Nomc_H2, close by backspace"]{
            background-color: orange;
        }
        span[data-baseweb="tag"][aria-label="Nomc_H3, close by backspace"]{
            background-color: purple;
        }
        span[data-baseweb="tag"][aria-label="Nomc_H4, close by backspace"]{
            background-color: green;
        }
        span[data-baseweb="tag"][aria-label="Nomc_H5, close by backspace"]{
            background-color: blue;
        }
        span[data-baseweb="tag"][aria-label="Nomc_H6, close by backspace"]{
            background-color: red;
        }
        span[data-baseweb="tag"][aria-label="LOC, close by backspace"]{
            background-color: cyan;
        }
        span[data-baseweb="tag"][aria-label="GPE, close by backspace"]{
            background-color: lime;
        }
        span[data-baseweb="tag"][aria-label="PER, close by backspace"]{
            background-color: pink;
        }
        span[data-baseweb="tag"][aria-label="Trig_PLU, close by backspace"]{
            background-color: olive;
        }
    </style>
    """, unsafe_allow_html=True)
        labels = {"Nomc_H6": "red", "Nomc_H5": "blue", "Nomc_H4": "green", "Nomc_H3": "purple", "Nomc_H2": "orange",
                  "Nomc_H1": "orange", "Nomc_H0": "brown", "LOC":"cyan", "GPE": "lime", "PER": "pink", "Trig_PLU": "olive"}
        selected_labels = st.multiselect("Select labels to display", options=labels.keys(), default=list(labels.keys()))
        #selected_labels = [l for l in selected_labels if len(l)>2]

    entities_counter = Counter()

    # Process all segments and cache the results
    for label, text, segment_number in labelled_sections:
        if (label, segment_number) not in segments_cache:
            _doc_bytes, _doc_json = process_text(text)  # Process the text
            _doc = spacy.tokens.Doc(nlp.vocab).from_bytes(_doc_bytes)  # Reconstruct the Doc object from bytes
            segments_cache[(label, segment_number)] = _doc
            entities = get_entities_json(_doc, selected_labels)
            print("****: ", entities)
            entities_cache[(label, segment_number)] = entities  # Cache entities
        else:
            _doc = segments_cache[(label, segment_number)]  # Retrieve the Doc object from cache
            entities = entities_cache[(label, segment_number)]  # Retrieve entities from cache

        if label == selected_segment:
            #_doc = Doc(_doc.vocab, words=[t.text for t in _doc], spaces=[t.whitespace_ for t in _doc])

            display(_doc, selected_labels, segment_number)
            entities_counter.update([ent[2] for ent in entities.values()])  # Increment the count of each entity label

    fig = go.Figure(data=[go.Pie(labels=list(entities_counter.keys()),
                             values=list(entities_counter.values()),
                             marker_colors=[labels[key] for key in entities_counter.keys()],
                             hole=.3,
                             )
                   ])

    fig.update_layout(title_text='Entities Distribution')
    st.sidebar.plotly_chart(fig)

    segment_counter = Counter([label for label, _, _ in labelled_sections])
    st.sidebar.markdown("## Text Segment Count")
    for label, count in segment_counter.items():
        st.sidebar.markdown(f"**{label}**: {count}")

    with st.sidebar:
        st.markdown(get_table_download_link_json(entities_cache), unsafe_allow_html=True)

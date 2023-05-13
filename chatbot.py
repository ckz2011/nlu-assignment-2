import pandas as pd
from  neo4j import GraphDatabase
import gradio as gr

import spacy
nlp = spacy.load("en_core_web_sm")

print("Welcome to Chatbot")

# doc = nlp("Apple is looking for buying U.K startup 100 Billion")


# text = ("Where was CoryLody Educated at? Educated_At")
# doc = nlp(text)

# print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
# print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

# for entity in doc.ents:
#     print(entity.text, entity.label_)


driver = GraphDatabase.driver("bolt://localhost:7687", auth = ("neo4j", "murari1200096"))
print(driver)


def extract_entity(question, entity_type):
    doc = nlp(question)
    for token in doc:
        print(token.pos_)
    for ent in doc.ents:
        print("Entity Label ", ent.label_)
        if ent.label_ in entity_type:
            print("Entity Text ", ent.text)
            return ent.text
    return None

def chatbot(input, history = []):
    output = get_answer(input)
    history.append((input, output))
    return history, history
        

def get_answer(question):
    person_name = extract_entity(question, ["PERSON"])
    print("Found Person_Names >> ", person_name)
    if person_name is None:
        return "Hi Couldn't understand the Question. Please try with another question. eg: Where was John educated at?"
    
    with driver.session() as session:
        if "educate" in question or "educated" in question:
            print("We have educated or educate in Question")
            query_template = "MATCH (p:Person {name: '$person_name'})-[:EDUCATED_AT]->(u:University) RETURN u.name"
            # Replace $person_name with the actual name you want to search for
            query = query_template.replace("$person_name", person_name)
            print("Query > " , query)
            result = session.run(query)
            if result.peek() is None:
                return f"No information found for the person '{person_name}'"
            for record in result:
                print(record)
                return f"The university of '{person_name}' is: {record['u.name']}"
        else:
            return "Hi Couldn't understand the Question. Please try with another question. eg: Where was John educated at?"

gr.Interface(fn = chatbot,
             inputs = ["text",'state'],
             outputs = ["chatbot",'state']).launch(debug = True)
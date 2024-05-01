import pytesseract
from PIL import Image
import re
from transformers import pipeline
import sqlalchemy
import glob  # Import the glob module to find all the files matching a pattern

def image_to_text(image_path):
    # Open an image file using the PIL library
    image = Image.open(image_path)
    # Use pytesseract to convert the image into a string of text
    text = pytesseract.image_to_string(image)
    print(f"Extracted text from {image_path}: {text}")  # Debugging output
    return text

def extract_entities(text):
    # Initialize a Named Entity Recognition (NER) pipeline
    nlp = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english', framework='pt')
    # Process the text through the NER model to identify entities
    entities = nlp(text)
    events = []
    dates = []
    # Iterate through identified entities and categorize them as events or dates based on their entity type
    for entity in entities:
        if entity['entity'] == 'B-LOC' or entity['entity'] == 'I-LOC':
            events.append(entity['word'])
        elif entity['entity'] == 'B-DATE' or entity['entity'] == 'I-DATE':
            dates.append(entity['word'])
    print(f"Extracted entities - Events: {events}, Dates: {dates}")  # Debugging output
    return events, dates

def generate_sql_commands(events, dates):
    sql_commands = []
    # Create SQL commands to insert each event and its corresponding date into the database
    for event, date in zip(events, dates):
        sql = f"INSERT INTO events (event_name, date, time, event_duration, comments) VALUES ('{event}', '{date}', NULL, NULL, '');"
        sql_commands.append(sql)
    print(f"Generated SQL Commands: {sql_commands}")  # Debugging output
    return sql_commands

def main(image_paths):
    for image_path in image_paths:
        text = image_to_text(image_path)
        events, dates = extract_entities(text)
        sql_commands = generate_sql_commands(events, dates)
        engine = sqlalchemy.create_engine('mysql+mysqlconnector://teamAdmin:NookBrosGotchu@mysql-db/panoptesdb')
        with engine.connect() as connection:
            for sql_command in sql_commands:
                result = connection.execute(sql_command)
                print(f"Executed SQL Command: {sql_command}")  # Debugging output

if __name__ == "__main__":
    image_paths = glob.glob('/app/*.jpg')
    print(f"Found {len(image_paths)} images to process.")  # Debugging output
    main(image_paths)

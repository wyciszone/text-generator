import random
import nltk
from nltk.corpus import gutenberg
import PySimpleGUI as sg
import re

corpus_authors = {
    'austen-emma.txt': 'Jane Austen',
    'bible-kjv.txt': 'The Bible',
    'blake-poems.txt': 'William Blake',
    'bryant-stories.txt': 'William Cullen Bryant',
    'burgess-busterbrown.txt': 'Thornton W. Burgess',
    'carroll-alice.txt': 'Lewis Carroll',
    'chesterton-ball.txt': 'G.K. Chesterton',
    'melville-moby_dick.txt': 'Herman Melville',
    'milton-paradise.txt': 'John Milton',
    'shakespeare-macbeth.txt': 'William Shakespeare'
}

class Markov(object):
    def __init__(self, words):
        self.cache = {}
        self.words = words
        self.word_size = len(words)
        self.database()

    def tuples(self):
        for i in range(len(self.words) - 3):
            yield (self.words[i], self.words[i+1], self.words[i+2], self.words[i+3])

    def database(self):
        for w1, w2, w3, w4 in self.tuples():
            key = (w1, w2, w3)
            if key in self.cache:
                self.cache[key].append(w4)
            else:
                self.cache[key] = [w4]

    def generate_markov_text(self, size=100, seed_words=None):
        if seed_words is None:
            seed = random.randint(0, self.word_size-4)
            seed_words = [self.words[seed], self.words[seed+1], self.words[seed+2], self.words[seed+3]]
        gen_words = list(seed_words) if isinstance(seed_words, str) else seed_words.copy()

        for i in range(size - 4):
            w1, w2, w3, w4 = gen_words[-4:]
            try:
                next_word = random.choice(self.cache[(w1, w2, w3)])
            except KeyError:
                next_word = random.choice(self.words)
            gen_words.append(next_word)

        return ' '.join(gen_words)

def format_generated_text(text):
    text = text.replace('"', '').replace("'", "")
    text = text.replace(" .", ".")
    text = text.replace(",,", ",")
    text = text.replace(" ,", ",")
    text = text.replace(" ;", ";")
    text = text.replace("  ", " ")
    text = text.replace(" ?", "?")
    text = re.sub(r'\b\w\.\b', '.', text)
    words_to_remove = ['the', 'an', 'or', 'when']
    pattern = r'\b(?:{})\b(?=\.)'.format('|'.join(words_to_remove))
    text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text

# interfejs
layout = [
    [sg.Text("Choose an author"), sg.Combo(list(corpus_authors.values()), key="author")],
    [sg.Text("Size of generated text"), sg.Spin([i for i in range(30, 301, 10)], initial_value=180, key="size")],
    [sg.Text("Or provide your own corpus"), sg.InputText(key="corpus_file"), sg.FileBrowse()],
    [sg.Text("Seed words"), sg.InputText(key="seed_words")],
    [sg.Multiline(key="generated_text", size=(80, 20))],
    [sg.Text("Filename"), sg.InputText(key="filename")],
    [sg.Button("Generate"), sg.Button("Save"), sg.Button("Exit")]
]

window = sg.Window("Markov Text Generator").Layout(layout)

# generowanie i zapis
while True:
    event, values = window.Read()
    if event in (None, "Exit"):
        break
    if event == "Generate":
        author_name = values["author"]
        author_file = next((file for file, author in corpus_authors.items() if author == author_name), None)
        size = int(values["size"])
        seed_words = values["seed_words"]
        corpus_file = values["corpus_file"]

        if corpus_file:
            with open(corpus_file, "r", encoding = "latin1") as file:
                words = file.read().split()
        elif author_file:
            words = gutenberg.words(author_file)
        else:
            continue

        markov = Markov(words)
        generated_text = markov.generate_markov_text(size, seed_words)
        formatted_text = format_generated_text(generated_text)
        window.Element("formatted_text").Update(formatted_text)

    if event == "Save":
        filename = values["filename"]
        if formatted_text:
            with open(filename, "w") as f:
                f.write(formatted_text)
            sg.Popup("File saved successfully!")
        else:
            sg.Popup("No generated text to save!")

window.Close()

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
        for i in range(len(self.words) - 4):
            yield (self.words[i], self.words[i+1], self.words[i+2], self.words[i+3])

    def database(self):
        for w1, w2, w3, w4 in self.tuples():
            key = (w1, w2, w3)
            if key in self.cache:
                self.cache[key].append(w4)
            else:
                self.cache[key] = [w4]

    def generate_markov_text(self, size=100, seed_words=None):
        gen_words = []

        if seed_words is None:
            seed = random.randint(0, self.word_size-4)
            seed_words = [self.words[seed], self.words[seed+1], self.words[seed+2], self.words[seed+3]]
        else:
            seed_words = seed_words.split() if isinstance(seed_words, str) else seed_words.copy()

        seed_length = len(seed_words)

        if seed_length >= 4:
            gen_words.extend(seed_words[-4:])
        else:
            gen_words.extend(seed_words)

        for i in range(size - len(gen_words)):
            if len(gen_words) < 3:  
                next_word = random.choice(self.words)
            else:
                current_words = gen_words[-3:] 
                try:
                    next_word = random.choice(self.cache[tuple(current_words)])
                except KeyError:
                    next_word = random.choice(self.words)
            gen_words.append(next_word)

        return ' '.join(gen_words)

    def convert_uppercase_to_lowercase(self):
        words_lower = [w.lower() if w.isupper() else w for w in self.words]
        return Markov(words_lower)


class TextFormatter(object):
    @staticmethod
    def remove_repeating_words(text):
        words = text.split()
        filtered_words = [words[0]]

        for i in range(1, len(words)):
            if words[i] != words[i-1] or "'" in words[i]:
                filtered_words.append(words[i])

        return ' '.join(filtered_words)

    @staticmethod
    def fix_interpunction(text):
        text = re.sub(r'([?!])\1+', r'\1', text)
        text = re.sub(r',+', r',', text)
        text = re.sub(r'\.+', r'.', text)

        return text

    @staticmethod
    def capitalize_sentences(text):
        sentences = re.split(r'(?<=[.!?])\s+', text)
        formatted_sentences = []

        for sentence in sentences:
            if sentence:
                formatted_sentence = sentence[0].upper() + sentence[1:]
                formatted_sentences.append(formatted_sentence)

        return ' '.join(formatted_sentences)

    @staticmethod
    def fix_punctuation_spacing(text):
        text = re.sub(r'\s+([.,;?!])', r'\1', text)
        text = re.sub(r'([.,;?!])\s+', r'\1 ', text)

        return text

    def format_text(self, text):
        formatted_text = self.remove_repeating_words(text)
        formatted_text = self.fix_interpunction(formatted_text)
        formatted_text = self.capitalize_sentences(formatted_text)
        formatted_text = self.fix_punctuation_spacing(formatted_text)
        return formatted_text

layout = [
    [sg.Text('Select Corpus:', size=(15, 1)), sg.Combo(list(corpus_authors.values()), size=(30, 1), key='corpus_choice')],
    [sg.Text('Seed Words:', size=(15, 1)), sg.Input(size=(50, 1), key='seed_words')],
    [sg.Text('Generated Text Size:', size=(15, 1)), sg.Input(size=(10, 1), key='text_size')],
    [sg.Text('Custom Corpus:', size=(15, 1)), sg.Input(size=(30, 1), key='custom_corpus_file'), sg.FileBrowse()],
    [sg.Text('Generated Text:', size=(15, 1)), sg.Multiline(size=(70, 10), key='generated_text')],
    [sg.Button('Generate Text', size=(15, 1)), sg.Button('Save File', size=(15, 1)), sg.Button('Exit', size=(15, 1))]
]

window = sg.Window('Text Generator', layout)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == 'Generate Text':
        corpus_choice = values['corpus_choice']
        seed_words = values['seed_words']
        text_size = int(values['text_size'])

        corpus_file = [file for file, author in corpus_authors.items() if author == corpus_choice][0]
        if corpus_file == 'Custom Corpus':
            custom_corpus_file = values['custom_corpus_file']
            corpus = nltk.corpus.PlaintextCorpusReader('', custom_corpus_file).words()
        else:
            corpus = nltk.corpus.gutenberg.words(corpus_file)

        markov = Markov(corpus)
        generated_text = markov.convert_uppercase_to_lowercase().generate_markov_text(size=text_size, seed_words=seed_words)

        formatter = TextFormatter()
        formatted_text = formatter.format_text(generated_text)
        window['generated_text'].update(formatted_text)

    if event == 'Save File':
        save_file = sg.popup_get_file('Save File', save_as=True, default_extension=".txt", file_types=(("Text Files", "*.txt"),))
        if save_file:
            with open(save_file, 'w') as file:
                file.write(window['generated_text'].get())

    if event == 'Exit':
        break

window.close()

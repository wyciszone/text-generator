import random
import nltk
import random
import nltk
from nltk.corpus import gutenberg
import PySimpleGUI as sg

authors = {'Austen': 'austen-emma.txt', 'Bible': 'bible-kjv.txt', 'Blake':'blake-poems.txt', 'Bryant':'bryant-stories.txt', 'Burgess':'burgess-busterbrown.txt', 'Carroll':'carroll-alice.txt', 'Chesterton':'chesterton-ball.txt', 'Melville':'melville-moby_dick.txt', 'Milton':'milton-paradise.txt', 'Shakespeare':'shakespeare-macbeth.txt'}

class Markov(object):
    
    def __init__(self, open_file):
        self.cache = {}
        self.open_file = open_file
        self.words = self.file_to_words()
        self.word_size = len(self.words)
        self.database()
        
    
    def file_to_words(self):
        self.open_file.seek(0)
        data = self.open_file.read()
        words = data.split()
        return words
        
    
    def triples(self):
        if len(self.words) < 3:
            return
        for i in range(len(self.words) - 2):
            yield (self.words[i], self.words[i+1], self.words[i+2])
            
    def database(self):
        for w1, w2, w3 in self.triples():
            key = (w1, w2)
            if key in self.cache:
                self.cache[key].append(w3)
            else:
                self.cache[key] = [w3]

    def generate_markov_text(self, size=random.randint(60,180), seed_words=None):
        if seed_words is None:
            seed = random.randint(0, self.word_size-3)
            seed_words = [self.words[seed], self.words[seed+1], self.words[seed+2]]
        else:
            seed_words = seed_words.split()[-3:]
        gen_words = []
        w1, w2, w3 = seed_words
        for i in range(size):
            gen_words.append(w1)
            try:
                w1, w2, w3 = w2, w3, random.choice(self.cache[(w1, w2)])
            except KeyError:
                w1, w2, w3 = self.words[random.randint(0, self.word_size-3)], self.words[random.randint(0, self.word_size-2)], self.words[random.randint(0, self.word_size-1)]
        gen_words.extend([w2, w3])
        return ' '.join(gen_words)

# window layout

sg.theme('DarkAmber')

layout = [  [sg.Text("Please choose an author:")],
            [sg.Combo(list(authors.keys()), key='-AUTHORS-')],
            [sg.Text('Input starting words:')],
            [sg.Input(key='-SEED-')],
            [sg.Button('Generate'), sg.Button('Cancel')] ]

# create the Window

window = sg.Window('Text generator', layout)

while True:
    event, values = window.read()
    print(values)
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    elif event == 'Generate':
        if values['-AUTHORS-'] in authors:
            filename = authors[str(values['-AUTHORS-'])]
        file = nltk.corpus.gutenberg.open(filename)
        markov = Markov(file)
        seed_words = values['-SEED-']
        generated_text = markov.generate_markov_text(seed_words=seed_words)
        sg.popup_scrolled(generated_text, title='Generated Text')
    
window.close()

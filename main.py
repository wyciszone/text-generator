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
        words = data.replace("'", '').replace('"', '').split()
        for word in words:
            if word.isupper():
                words.remove(word)
        return words
        
    
    def triples(self, use_four_words=False):
        if len(self.words) < 3:
            return
        if use_four_words:
            for i in range(len(self.words) - 3):
                yield (self.words[i], self.words[i+1], self.words[i+2], self.words[i+3])
        else:
            for i in range(min(len(self.words) - 2, 35)):
                yield (self.words[i], self.words[i+1], self.words[i+2])
            for i in range(35, len(self.words) - 3):
                yield (self.words[i], self.words[i+1], self.words[i+2], self.words[i+3])
            
    def database(self):
        for w1, w2, w3, w4 in self.triples(use_four_words=True):
            key = (w1, w2, w3)
            if key in self.cache:
                self.cache[key].append(w4)
            else:
                self.cache[key] = [w4]

    def generate_markov_text(self, beginning_words, size=random.randint(60,180), seed_words=None):
        if seed_words is None:
            seed = random.randint(0, self.word_size-4)
            seed_words = [self.words[seed], self.words[seed+1], self.words[seed+2], self.words[seed+3]]
        else:
            seed_words = seed_words.split()
            if len(seed_words) >= 4:
                seed_words = seed_words[-4:]
            elif len(seed_words) == 3:
                seed_words.append(random.choice(self.words))
            elif len(seed_words) == 2:
                seed_words.extend(random.sample(self.words, 2))
            else:
                seed = random.randint(0, self.word_size-4)
                seed_words = [self.words[seed], self.words[seed+1], self.words[seed+2], self.words[seed+3]]
        gen_words = seed_words.copy()
        use_four_words = False
        for i in range(size-4):
            if i >= 20 and not use_four_words:
                self.cache = {}
                self.database()
                use_four_words = True
            if use_four_words:
                w1, w2, w3, w4 = gen_words[-4:]
                try:
                    next_word = random.choice(self.cache[(w1, w2, w3)])
                except KeyError:
                    next_word = random.choice(self.words)
                gen_words.append(next_word)
            else:
                w1, w2, w3 = gen_words[-3:]
                try:
                    next_word = random.choice(self.cache[(w1, w2)])
                except KeyError:
                    next_word = random.choice(self.words)
                gen_words.append(next_word)
        beginning_words = beginning_words.split()
        try:
            for i in range(0,4):
                beginning_words.pop()
        except IndexError:
            pass
        my_text = beginning_words + gen_words
        return ' '.join(my_text)
        

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
        beginning_words = values['-SEED-']
        generated_text = markov.generate_markov_text(seed_words=seed_words, beginning_words=beginning_words)
        sg.popup_scrolled(generated_text, title='Generated Text')
    
window.close()

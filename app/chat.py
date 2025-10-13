# gui_chat.py — простой GUI для общения с вашим QA‑ботом на основе intests.json / words.pkl / classes.pkl / qa_model.h5
# Требования: pip install tensorflow keras nltk numpy pillow

import json
import random
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

import numpy as np
import pickle
import os

# --- NLP подготовка (совместима с вашим train_bot.py) ---
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

# Убедимся, что нужные токенайзеры есть
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# --- Модель ---
from keras.models import load_model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INTENTS_PATH = os.path.join(BASE_DIR, 'intents.json')
WORDS_PATH = os.path.join(BASE_DIR, 'words.pkl')
CLASSES_PATH = os.path.join(BASE_DIR, 'classes.pkl')
MODEL_PATH = os.path.join(BASE_DIR, 'qa_model.h5')

with open(INTENTS_PATH, 'r', encoding='utf-8') as f:
    intents = json.load(f)

words = pickle.load(open(WORDS_PATH, 'rb'))
classes = pickle.load(open(CLASSES_PATH, 'rb'))
model = load_model(MODEL_PATH)

# --- Вспомогательные функции из классического BoW‑бота ---

def clean_up_sentence(sentence: str):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bow(sentence: str, words_vocab):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words_vocab)
    for s in sentence_words:
        for i, w in enumerate(words_vocab):
            if w == s:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence: str, model_, error_threshold: float = 0.25):
    p = bow(sentence, words)
    res = model_.predict(np.array([p]), verbose=0)[0]
    results = [[i, r] for i, r in enumerate(res) if r > error_threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def get_response(intents_list, intents_json):
    if not intents_list:
        return "Извини, я не понял вопрос. Уточни, пожалуйста."
    tag = intents_list[0]['intent']
    for i in intents_json['intents']:
        if i['tag'] == tag:
            return random.choice(i.get('responses', ["Уточни, пожалуйста."]))
    return "Извини, не нашёл подходящий ответ."


# --- GUI ---
class ChatGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('QA Bot — Чат')
        self.geometry('720x560')

        # История
        self.chat = ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED, font=('Segoe UI', 11))
        self.chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 6))

        # Нижняя панель
        bottom = tk.Frame(self)
        bottom.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.input_var = tk.StringVar()
        self.entry = tk.Entry(bottom, textvariable=self.input_var, font=('Segoe UI', 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind('<Return>', self.on_send)

        self.send_btn = tk.Button(bottom, text='Отправить', command=self.on_send)
        self.send_btn.pack(side=tk.LEFT, padx=8)

        self.clear_btn = tk.Button(bottom, text='Очистить', command=self.clear_chat)
        self.clear_btn.pack(side=tk.LEFT)

        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Сохранить диалог…', command=self.save_transcript)
        file_menu.add_separator()
        file_menu.add_command(label='Выход', command=self.destroy)
        menubar.add_cascade(label='Файл', menu=file_menu)
        self.config(menu=menubar)

        self._append('Бот', 'Привет! Я готов отвечать на вопросы по базе знаний.')
        self.entry.focus_set()

    def _append(self, who: str, text: str):
        self.chat.configure(state=tk.NORMAL)
        self.chat.insert(tk.END, f"{who}: {text}\n")
        self.chat.configure(state=tk.DISABLED)
        self.chat.see(tk.END)

    def clear_chat(self):
        self.chat.configure(state=tk.NORMAL)
        self.chat.delete('1.0', tk.END)
        self.chat.configure(state=tk.DISABLED)

    def save_transcript(self):
        content = self.chat.get('1.0', tk.END)
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text', '*.txt')])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo('Сохранено', f'Диалог сохранён в:\n{path}')

    def on_send(self, event=None):
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set('')
        self._append('Вы', text)

        # Не блокируем UI — отвечаем в отдельном потоке
        threading.Thread(target=self._bot_reply, args=(text,), daemon=True).start()

    def _bot_reply(self, text: str):
        try:
            intents_list = predict_class(text, model)
            reply = get_response(intents_list, intents)
        except Exception as e:
            reply = f"Ошибка обработки вопроса: {e}"
        self._append('Бот', reply)


if __name__ == '__main__':
    app = ChatGUI()
    app.mainloop()

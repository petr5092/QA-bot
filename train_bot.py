import nltk
import json
import pickle
import numpy as np
from nltk.stem import WordNetLemmatizer
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import random
from tensorflow.keras.models import load_model



# Загрузка данных
with open('intents.json', 'r', encoding='utf-8') as file:
    intents = json.load(file)

# Инициализация лемматизатора
lemmatizer = WordNetLemmatizer()

# Списки для хранения данных
words = []
classes = []
documents = []
ignore_words = ['?', '!', '.', ',']

# Токенизация и создание списка документов
for intent in intents['intents']:
    for pattern in intent['patterns']:
        # Токенизация каждого слова в паттерне
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        # Добавление документов (паттерн + метка)
        documents.append((word_list, intent['tag']))
        
        # Добавление тегов в список классов
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# Лемматизация и удаление дубликатов
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

# Сортировка классов
classes = sorted(list(set(classes)))

# Сохраняем слова и классы
pickle.dump(words, open("words.pkl", "wb"))
pickle.dump(classes, open("classes.pkl", "wb"))

# Создание данных для обучения
training_sentences = []
training_labels = []

# Преобразование паттернов в числовые векторы
for doc in documents:
    pattern_words = doc[0]
    training_sentences.append(' '.join(pattern_words))
    training_labels.append(doc[1])

# Кодирование классов
label_encoder = LabelEncoder()
training_labels = label_encoder.fit_transform(training_labels)
training_labels = to_categorical(training_labels, num_classes=len(classes))

# Преобразование слов в векторы
training_sentences = [nltk.word_tokenize(sentence) for sentence in training_sentences]
training_sentences = [[lemmatizer.lemmatize(w.lower()) for w in sentence] for sentence in training_sentences]

# Создание матрицы признаков
# Do not convert `training_sentences` to a NumPy array because it's a list of
# token lists with varying lengths (inhomogeneous). Converting to np.array
# raises ValueError: setting an array element with a sequence. The
# create_bag_of_words function below accepts a list of token lists.

# Преобразование слов в числовые векторы
def create_bag_of_words(documents, words):
    bag = []
    for sentence in documents:
        sentence_words = set(sentence)
        bag_of_words = [1 if w in sentence_words else 0 for w in words]
        bag.append(bag_of_words)
    return np.array(bag)

training_bag = create_bag_of_words(training_sentences, words)

# Строим модель
model = Sequential()
model.add(Dense(128, input_shape=(len(training_bag[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(classes), activation='softmax'))

# Компиляция модели
model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.01), metrics=['accuracy'])

# Обучение модели
model.fit(training_bag, training_labels, epochs=200, batch_size=5, verbose=1)

# Сохраняем модель
model.save("qa_model.h5")
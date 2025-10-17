from fastapi import APIRouter, HTTPException, Body, Query
from chat.schemas import ChatRequest
from typing import Optional
import json
import os
import random
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model

router = APIRouter(
    prefix="/chat",
    tags=["Чат"]
)



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_DIR = os.path.join(BASE_DIR, 'files')
INTENTS_PATH = os.path.join(FILES_DIR, 'intents.json')
WORDS_PATH = os.path.join(FILES_DIR, 'words.pkl')
CLASSES_PATH = os.path.join(FILES_DIR, 'classes.pkl')
MODEL_PATH = os.path.join(FILES_DIR, 'qa_model.h5')


lemmatizer = WordNetLemmatizer()



intents = {}
if os.path.exists(INTENTS_PATH):
    with open(INTENTS_PATH, 'r', encoding='utf-8') as f:
        intents = json.load(f)

try:
    words = pickle.load(open(WORDS_PATH, 'rb'))
except Exception:
    words = []

try:
    classes = pickle.load(open(CLASSES_PATH, 'rb'))
except Exception:
    classes = []

try:
    model = load_model(MODEL_PATH)
except Exception:
    model = None


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
    if model_ is None or not words or not classes:
        return []
    p = bow(sentence, words)
    res = model_.predict(np.array([p]), verbose=0)[0]
    results = [[i, r] for i, r in enumerate(res) if r > error_threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": float(r[1])})
    return return_list


def get_response_from_intents(intents_list, intents_json):
    if not intents_list:
        return None
    tag = intents_list[0]['intent']
    for i in intents_json.get('intents', []):
        if i.get('tag') == tag:
            return random.choice(i.get('responses', ["Уточни, пожалуйста."])), tag
    return None


def fallback_pattern_match(question: str) -> Optional[str]:
    if not intents:
        return None
    q = question.strip().lower()
    for intent in intents.get('intents', []):
        for pattern in intent.get('patterns', []):
            if q == pattern.strip().lower():
                return random.choice(intent.get('responses', []))
    return None





@router.post("/ask")
async def ask_question(body: Optional[ChatRequest] = Body(None), question: Optional[str] = Query(None)):
    question = (body.question if body else None) or question
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Параметр 'question' не должен быть пустым")
    try:
        intents_list = predict_class(question, model)
        if intents_list:
            resp = get_response_from_intents(intents_list, intents)
            if resp:
                answer, intent_tag = resp
                return {"answer": answer, "intent": intent_tag, "source": "model"}
    except Exception:
        pass
    try:
        fallback = fallback_pattern_match(question)
        if fallback:
            return {"answer": fallback, "source": "intents_pattern"}
    except Exception:
        pass
    return {"answer": "Извините, я не понимаю ваш вопрос.", "source": "none"}

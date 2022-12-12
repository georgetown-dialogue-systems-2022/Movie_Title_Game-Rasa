# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import random
from os import path

import pandas as pd
from typing import Text, List, Any, Dict
import numpy as np
from rasa_sdk import Tracker, ValidationAction, Action, FormValidationAction
from rasa_sdk.events import EventType, AllSlotsReset, SlotSet, SessionStarted, ActionExecuted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

guessCountSaver=0
hintCountSaver=0
GUESS_UP_TO=3
HINT_UP_TO=4
Genres=['war',
       'biography', 'western', 'thriller', 'adventure', 'romance',
       'reality-tv', 'mystery', 'horror', 'film-noir', 'musical', 'sport',
       'animation', 'action', 'comedy', 'fantasy', 'history', 'sci-fi',
       'music', 'crime', 'drama', 'family']
Hints=['director','actors','year','description']
hint=set()
A=[]
K=[]

Hard_question_bank='final.csv'
Easy_question_bank='easy.csv'

eval_data = [{"title": "5:⭐⭐⭐⭐⭐", "payload": "5 score"}, {"title": "4:⭐⭐⭐⭐", "payload": "4 score"},
             {"title": "3:⭐⭐⭐", "payload": "3 score"}, {"title": "2:⭐⭐", "payload": "2 score"},
             {"title": "1:⭐", "payload": "1 score"}]

eval_message = {"payload": "quickReplies", "data": eval_data}
eval_t = 'May I take you a few seconds to know how you feel chatting with me?'

class ValidateGenreNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_genre_name_form"


    def validate_difficulty(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `actionType` value."""
        level = tracker.get_slot('difficulty').lower()
        if level == 'hard':
            dispatcher.utter_message(text='Wow!! You are sooooo brave! Come on!')
        elif level == 'easy':
            dispatcher.utter_message(text='Good choice!')
        return {"difficulty": level}

    def validate_genre(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `actionType` value."""
        global A,K
        g = tracker.get_slot('genre').lower()
        if g not in Genres:
            dispatcher.utter_message(text=f'Please enter the correct Genre name!')
            return {"genre": None,"name":None}
        else:

            level = tracker.get_slot('difficulty')
            if level == 'hard':
                data = pd.read_csv(Hard_question_bank)
            else:
                data = pd.read_csv(Easy_question_bank)

            d = data.sample()
            name = d.iloc[0]['movie_title']
            n = name.split()
            if len(n) > 1:
                p = round(len(n) / 3)
                masks = set(random.sample(range(0, len(n)), len(n) - p))
                n = [j if i not in masks else 'X' for i, j in enumerate(n)]
                n = ' '.join(n)
                t = 'We mask some tokens as X. \n The initial film name is: {}'.format(n)
            else:
                n = list(name)
                p = round(len(n) / 3)
                masks = set(random.sample(range(0, len(n)), len(n) - p))
                n = [j if i not in masks else 'X' for i, j in enumerate(n)]
                n = ''.join(n)
                t = 'We mask some characters as X. \n The initial film name is: {}'.format(n)
            dispatcher.utter_message(text=t)
            a=d.iloc[0]['actors'].split(',')
            a=[i.strip() for i in a]
            A=a
            la=len(a)
            k = d.iloc[0]['description']

            if k!='[]':
                k=k[1:-1].split(',')
                k = [i.strip()[1:-1] for i in k]
                lk = len(k)
                K=k
                dispatcher.utter_message(text='You can request a specific or random hint. \n '
                                              'For actors and description hints, each request can only retrieve one. Some movies don\'t have description hints!\n'
                                              'The numbers of hints of this movie are: 1 for year, 1 for director, {} for actors, {} for description'.format(la,lk))
            else:
                dispatcher.utter_message(text='You can request a specific or random hint. \n '
                                              'For actors and description hints, each request can only retrieve one. Some movies don\'t have description hints!\n'
                                              'The numbers of hints of this movie are: 1 for year, 1 for director, {} for actors'.format(
                    la))

            print(name)
            print(A,K)
            return {"genre": g,"name":name}

class ActionValidateGuessing(Action):
    def name(self) -> Text:
        return "action_guess"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",)-> List[Dict[Text, Any]]:

        global guessCountSaver, hintCountSaver, hint
        # movie name can have :
        msg = tracker.latest_message['text']
        first = msg.split(':')[0]
        n = msg.replace(first + ":", "")
        name = tracker.get_slot('name')
        if name is None:
            dispatcher.utter_message(text="Please start the game again and choose a genre.")
        else:
            # debug movie name
            print('The true name is:', name)
            # judge correctness
            c = tracker.get_slot("guesscount")
            dispatcher.utter_message(text='Your guess is: {}'.format(n))
            if n.lower().strip() == name.lower().strip():
                # correct
                dispatcher.utter_message(response='utter_confirm')
                # finish
                t = 'You can restart a new game!'
                dispatcher.utter_message(text=t)
                guessCountSaver = c+1
                hintCountSaver = tracker.get_slot("hintcount")
                hint=set()
                print("hintCountSaver:", hintCountSaver)
                # ask for eval
                dispatcher.utter_message(text=eval_t, json_message=eval_message)
                return []
            elif c - guessCountSaver < GUESS_UP_TO:
                # guess again
                t='Your guess is not correct. Plz try again!'
                dispatcher.utter_message(text=t)
        return []

class Actionhint(Action):
    def name(self) -> Text:
        return "action_hint"

    def run(self, dispatcher, tracker, domain):
        global hintCountSaver, hint, A, K

        # check hint
        print('At present the hint is',hint)
        hint_counter=tracker.get_slot("hintcount")
        # print("intent:",hint_counter,",",hintCountSaver)
        if hint_counter-hintCountSaver+1<=HINT_UP_TO:
            # can ask for hints
            name = tracker.get_slot("name")
            data = pd.read_csv('final.csv')
            la = 0
            lk = 0
            for given_h in hint:
                if given_h in K:
                    lk+=1
                if given_h in A:
                    la+=1

            d = data[data['movie_title'] == name]
            if not tracker.get_slot("hint"):
                if not K:
                    hints = ['year', 'director', 'actors']
                    if la==len(A):
                        hints.pop()

                else:
                    hints = ['year', 'director', 'actors', 'description']
                    if la==len(A):
                        hints.remove('actors')
                    if lk==len(K):
                        hints.remove('description')
                h = hints[random.randint(0,len(hints)-1)]
                if h == 'actors':
                    given = A[la]
                elif h == 'description':
                    given = K[lk]
                else:
                    given = d.iloc[0][h]
                while given in hint:
                    h = hints[random.randint(0, len(hints)-1)]
                    if h == 'actors':
                        given = A[la]
                    elif h == 'description':
                        given = K[lk]
                    else:
                        given = d.iloc[0][h]
                hint.add(given)
                t = 'The {} of this movie is that: {}'.format(h, given)
                dispatcher.utter_message(text=t)
            else:
                h=tracker.get_slot("hint").lower()

                # check hint
                if h=='actors' or h=='actor':
                    given = A[la]
                elif h=='description':
                    given=K[lk]
                elif h=='year' or h=='director':
                    given=d.iloc[0][h]
                else:
                    dispatcher.utter_message(text='Please enter correct hint category!')
                    dispatcher.utter_message(text='You have lost one chance for getting the hint!')
                    return [SlotSet("hint", None)]
                hint.add(given)
                t = 'The {} of this movie is that: {}'.format(h, given)
                dispatcher.utter_message(text=t)
            if h=='actors' and la+1==len(A):
                dispatcher.utter_message(text='You have run out of all actor hints!')
            if h=='description' and lk+1==len(K):
                dispatcher.utter_message(text='You have run out of all keywords hints!')
            # hint count
            t = 'Ask for hint:({}/{})'.format(hint_counter-hintCountSaver+1, HINT_UP_TO)
            dispatcher.utter_message(text=t)
        return [SlotSet("hint", None)]

class ActionGuessCounter(Action):

    def name(self) -> Text:
        return "action_guess_counter"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        global guessCountSaver,hintCountSaver, hint

        count = 0
        current_count = tracker.get_slot("guesscount")
        for event in tracker.applied_events():
            parse=event.get('name')
            # print(parse)
            if parse=='action_guess':
                # intentname=parse.get('intent').get('name')
                # if intentname=='guess':
                count+=1
                # print(intentname,'\n')
        if count!=current_count:
            current_count=count
        print("GUESS: global:", guessCountSaver, "real count:", current_count - guessCountSaver, ', count:', count)
        # Guess more than 3 times
        if current_count-guessCountSaver >= GUESS_UP_TO:
            name = tracker.get_slot('name')
            t = "You have run out of the chance. The correct answer is: {}\n" \
                "You can restart a new game!".format(name)
            dispatcher.utter_message(text=t)
            guessCountSaver =current_count
            hintCountSaver = tracker.get_slot("hintcount")
            hint=set()
            # ask for eval
            dispatcher.utter_message(text=eval_t, json_message=eval_message)
            # finish
            return []
        else:
            return [SlotSet("guesscount", current_count)]

class ActionHintCounter(Action):

    def name(self) -> Text:
        return "action_hint_counter"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        global hintCountSaver
        print("======================")
        print("name:", tracker.get_slot("name"))
        print("genre:",tracker.get_slot("genre"))
        print("genre:", tracker.get_slot("bot_eval"))
        print("difficulty:", tracker.get_slot("difficulty"))
        print("======================")
        count = 0
        current_count = tracker.get_slot("hintcount")
        # print("=====")
        for event in tracker.applied_events():
            parse=event.get('name')
            # print(parse)
            if parse=='action_hint':
                count+=1
        # print("=====")
        if count!=current_count:
            current_count=count
        print("HINT: global:",hintCountSaver,"real count:",current_count-hintCountSaver,', count:',count)
        # Give hint more than 4 times
        if current_count-hintCountSaver >= HINT_UP_TO:
            t = "You can not ask for more hints!"
            dispatcher.utter_message(text=t)
        return [SlotSet("hintcount", current_count)]

class ActionEval(Action):

    def name(self) -> Text:
        return "action_record_eval"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        score=tracker.get_slot(key='bot_eval')
        if score!=0:
            tmp_score = pd.DataFrame({'score': [score]})
            try:
                data = pd.read_csv('eval.csv')
                data = pd.concat([data, tmp_score], axis=0)
            except:
                data = tmp_score
            data.to_csv('eval.csv', index=False)
            dispatcher.utter_message(response='utter_eval')
        return [AllSlotsReset()]

class ActionSessionStart(Action):
    def name(self) -> Text:
        """This is the name to be mentioned in domain.yml and stories.md files
            for this action."""
        return "action_session_start"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker,
            domain: Dict[Text, Any],
    ) -> List[EventType]:
        """This run function will be executed when "action_session_start" is
            triggered."""
        # The session should begin with a 'session_started' event
        events = [SessionStarted()]
        dispatcher.utter_message(
            text="Hi! Welcome to the Movie Wordle Game! Lets' start!")
        # dispatcher.utter_message(template='utter_start')
        events.append(ActionExecuted("action_listen"))
        return events




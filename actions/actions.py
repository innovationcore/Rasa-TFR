# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
import typing
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import datetime


class ActionTimeSet(Action):
    def name(self) -> Text:
        return "action_timeset"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        arg = tracker.get_slot('usertime')
        if arg is None:  # If there is no user specified argument, use system time.
            arg = datetime.datetime.now().time()
        else:
            trim = arg.lower().rfind('p')
            if trim > -1:  # If the user specifies PM, convert to 24h format.
                arg = str(int(arg[0])+12) + arg[1:trim]
            arg = datetime.datetime.strptime(arg, "%H:%M")
            if arg.hour >= 20:  # If the user ends after 8pm, scold them.
                dispatcher.utter_message(template="utter_after8")
        return [SlotSet("prevtime", tracker.get_slot('time')),
                SlotSet("time", arg.hour + arg.minute / 60.0)]


class ActionCompleteFast(Action):
    def name(self) -> Text:
        return "action_completefast"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        endtime = tracker.get_slot('prevtime')
        total = tracker.get_slot('fasts_total') + 1
        wins = tracker.get_slot('fasts_success')
        if endtime is None:
            endtime = 0.0
        delta = 24.0 - abs(endtime - tracker.get_slot('time'))
        if delta > 11.0:
            message="utter_toolate"
        elif delta < 9.0:
            message="utter_tooearly"
        else:
            wins += 1
            message="utter_success"
        return [SlotSet("fasts_total", total),
                SlotSet("fasts_success", wins),
                SlotSet("kdr", round(wins / total * 100.0, 3)),
                FollowupAction(name=message)]

from datetime import datetime
from typing import Any, Dict, List, Text
from dateutil.parser import *
from rasa_sdk import Action, Tracker
from rasa_sdk.events import FollowupAction, SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionTimeSet(Action):
    def name(self) -> Text:
        return "action_timeset"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        arg = tracker.get_slot('usertime')
        if arg is None:  # If there is no user specified argument, use system time.
            arg = datetime.now().time()
        else:
            arg = parse(arg)
        arg = arg.hour + arg.minute / 60.0
        if arg >= 20.0:  # If the user ends after 8pm, scold them.
            dispatcher.utter_message(response="utter_after8")
        return [SlotSet("prevtime", tracker.get_slot('time')),
                SlotSet("time", arg)]


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
            message = "utter_toolate"
        elif delta < 9.0:
            message = "utter_tooearly"
        else:
            wins += 1
            message = "utter_success"
        return [SlotSet("fasts_total", total),
                SlotSet("fasts_success", wins),
                SlotSet("kdr", round(wins / total * 100.0, 3)),
                FollowupAction(name=message)]

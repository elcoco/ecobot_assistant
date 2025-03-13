from typing import Optional
import json
import time
from pathlib import Path

from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from core.tts import TTS
from core.wakeword import WakeWord

from core.ai.tools.base import ToolBaseClass, ToolError
#from core.ai.ai_thread import AIThread
from core.ai.ai import AI


region_map = {
    "Arabia":		      "xa-ar",
    "Arabia (en)":	      "xa-en",
    "Argentina":	      "ar-es",
    "Australia":	      "au-en",
    "Austria":		      "at-de",
    "Belgium (fr)":	      "be-fr",
    "Belgium (nl)":	      "be-nl",
    "Brazil":		      "br-pt",
    "Bulgaria":		      "bg-bg",
    "Canada":		      "ca-en",
    "Canada (fr)":	      "ca-fr",
    "Catalan":		      "ct-ca",
    "Chile":		      "cl-es",
    "China":		      "cn-zh",
    "Colombia":		      "co-es",
    "Croatia":		      "hr-hr",
    "Czech Republic":	  "cz-cs",
    "Denmark":		      "dk-da",
    "Estonia":		      "ee-et",
    "Finland":		      "fi-fi",
    "France":		      "fr-fr",
    "Germany":		      "de-de",
    "Greece":		      "gr-el",
    "Holland":	          "nl-nl",
    "Hong Kong":	      "hk-tz",
    "Hungary":		      "hu-hu",
    "India":		      "in-en",
    "Indonesia":	      "id-id",
    "Indonesia (en)":	  "id-en",
    "Ireland":		      "ie-en",
    "Israel":		      "il-he",
    "Italy":		      "it-it",
    "Japan":		      "jp-jp",
    "Korea":		      "kr-kr",
    "Latvia":		      "lv-lv",
    "Lithuania":	      "lt-lt",
    "Latin America":	  "xl-es",
    "Malaysia":		      "my-ms",
    "Malaysia (en)":	  "my-en",
    "Mexico":		      "mx-es",
    "Netherlands":		  "nl-nl",
    "New Zealand":		  "nz-en",
    "Norway":		      "no-no",
    "Peru":		          "pe-es",
    "Philippines":		  "ph-en",
    "Philippines (tl)":	  "ph-tl",
    "Poland":		      "pl-pl",
    "Portugal":		      "pt-pt",
    "Romania":		      "ro-ro",
    "Russia":		      "ru-ru",
    "Singapore":		  "sg-en",
    "Slovak Republic":	  "sk-sk",
    "Slovenia":		      "sl-sl",
    "South Africa":		  "za-en",
    "Spain":		      "es-es",
    "Sweden":		      "se-sv",
    "Switzerland (de)":	  "ch-de",
    "Switzerland (fr)":	  "ch-fr",
    "Switzerland (it)":	  "ch-it",
    "Taiwan":		      "tw-tzh",
    "Thailand":		      "th-th",
    "Turkey":		      "tr-tr",
    "Ukraine":		      "ua-uk",
    "United Kingdom":	  "uk-en",
    "United States":	  "us-en",
    "United States (es)": "ue-es",
    "Venezuela":		  "ve-es",
    "Vietnam":		      "vn-vi",
    "No region":		  "wt-wt" }


class LookupNewsTool(ToolBaseClass):
    def __init__(self, *args, **kwargs):
        cfg = {
            "type": "function",
            "function": {
                "name": "lookup_news",
                "description": "Get latest news",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subject":   {"type": "string", "description": "News subject" },
                        "region":   {"type": "string", "description": "Country of origin" },
                        #"amount":   {"type": "int", "description": "amount of news items" },
                    },
                    "required": ["subject", "region"],
                },
            }
        }
        super().__init__(cfg, r"^look\s?up\s(?:.*)news", *args, **kwargs)

    def get_news(self, subject: str="", region: str="wt-wt"):
        # TODO: come up with a way to have a conversation by using the aithread.
        #       Solve the circular import problem
        if not subject:
            subject = "news"

        region_code = region_map.get(region.capitalize(), "")
        print(f"Searchin news: subject={subject}, region={region_code}")
        return DDGS().news(keywords=subject, region=region_code, safesearch="off", timelimit="m", max_results=5)

    def parse_json(self, input):
        """ Parse news json into a list of messages that can be fed into AI """
        return [{"role": "user", "content": f"{item['title']}: {item['body']}"} for item in input]


    def call(self, query: str, ww: WakeWord, tts: TTS):
        print("Start tool call")

        tts.speak("Searching for the latest news.")
        
        if not (args := self.parse_args(query, ww, tts)):
            return

        try:
            news = self.get_news(**args)
        except DuckDuckGoSearchException as e:
            tts.speak(f"Failed to connect to duck duck go, are you connected to the internet?")
            raise ToolError(str(e))

        context = self.parse_json(news)

        # Lookup ai and feed chunks of text to TTS while being interruptable by wakeword
        ai = AI(self._ai_model)
        with ww, ai("Give an overview of the latest news events in non-markdown text", context=context) as t:
            while not t.is_finished():
                if ww.is_triggered():
                    break

                if not (sentence := t.get_sentence()):
                    time.sleep(.1)
                    continue

                with tts(sentence):
                    if tts.wait(ww.is_triggered):
                        break

        print("exit tool call")

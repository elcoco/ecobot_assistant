from typing import Optional
import json

from duckduckgo_search import DDGS

from core.ai.tools.base import ToolBaseClass, ToolError
from core.ai import AI
#from core.ai.ai_thread import AIThread


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
    " Hong Kong":	      "hk-tz",
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
                    "required": [],
                },
            }
        }
        super().__init__(cfg, r"^look\s+up\s(?:\w*\s)news", *args, **kwargs)

    def get_news(self, subject: str="", region: str="wt-wt"):
        # TODO: come up with a way to have a conversation by using the aithread.
        #       Solve the circular import problem
        results = DDGS().news(keywords=subject, region=region, safesearch="off", timelimit="m", max_results=20)
        return json.dumps(results)

    def call(self, query: str):
        args = self.call_ai_tools(query)
        results = self.get_news(**args)
        for l in results:
            print(json.dumps(l, indent=4))
        return ""

import os
from chatterbot import ChatBot, response_selection
from chatterbot.trainers import ChatterBotCorpusTrainer

from django.conf import settings


# Setting up the basic functionality of how the chatbot should operate

def build_bot():
    chat_bot = ChatBot("Persimmon Bank",
                       logic_adapters=[
                          {
                              "import_path": "chatterbot.logic.BestMatch",
                              "statement_comparison_function": "comparisons.levenshtein_distance",
                              "response_selection_method": response_selection.get_first_response
                          },
                          {
                              "import_path": "chatterbot.logic.BestMatch",
                              "default_response": "I'm sorry I'm not sure what you mean",
                              "maximum_similarity_threshold": .95
                          }

                       ], database_uri='sqlite:///' + settings.CHATBOT_DATABASE, read_only=True)
    return chat_bot


def train_bot():
    if os.path.exists(settings.CHATBOT_DATABASE):
        os.remove(settings.CHATBOT_DATABASE)

    chat_bot = build_bot()
    trainer = ChatterBotCorpusTrainer(chat_bot)

    trainer.train(
        os.path.join(os.path.dirname(__file__), './trainer/appointment.json'),
        os.path.join(os.path.dirname(__file__), './trainer/home_page.json'),
        os.path.join(os.path.dirname(__file__), './trainer/mobile_atm.json'),
        os.path.join(os.path.dirname(__file__), './trainer/transfer_funds.json'),
        os.path.join(os.path.dirname(__file__), './trainer/update_contact_info.json'),
        os.path.join(os.path.dirname(__file__), './trainer/greetings.json'),
        os.path.join(os.path.dirname(__file__), './trainer/new_account.json'),
        os.path.join(os.path.dirname(__file__), './trainer/my_accounts.json'),
    )


def run_bot(inp):
    chat_bot = build_bot()
    response = chat_bot.get_response(inp)
    return response


train_bot()

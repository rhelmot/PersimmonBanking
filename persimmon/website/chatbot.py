import os
from chatterbot import ChatBot, response_selection
from chatterbot.trainers import ChatterBotCorpusTrainer
import chatterbot.utils

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
    trainer = ChatterBotCorpusTrainer(chat_bot, show_training_progress=False)

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


# hackfix. we need to monkeypatch download(quiet=True) for our own sanity but also so CI will work correctly
# pylint: disable=import-outside-toplevel,raise-missing-from
def nltk_download_corpus(resource_path):
    """
    Download the specified NLTK corpus file
    unless it has already been downloaded.

    Returns True if the corpus needed to be downloaded.
    """
    from nltk.data import find
    from nltk import download
    from os.path import split, sep
    from zipfile import BadZipfile

    # Download the NLTK data only if it is not already downloaded
    _, corpus_name = split(resource_path)

    if not resource_path.endswith(sep):
        resource_path = resource_path + sep

    downloaded = False

    try:
        find(resource_path)
    except LookupError:
        download(corpus_name, quiet=True)
        downloaded = True
    except BadZipfile:
        raise BadZipfile(
            'The NLTK corpus file being opened is not a zipfile, '
            'or it has been corrupted and needs to be manually deleted.'
        )

    return downloaded


train_bot()
chatterbot.utils.nltk_download_corpus = nltk_download_corpus

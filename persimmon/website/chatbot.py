from chatterbot import ChatBot, comparisons, response_selection
from chatterbot.trainers import ChatterBotCorpusTrainer
import os

def runbot(inp):

    # Setting up the basic functionality of how the chatbot should operate
    chatbot = ChatBot("Persimmon Bank",
                      logic_adapters=[
                          {
                              "import_path": "chatterbot.logic.BestMatch",
                              "statement_comparison_function": "comparisons.levenshtein_distance",
                              "response_selection_method": response_selection.get_first_response
                          },
                          {
                              "import_path": "chatterbot.logic.BestMatch",
                              "default_response": "I'm sorry I'm not sure what you mean",
                              "maximum_similarity_threshold": .65
                          }

                      ]
                      )

    trainer = ChatterBotCorpusTrainer(chatbot)

    trainer.train("chatterbot.corpus.english.greetings",
                "chatterbot.corpus.english.conversations"
                  )
    trainer.train(os.path.join(os.path.dirname(__file__), './trainer/home_page.json'))


    # "Hi",
    # "http://127.0.0.1:8000/website/chatbot",
    # "Hi how's it going?",
    # "http://127.0.0.1:8000/website/chatbot",
    # "Yo",
    # "http://127.0.0.1:8000/website/chatbot"
    response = chatbot.get_response(inp)
    return response

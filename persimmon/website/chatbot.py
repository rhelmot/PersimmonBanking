from chatterbot import ChatBot, response_selection
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
                              "maximum_similarity_threshold": .95
                          }

                      ]
                      )

    trainer = ChatterBotCorpusTrainer(chatbot)

    trainer.train(os.path.join(os.path.dirname(__file__), './trainer/appointment.json'),
                  os.path.join(os.path.dirname(__file__), './trainer/home_page.json'),
                  os.path.join(os.path.dirname(__file__), './trainer/transfer_funds.json'),
                  os.path.join(os.path.dirname(__file__), './trainer/update_contact_info.json'),
                  os.path.join(os.path.dirname(__file__), './trainer/greetings.json')
                  )

    response = chatbot.get_response(inp)
    return response

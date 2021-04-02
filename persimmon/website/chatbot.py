import os
from chatterbot import ChatBot, response_selection
from chatterbot.trainers import ChatterBotCorpusTrainer


# Setting up the basic functionality of how the chatbot should operate

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

                  ], database_uri=None, read_only=True
                   )
# Training the bot
trainer = ChatterBotCorpusTrainer(chat_bot)

trainer.train(os.path.join(os.path.dirname(__file__), './trainer/appointment.json'),
              os.path.join(os.path.dirname(__file__), './trainer/home_page.json'),
              os.path.join(os.path.dirname(__file__), './trainer/mobile_atm.json'),
              os.path.join(os.path.dirname(__file__), './trainer/transfer_funds.json'),
              os.path.join(os.path.dirname(__file__), './trainer/update_contact_info.json'),
              os.path.join(os.path.dirname(__file__), './trainer/greetings.json'),
              os.path.join(os.path.dirname(__file__), './trainer/new_account.json'),
              os.path.join(os.path.dirname(__file__), './trainer/my_accounts.json'),
              )


def run_bot(inp):
    response = chat_bot.get_response(inp)
    return response

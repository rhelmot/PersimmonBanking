from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer


def runbot(inp, train_bot=False):
    chatbot = ChatBot("Persimmon Bank")

    conversation = [
        "http://127.0.0.1:8000/website/chatbot",
    ]

    trainer = ListTrainer(chatbot)

    trainer.train(conversation)

    response = chatbot.get_response("http://127.0.0.1:8000/website/chatbot")
    print(response)
    return (response)
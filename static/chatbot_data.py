from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import spacy

spacy.load("en_core_web_sm")

chatbot = ChatBot(
    "CRCE Bot",
    logic_adapters=[
        {
            "import_path": "chatterbot.logic.BestMatch",
            "default_response": "Sorry, I don't have information on that.",
            "maximum_similarity_threshold": 0.90,
        }
    ],
    database_uri="sqlite:///chatbot.sqlite3",
)

trainer = ListTrainer(chatbot)

conversation = [
    "hi",
    "Hello! Welcome to CRCE Bot 😊",
    "placement details",
    "Our college provides strong placement support with reputed recruiters.",
    "hostel details",
    "Hostel facilities are available with good accommodation and safety.",
    "courses offered",
    "We offer undergraduate, postgraduate and doctoral programs."
]

# 🚨 TRAIN ONLY ONCE
if __name__ == "__main__":
    trainer.train(conversation)

import openai
import logging
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR")
TOP_K = int(os.getenv("TOP_K"))

openai.api_key = OPENAI_API_KEY

embedding_model = SentenceTransformer(MODEL_NAME)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)

logger.info("Connecting to ChromaDB ")
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
collection = chroma_client.get_or_create_collection(name="faq_embeddings", embedding_function=embedding_fn)

def correct_grammar(text: str) -> str:
    prompt = (
        """The following sentence is written in Azerbaijani but may contain grammar mistakes or informal transliterations of characters (e.g., "ç" as "c", "ş" as "sh", "ə" as "e", etc.).
Please rewrite the sentence in correct Azerbaijani grammar and spelling. Only return the corrected sentence. Please dont translate this words - login, mygov, egov.

**User message:** "{}"
""".format(text)
    )
    try:
        logger.info(f"Correcting grammar for input: {text}")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0,
        )
        corrected = response['choices'][0]['message']['content'].strip()
        logger.info(f"Grammar corrected: {corrected}")
        return corrected
    except Exception as e:
        logger.error(f"Grammar correction failed: {e}")
        return text


def retrieve_chunks(question: str, k=TOP_K):
    logger.info(f"Retrieving top {k} chunks for: {question}")
    try:
        results = collection.query(query_texts=[question], n_results=k)
        docs = results['documents'][0]
        for i, doc in enumerate(docs, 1):
            logger.info(f"Chunk {i}: {doc[:100]}...")
        return docs
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return []

def generate_answer(user_question: str, retrieved_chunks: list) -> str:
    context = "\n\n".join(retrieved_chunks)
    prompt = (
        "You are an AI assistant trained to answer Azerbaijani government-related FAQs.\n"
        "You will be given a user question and a few relevant context snippets.\n"
        "Use the context to provide the most accurate and clear answer to the question.\n"
        "If the context does not contain a clear answer, politely state that you're unsure.\n\n"
        f"**User Question (in Azerbaijani):**\n{user_question}\n\n"
        f"**Relevant Context:**\n{context}\n\n"
        "Answer (in Azerbaijani):"
    )
    try:
        logger.info("Sending final prompt to OpenAI...")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3,
        )
        answer = response['choices'][0]['message']['content'].strip()
        logger.info(f"Final answer generated: {answer}")
        return answer
    except Exception as e:
        logger.error(f"OpenAI generation failed: {e}")
        return "Bağışlayın, cavabı hazırlamaq mümkün olmadı."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    logger.info(f"Received message from user: {user_question}")

    await update.message.reply_text("Cavab hazırlanır...")

    corrected = correct_grammar(user_question)
    chunks = retrieve_chunks(corrected)
    answer = generate_answer(corrected, chunks)

    await update.message.reply_text(answer)
    logger.info("Answer sent to user.\n")


def main():
    logger.info("Starting Telegram bot...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()


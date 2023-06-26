import logging

from chatbot.ai.workers.thread_summarizer.thread_summarizer import logger
from chatbot.mongo_database.mongo_database_manager import MongoDatabaseManager
from chatbot.system.filenames_and_paths import get_thread_backups_collection_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def grab_green_check_messages(server_name: str,
                                    all_thread_collection_name: str = None,
                                    overwrite: bool = False,
                                    save_to_json: bool = True,
                                    collection_name: str = "green_check_messages"):
    mongo_database = MongoDatabaseManager()
    if all_thread_collection_name is None:
        all_thread_collection_name = get_thread_backups_collection_name(server_name=server_name)

    all_thread_collection_name = mongo_database.get_collection(all_thread_collection_name)
    all_threads  = list(all_thread_collection_name.find())

    logger.info("Generating thread summary")
    total_cost = 0
    for thread_entry in all_threads:

        if not thread_entry["green_check_emoji_present"]:
            continue

        print("=====================================================================================================")
        print("=====================================================================================================")
        print(
            f"Thread: {thread_entry['thread_title']}, Channel: {thread_entry['channel']}, Created at: {thread_entry['created_at']}")
        print(f"{thread_entry['thread_url']}")

        messages_with_green_check = []
        for message in thread_entry["messages"]:
            if message["green_check_emoji_present_in_message"]:
                messages_with_green_check.append(message["content"])

                await mongo_database.upsert(
                    collection=collection_name,
                    query={"_student_name": thread_entry["_student_name"]},
                    data={"$addToSet": {"thread_id": thread_entry["thread_id"],
                                        "green_check_messages": message["content"]}}
                )
        print(f"Student: {thread_entry['_student_name']}: \n"
              f"Messages with green check: {messages_with_green_check}")


    if save_to_json:
        mongo_database.save_json(collection_name=collection_name)


if __name__ == "__main__":
    import asyncio

    asyncio.run(grab_green_check_messages(server_name="Neural Control of Real World Human Movement 2023 Summer1",
                                          overwrite=True,
                                          save_to_json=True,
                                          ))

from datetime import datetime
import os
import json
import sys


def run(folder_path, messages_loc):
    """
    Function to convert WhatsApp chat text files to JSON format.

    Parameters:
        folder_path (str): Path to the folder containing the WhatsApp chat text files.
        messages_loc (str): Path to the folder where the JSON files will be saved.

    Usage:
        python convert.py 'C:/Users/johns/Downloads/whatsapp' "C:/Users/johns/Downloads/facebook-data/messages"
    """

    for root, directories, files in os.walk(folder_path):
        for file in files:
            print("Processing: ", file)

            # Read the text file
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                lines = f.readlines()

            if "WhatsApp Chat with " in file:
                idx = file.find("WhatsApp Chat with ")
                title = file[idx + 19 : -4]
            else:
                print("File name does not contain 'WhatsApp Chat with'")
                title = "chat"

            thread = messages_loc + "/inbox/" + "WhatsApp - " + title

            if not os.path.exists(thread):
                os.makedirs(thread)

            # Initialize the json structure
            chat_data = {
                "participants": [],
                "messages": [],
                "title": title,
                # "is_still_participant": true,
                "thread_path": "inbox/" + "WhatsApp - " + title,
                "magic_words": [],
            }

            # Initialize variables to keep track of participants and current message sender
            participants = set()
            current_sender = None

            # Loop through each line and process accordingly
            for line in lines:
                parts = line.split(" - ")
                if len(parts) == 2 and "\u202f" in parts[0]:
                    timestamp_str, message_content = parts
                    timestamp_str = timestamp_str.strip()
                    message_content = message_content.strip()

                    # Replace the invisible character with a space and convert to datetime object
                    timestamp_str = timestamp_str.replace("\u202f", " ")
                    timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y, %I:%M %p")

                    if len(message_content.split(": ")) == 1:
                        print("Assuming WhatsApp notification message: " + line[22:-1])
                        continue

                    else:
                        components = message_content.split(": ")
                        sender = components[0]
                        message = ": ".join(components[1:])

                        if sender != current_sender:
                            current_sender = sender
                            participants.add(current_sender)

                        message_data = {
                            "sender_name": sender,
                            "timestamp_ms": int(timestamp.timestamp() * 1000),
                            "content": message,
                        }
                        chat_data["messages"].append(message_data)

                elif line.endswith("\n"):
                    # Someone sent a message with a return. Append to previous message with \n.
                    chat_data["messages"][-1]["content"] += " \n " + line[:-1]
                    continue

                else:
                    print(
                        "Process failed. Line contained hyphen or a hard return: \n "
                        + line[:-1]
                    )
                    continue

            # Assign participants list to the chat_data dictionary
            chat_data["participants"] = [{"name": name} for name in participants]

            # Write the facebook messenger dictionary to a JSON file
            out_file = open(thread + "/message_1.json", "w")
            json.dump(chat_data, out_file, indent=6)
            out_file.close()


if __name__ == "__main__":
    # Example usage:
    # python convert.py 'C:/Users/johns/Downloads/whatsapp' "C:/Users/johns/Downloads/facebook-data/messages"

    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} whatsapp_folder messages_folder")
    else:
        whatsapp_folder = sys.argv[1]
        messages_folder = sys.argv[2]
        run(whatsapp_folder, messages_folder)

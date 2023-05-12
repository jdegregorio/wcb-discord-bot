import re
from dev.score_truax import generate_humor_scores


def load_file(file_path):
    try:
        with open(file_path, 'r') as f:
            text = f.read()
        return text
    except Exception as e:
        print(f"Failed to load file {file_path} due to {e}")
        return ""


def split_by_author(text):
    chunks = re.split('(?=\n\n.+\n  \d{1,2}:\d{2} (?:AM|PM))', text)
    chunks = [chunk for chunk in chunks if not 'agoView thread' in chunk]
    return chunks


def structure_as_dict(message_str):
    lines = message_str.strip().split('\n')
    if len(lines) < 3:
        return None

    author = lines[0]
    time = lines[1].strip()
    content = '\n'.join(lines[2:])
    
    return {
        'author': author,
        'time': time,
        'content': content,
    }


def remove_patterns(text):
    text = re.sub(r'\d{1,2}:\d{2}( AM| PM)?', '', text)
    text = re.sub(r'\(edited\)', '', text)
    return text


def gather_author_messages(messages, author, n, other_author_name='Friend'):
    author_messages = [i for i, msg in enumerate(messages) if msg['author'] == author]
    output = []
    for idx in author_messages:
        start = max(0, idx - n)
        relevant_messages = messages[start:idx+1]
        conversation = ''
        for msg in relevant_messages:
            msg_author = msg['author'] if msg['author'] == author else other_author_name
            conversation += '{}: {}\n'.format(msg_author, msg['content'])
        output.append(conversation)
    return output


if __name__ == "__main__":
    paths = [
        "wcb_data/WCB_General_2017.txt",
        "wcb_data/WCB_General_2018.txt",
        "wcb_data/WCB_General_2019.txt",
        "wcb_data/WCB_General_2020.txt",
        "wcb_data/WCB_General_1_1_21_to_11_17_22.txt"
    ]

    messages_truax = []
    for path in paths:
        text = load_file(path)
        text_processed = split_by_author(text)
        messages = [structure_as_dict(message) for message in text_processed]
        messages = [message for message in messages if message is not None]
        for message in messages:
            message['content'] = remove_patterns(message['content'])
        messages_truax.extend(gather_author_messages(messages, "andrew.truax", 5))

    # Generate scores and handle exceptions
    messages_truax_scored = []
    for message in messages_truax:
        try:
            score = generate_humor_scores(message)
            message_dict = {'message': message, 'score': score}
            messages_truax_scored.append(message_dict)
        except Exception as e:
            print(f"Failed to generate score for message due to {e}")
            message_dict = {'message': message, 'score': None}
            messages_truax_scored.append(message_dict)

    # Sort by score
    messages_truax_scored = sorted(messages_truax_scored, key=lambda x: (x['score'] is None, x['score']), reverse=True)

    # If you want to write the conversations and scores to a file, you can use the following code:
    with open('./dev/truax_messages.txt', 'w') as f:
        for message in messages_truax_scored:
            f.write("\n---------\n")
            f.write(f"CONVERSATION:\n'''{message['message']}\n'''")
            if message['score'] is not None:
                f.write(f"\nOUTPUT SCORE: {message['score']}\n---------")
            else:
                f.write("\nOUTPUT SCORE: Failed to generate\n---------")


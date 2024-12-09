import html

from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    print('current_question_id', current_question_id)
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to the Django session.
    '''
    if current_question_id and answer not in ["A", "B", "C", "D"]:
        return False, "Answer should be one of A, B, C or D."
    # Store the user's answer in the session
    if current_question_id:
        session[f"question_{current_question_id - 1}_answer"] = ord(answer) - ord('A')

    return True, ""



def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    # Set current question id if not set
    if not current_question_id:
        current_question_id = 0

    # Ensure the current question ID is valid
    if current_question_id >= len(PYTHON_QUESTION_LIST):
        return None, -1  # No more questions

    # Fetch the current question and options
    current_question = PYTHON_QUESTION_LIST[current_question_id]
    question_text = current_question["question_text"]
    options = current_question["options"]

    # Determine the next question ID (or -1 if this is the last question)
    next_question_id = current_question_id + 1 if current_question_id + 1 < len(PYTHON_QUESTION_LIST) else -1

    # Return empty question if next question id is invalid
    if next_question_id == -1:
        return None, None

    return (
        html.escape(f"Question {current_question_id + 1}: {question_text}\n"
        f"A: {options[0]}\n"
        f"B: {options[1]}\n"
        f"C: {options[2]}\n"
        f"D: {options[3]}\n"),
        next_question_id
    )



def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    score = 0
    total_questions = len(PYTHON_QUESTION_LIST)

    # Check each question in the question list
    for current_question_id, question in enumerate(PYTHON_QUESTION_LIST):
        correct_answer = question["options"].index(question["answer"])
        
        # Get the user's answer from the session
        user_answer = session.get(f'question_{current_question_id}_answer')

        # Increment the score if the user's answer matches the correct answer
        if user_answer == correct_answer:
            score += 1

    # Return the final score message
    return f"Your score is {score}/{total_questions}. Well done!"


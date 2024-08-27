import streamlit as st
import groq
import time

# Set up Groq client (replace with your actual API key)
client = groq.Client(api_key="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")

def generate_complete_response(system_message, user_message, model, max_tokens):
    """Generates a complete response without truncation."""
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        model=model,
        max_tokens=max_tokens
    )
    result = response.choices[0].message.content.strip()

    while not result.endswith(('.', '!', '?')):
        additional_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Continue the previous response."},
                {"role": "user", "content": result}
            ],
            model=model,
            max_tokens=max_tokens
        )
        result += " " + additional_response.choices[0].message.content.strip()
        
    return result

def extract_key_points(argument):
    system_message = "Extract 2-3 key points from the given argument."
    return generate_complete_response(system_message, argument, model="llama-3.1-70b-versatile", max_tokens=100)

def generate_argument(prompt, stance, previous_arguments=""):
    system_message = (f"You are an aggressive debater. Strongly argue {stance} the given situation, directly "
                      f"challenging and contradicting your opponent's points. Be confrontational and pick apart their arguments.")
    user_message = f"Situation: {prompt}\n\nPrevious arguments:\n{previous_arguments}"
    return generate_complete_response(system_message, user_message, model="llama-3.1-70b-versatile", max_tokens=200)

def determine_winner_and_summarize(prompt, debate_transcript):
    winner_response = generate_complete_response(
        "Determine the winner of the debate based on the strength of arguments.",
        f"Situation: {prompt}\n\nDebate transcript:\n{debate_transcript}",
        model="llama-3.1-70b-versatile",
        max_tokens=50
    )
    summary_response = generate_complete_response(
        "Provide 2-3 key points summarizing the debate.",
        f"Situation: {prompt}\n\nDebate transcript:\n{debate_transcript}",
        model="llama-3.1-70b-versatile",
        max_tokens=200
    )
    return f"Winner: {winner_response}\n\n{summary_response}"

# The rest of your Streamlit app remains unchanged...

st.title("Nivan - Fight Club")

if 'debate_started' not in st.session_state:
    st.session_state.debate_started = False
    st.session_state.debate_transcript = ""
    st.session_state.round = 0

if not st.session_state.debate_started:
    debate_type = st.radio("Choose debate type:", ["AI vs AI", "AI vs Human", "Human vs Human"])
    situation = st.text_area("Enter a debate topic:")

    if debate_type == "AI vs Human":
        human_stance = st.radio("Choose your stance:", ["For", "Against"])

    if st.button("Start Debate"):
        if situation:
            st.session_state.debate_started = True
            st.session_state.debate_type = debate_type
            st.session_state.situation = situation
            if debate_type == "AI vs Human":
                st.session_state.human_stance = human_stance
            st.session_state.round = 1
            st.session_state.ai_response = ""
            st.session_state.human_argument = ""
            st.rerun()
        else:
            st.warning("Please enter a debate topic.")

else:
    st.write(f"Debate topic: {st.session_state.situation}")
    st.write(f"Debate type: {st.session_state.debate_type}")

    if st.session_state.debate_type == "AI vs AI":
        if st.session_state.round <= 3:
            with st.spinner(f"Round {st.session_state.round}: Teams arguing..."):
                if st.session_state.round > 1:
                    key_points = extract_key_points(st.session_state.debate_transcript.split('\n\n')[-2])
                    team_a_argument = generate_argument(st.session_state.situation,
                                                        "in favor of and contradicting the previous argument",
                                                        f"Points to contradict:\n{key_points}\n\nFull debate:\n{st.session_state.debate_transcript}")
                else:
                    team_a_argument = generate_argument(st.session_state.situation, "in favor of",
                                                        st.session_state.debate_transcript)
                st.write("Team A:", team_a_argument)
                st.session_state.debate_transcript += f"Team A: {team_a_argument}\n\n"

                key_points = extract_key_points(team_a_argument)
                team_b_argument = generate_argument(st.session_state.situation,
                                                    "against and contradicting the previous argument",
                                                    f"Points to contradict:\n{key_points}\n\nFull debate:\n{st.session_state.debate_transcript}")
                st.write("Team B:", team_b_argument)
                st.session_state.debate_transcript += f"Team B: {team_b_argument}\n\n"

            st.session_state.round += 1
            if st.session_state.round <= 3:
                if st.button("Next Round", key=f"next_round_{st.session_state.round}"):
                    st.rerun()
            else:
                if st.button("Conclude Debate", key="conclude_debate"):
                    st.rerun()
        else:
            st.subheader("Debate Result and Key Points:")
            with st.spinner("Determining winner and summarizing..."):
                result = determine_winner_and_summarize(st.session_state.situation, st.session_state.debate_transcript)
            st.write(result)

            if st.button("Start New Debate"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

    elif st.session_state.debate_type == "AI vs Human":
        st.write(f"Round {st.session_state.round}")

        if st.session_state.human_stance == "For":
            if not st.session_state.human_argument:
                human_argument = st.text_area(f"Your argument (For):")
                if st.button("Submit", key=f"submit_human_{st.session_state.round}"):
                    st.session_state.human_argument = human_argument
                    st.session_state.debate_transcript += f"Human: {human_argument}\n\n"
                    st.rerun()
            else:
                st.write("Human:", st.session_state.human_argument)
                if not st.session_state.ai_response:
                    with st.spinner("AI arguing..."):
                        key_points = extract_key_points(st.session_state.human_argument)
                        ai_argument = generate_argument(
                            st.session_state.situation,
                            "against",
                            f"Directly challenge and contradict these points from your opponent:\n{key_points}\n\nFull debate:\n{st.session_state.debate_transcript}"
                        )
                    st.session_state.ai_response = ai_argument
                    st.session_state.debate_transcript += f"AI: {ai_argument}\n\n"
                    st.rerun()
                else:
                    st.write("AI:", st.session_state.ai_response)
                    if st.session_state.round < 3:
                        if st.button("Next Round", key=f"next_round_{st.session_state.round}"):
                            st.session_state.round += 1
                            st.session_state.human_argument = ""
                            st.session_state.ai_response = ""
                            st.rerun()
        else:
            if not st.session_state.ai_response:
                with st.spinner("AI arguing..."):
                    if st.session_state.round > 1:
                        key_points = extract_key_points(st.session_state.debate_transcript.split('\n\n')[-2])
                        ai_argument = generate_argument(
                            st.session_state.situation,
                            "in favor of",
                            f"Directly challenge and contradict these points from your opponent:\n{key_points}\n\nFull debate:\n{st.session_state.debate_transcript}"
                        )
                    else:
                        ai_argument = generate_argument(st.session_state.situation, "in favor of",
                                                        st.session_state.debate_transcript)
                st.session_state.ai_response = ai_argument
                st.session_state.debate_transcript += f"AI: {ai_argument}\n\n"
                st.rerun()
            else:
                st.write("AI:", st.session_state.ai_response)
                if not st.session_state.human_argument:
                    human_argument = st.text_area(f"Your argument (Against):")
                    if st.button("Submit", key=f"submit_human_{st.session_state.round}"):
                        st.session_state.human_argument = human_argument
                        st.session_state.debate_transcript += f"Human: {human_argument}\n\n"
                        st.rerun()
                else:
                    st.write("Human:", st.session_state.human_argument)
                    if st.session_state.round < 3:
                        if st.button("Next Round", key=f"next_round_{st.session_state.round}"):
                            st.session_state.round += 1
                            st.session_state.human_argument = ""
                            st.session_state.ai_response = ""
                            st.rerun()

    elif st.session_state.debate_type == "Human vs Human":
        st.write("This mode is under development.")
        if st.button("Start New Debate"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


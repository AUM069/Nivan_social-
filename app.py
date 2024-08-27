import streamlit as st
import groq
import time

# Set up Groq client (replace with your actual API key)
client = groq.Client(api_key="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")

def extract_key_points(argument):
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Extract 2-3 key points from the given argument."},
            {"role": "user", "content": argument}
        ],
        model="llama-3.1-70b-versatile",
        max_tokens=100
    )
    return response.choices[0].message.content

def generate_argument(prompt, stance, previous_arguments=""):
    response = client.chat.completions.create(
        messages=[
            {"role": "system",
             "content": f"You are an aggressive debater. Strongly argue {stance} the given situation, directly challenging and contradicting your opponent's points. Be confrontational and pick apart their arguments."},
            {"role": "user", "content": f"Situation: {prompt}\n\nPrevious arguments:\n{previous_arguments}"}
        ],
        model="llama-3.1-70b-versatile",
        max_tokens=200
    )
    return response.choices[0].message.content

def determine_winner_and_summarize(prompt, debate_transcript):
    winner_response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Determine the winner of the debate based on the strength of arguments."},
            {"role": "user", "content": f"Situation: {prompt}\n\nDebate transcript:\n{debate_transcript}"}
        ],
        model="llama-3.1-70b-versatile",
        max_tokens=50
    )
    winner = winner_response.choices[0].message.content

    summary_response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Provide 2-3 key points summarizing the debate."},
            {"role": "user", "content": f"Situation: {prompt}\n\nDebate transcript:\n{debate_transcript}"}
        ],
        model="llama-3.1-70b-versatile",
        max_tokens=200
    )
    summary = summary_response.choices[0].message.content

    return f"Winner: {winner}\n\n{summary}"

def check_truncation(text):
    if text.endswith((".", "!", "?")):
        return text
    return text + " [Response may be truncated]"

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
            st.write(check_truncation(result))

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
                        if st.session_state.round < 3:
                            st.session_state.round += 1
                            st.session_state.ai_response = ""
                            st.rerun()
                        else:
                            st.rerun()

        if st.session_state.round > 3:
            st.subheader("Debate Result and Key Points:")
            with st.spinner("Determining winner and summarizing..."):
                result = determine_winner_and_summarize(st.session_state.situation, st.session_state.debate_transcript)
            st.write(check_truncation(result))

            if st.button("Start New Debate"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

    elif st.session_state.debate_type == "Human vs Human":
        if st.session_state.round <= 3:
            human_a_argument = st.text_area(f"Round {st.session_state.round}: Human A argument:")
            human_b_argument = st.text_area(f"Round {st.session_state.round}: Human B argument:")
            if st.button("Submit Round", key=f"submit_round_{st.session_state.round}"):
                st.session_state.debate_transcript += f"Human A: {human_a_argument}\n\n"
                st.session_state.debate_transcript += f"Human B: {human_b_argument}\n\n"
                st.session_state.round += 1
                st.rerun()
        else:
            st.subheader("Debate Result and Key Points:")
            with st.spinner("Determining winner and summarizing..."):
                result = determine_winner_and_summarize(st.session_state.situation, st.session_state.debate_transcript)
            st.write(check_truncation(result))

            if st.button("Start New Debate"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()


import streamlit as st
import requests



st.set_page_config(
    page_title="AI Support Ticket Assistant",
    layout="centered"
)


API_URL = "http://127.0.0.1:8000/ask"




st.title("AI Support Ticket Assistant")

st.write(
    "Ask questions about customer support tickets "
    "using natural language."
)



if "messages" not in st.session_state:

    st.session_state.messages = []



for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


question = st.chat_input(
    "Ask something about the support tickets..."
)



if question:

    # ----------------------------------------------
    # Display user message
    # ----------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    # ----------------------------------------------
    # Call FastAPI
    # ----------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Analyzing tickets..."):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "question": question
                    },
                    timeout=60
                )

                # ----------------------------------
                # Successful response
                # ----------------------------------

                if response.status_code == 200:

                    data = response.json()

                    result = data["result"]

                    # ------------------------------
                    # Display result
                    # ------------------------------

                    if isinstance(result, int):

                        answer = f"**{result} tickets**"

                        st.markdown(answer)

                    elif isinstance(result, float):

                        answer = f"**{result:.2f}**"

                        st.markdown(answer)

                    elif isinstance(result, dict):

                        st.json(result)

                        answer = str(result)

                    elif isinstance(result, list):

                        answer = (
                            f"Found **{len(result)} tickets**."
                        )

                        st.markdown(answer)

                        st.dataframe(
                            result,
                            use_container_width=True
                        )

                    else:

                        answer = str(result)

                        st.markdown(answer)

                    # ------------------------------
                    # Save assistant response
                    # ------------------------------

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                # ----------------------------------
                # API error
                # ----------------------------------

                else:

                    error = response.json()

                    message = error.get(
                        "detail",
                        "Something went wrong."
                    )

                    st.error(message)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": message
                        }
                    )

            # --------------------------------------
            # Connection error
            # --------------------------------------

            except requests.exceptions.ConnectionError:

                message = (
                    "Cannot connect to the FastAPI server. "
                    "Please make sure FastAPI is running."
                )

                st.error(message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": message
                    }
                )

            # --------------------------------------
            # Other errors
            # --------------------------------------

            except Exception as e:

                message = f"Error: {str(e)}"

                st.error(message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": message
                    }
                )
import streamlit as st
import openai
import spacy
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# OpenAI API key
openai.api_key = ""  # Replace with your actual OpenAI API key

def extract_key_terms(text):
    """Extract key terms using Named Entity Recognition (NER)."""
    doc = nlp(text)
    return ", ".join([ent.text for ent in doc.ents])

def generate_mcq(text):
    """Generate an MCQ from input text using OpenAI API."""
    prompt = f"""Generate a multiple-choice question with four answer choices and the correct answer from the following text:
    \n{text}\n
    Format the response strictly as follows:
    Question: <question text>
    Options:
    A) <option 1>
    B) <option 2>
    C) <option 3>
    D) <option 4>
    Answer: <correct option letter (A/B/C/D)>"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI that generates multiple-choice questions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )

    mcq_text = response["choices"][0]["message"]["content"]

    match = re.match(r"Question:\s*(.*?)\nOptions:\s*A\)\s*(.*?)\nB\)\s*(.*?)\nC\)\s*(.*?)\nD\)\s*(.*?)\nAnswer:\s*([ABCD])", mcq_text, re.DOTALL)

    if match:
        question = match.group(1).strip()
        options = {
            "A": match.group(2).strip(),
            "B": match.group(3).strip(),
            "C": match.group(4).strip(),
            "D": match.group(5).strip()
        }
        correct_option = match.group(6).strip()
    else:
        question = "Could not extract question properly."
        options = {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}
        correct_option = "A"

    return question, options, correct_option

def check_answer(user_answer, correct_answer):
    """Check if user's answer is correct."""
    if user_answer == correct_answer:
        return "✅ Correct!"
    else:
        return f"❌ Incorrect! The correct answer is {correct_answer}."

# Streamlit UI
st.title("🧠 AI-Powered Quiz Generator")
st.write("Enter a paragraph of text below, and this app will generate a multiple-choice question (MCQ) for you.")

text_input = st.text_area("Enter a paragraph of text")

if st.button("Generate MCQ"):
    if text_input.strip() == "":
        st.warning("Please enter some text.")
    else:
        key_terms = extract_key_terms(text_input)
        question, options, correct_option = generate_mcq(text_input)

        st.subheader("Key Terms Identified")
        st.info(key_terms if key_terms else "No key terms found.")

        st.subheader("Generated Question")
        st.write(question)

        selected_option = st.radio("Choose your answer", list(options.items()), format_func=lambda x: f"{x[0]}) {x[1]}", key="mcq")

        if st.button("Check Answer"):
            result = check_answer(selected_option[0], correct_option)
            st.success(result if "✅" in result else result)

# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import fitz  # PyMuPDF
from difflib import SequenceMatcher

# Import sumy for text summarization
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

app = Flask(__name__)
app.secret_key = 'dkfdfkemkrekdf'

# Function to extract text from a PDF
def get_pdf_text(pdf_file):
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype='pdf')
    for page in doc:
        text += page.get_text()
    return text

# Function to compare two PDFs and generate summaries
def get_similar_content(text1, text2):
    # Use SequenceMatcher to get the matching blocks
    matcher = SequenceMatcher(None, text1, text2)
    matching_blocks = matcher.get_matching_blocks()

    similar_content = []

    for match in matching_blocks:
        start_idx = match.a
        end_idx = match.a + match.size
        similar_content.append(text1[start_idx:end_idx])

    return similar_content

# Function to compare two PDFs and generate summaries
def compare_pdfs(pdf1, pdf2):
    text1 = get_pdf_text(pdf1)
    text2 = get_pdf_text(pdf2)
    similarity_percentage = round(100 * SequenceMatcher(None, text1, text2).ratio(), 2)

    similar_content = get_similar_content(text1, text2)

    # Generate summaries for the two PDFs using sumy
    parser1 = PlaintextParser.from_string(text1, Tokenizer("english"))
    summarizer1 = LsaSummarizer()
    summary1 = summarizer1(parser1.document, 3)  # Adjust the number of sentences in the summary

    parser2 = PlaintextParser.from_string(text2, Tokenizer("english"))
    summarizer2 = LsaSummarizer()
    summary2 = summarizer2(parser2.document, 3)  # Adjust the number of sentences in the summary

    # Generate summary for similar content
    parser_similar_content = PlaintextParser.from_string('\n'.join(similar_content), Tokenizer("english"))
    summarizer_similar_content = LsaSummarizer()
    summary_similar_content = summarizer_similar_content(parser_similar_content.document, 3)  # Adjust the number of sentences in the summary

    # Convert the summaries to a string
    summary1_text = "\n".join([str(sentence) for sentence in summary1])
    summary2_text = "\n".join([str(sentence) for sentence in summary2])
    summary_similar_content_text = "\n".join([str(sentence) for sentence in summary_similar_content])

    return text1, text2, similarity_percentage, summary1_text, summary2_text, similar_content, summary_similar_content_text

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for comparing PDFs
@app.route('/compare', methods=['POST'])
def compare():
    if 'pdf1' in request.files and 'pdf2' in request.files:
        pdf1 = request.files['pdf1']
        pdf2 = request.files['pdf2']

        if pdf1.filename and pdf2.filename:
            text1, text2, similarity_percentage, summary1, summary2, similar_content, summary_similar_content = compare_pdfs(pdf1, pdf2)
            return render_template('result.html', text1=text1, text2=text2, similarity_percentage=similarity_percentage, summary1=summary1, summary2=summary2, similar_content=similar_content, summary_similar_content=summary_similar_content)
        else:
            flash('Please select two PDF files for comparison.')
            return redirect(url_for('index'))

    return "File upload failed."

if __name__ == '__main__':
    app.run(debug=False)

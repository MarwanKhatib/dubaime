from flask import Flask, send_from_directory, render_template, request
import os
import sqlite3

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                            'favicon.ico', mimetype='image/vnd.microsoft.icon')

def get_faqs(language):
    conn = sqlite3.connect('faqs.db')
    c = conn.cursor()
    c.execute('SELECT question, answer FROM faqs WHERE language = ?', (language,))
    faqs = c.fetchall()
    conn.close()
    return faqs

def boolean_search(query, faqs):
    results = []
    query_lower = query.lower()
    for question, answer in faqs:
        if query_lower in question.lower() or query_lower in answer.lower():
            results.append((question, answer))
    return results

def extend_boolean_search(query, faqs):
    results = []
    query_terms = query.lower().split()
    for question, answer in faqs:
        if any(term in question.lower() for term in query_terms) or any(term in answer.lower() for term in query_terms):
            results.append((question, answer))
    return results

def vector_search(query, faqs):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    documents = [question + ' ' + answer for question, answer in faqs]
    documents.append(query)

    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()

    query_vector = vectors[-1].reshape(1, -1)
    faqs_vectors = vectors[:-1]

    cosine_similarities = cosine_similarity(query_vector, faqs_vectors)
    similar_indices = cosine_similarities[0].argsort()[:-6:-1]

    results = [(faqs[i][0], faqs[i][1]) for i in similar_indices]
    return results

@app.route('/')
def search():
    return render_template('search.html')

@app.route('/results', methods=['POST'])
def results():
    query = request.form['query']
    language = request.form['language']
    model = request.form['model']
    
    faqs = get_faqs(language)
    if not faqs:
        return render_template('results.html', query=query, results=[("No FAQs found", "")])
    
    if model == 'boolean':
        results = boolean_search(query, faqs)
    elif model == 'extended_boolean':
        results = extend_boolean_search(query, faqs)
    elif model == 'vector':
        results = vector_search(query, faqs)
    else:
        results = [("Model not supported", "")]
    
    if not results:
        results = [("No results found for the given query", "")]
    
    return render_template('results.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=False)

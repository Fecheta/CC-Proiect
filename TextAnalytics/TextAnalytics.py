from TextAnalytics.credentials import client

client = client()


def reviews(description):
    result = []
    documents = [description]
    response = client.analyze_sentiment(
        documents=documents,
        language='en-US',
        show_opinion_mining=True
    )

    doc = response[0]

    # doc.id
    # doc.sentiment
    # doc.confidence_scores.positive

    positive_reviews = [doc for doc in response if doc.sentiment == 'positive']
    mixed_reviews = [doc for doc in response if doc.sentiment == 'mixed']
    negative_reviews = [doc for doc in response if doc.sentiment == 'negative']

    for document in response:
        result.append('Sentiment Analysis Outcome: {0}'.format(document.sentiment))
        result.append('Overall score: positive = {0:.2f}; neutral{1:.2f}; negative={2:.2f}'.format(
            document.confidence_scores.positive,
            document.confidence_scores.neutral,
            document.confidence_scores.negative
        ))
        result.append('-' * 75)

        sentences = doc.sentences
        for index, sentence in enumerate(sentences):
            result.append('Sentence #{0}'.format(index + 1))
            result.append('Sentence Text: {0}'.format(sentence.text))
            result.append('Sentence score: positive = {0:.2f}; neutral{1:.2f}; negative={2:.2f}'.format(
                sentence.confidence_scores.positive,
                sentence.confidence_scores.neutral,
                sentence.confidence_scores.negative
            ))
    return result

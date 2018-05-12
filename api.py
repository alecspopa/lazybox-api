from flask import Flask, request, jsonify

from google.cloud import translate
import dialogflow
import random

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/intent", methods=['GET', 'POST'])
def intent():
    if request.method == 'POST':
        text_en = translate_text(request.form['text'])
        intent = detect_intent('lazybox-5fc02', 'sess1', text_en, 'en')

        return jsonify(intent)
    else:
        if round(random.uniform(0, 1)) == 1:
            return 'kitchen|d4|on'
        else:
            return 'kitchen|d4|off'
        # intent_to_device_string(intent)


def translate_text(text):
    # Instantiates a client
    translate_client = translate.Client()

    # The text to translate
    target = 'en'

    # Translates some text into English
    translation = translate_client.translate(
        text,
        target_language=target)

    print('Text: {}'.format(text))
    print('Translation: {}'.format(translation['translatedText']))

    return translation['translatedText']


def detect_intent(project_id, session_id, text, language_code):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversaion."""
    dialogflow_client = dialogflow.SessionsClient()

    session = dialogflow_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session))

    text_input = dialogflow.types.TextInput(
        text=text, language_code=language_code)

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = dialogflow_client.detect_intent(
        session=session, query_input=query_input)

    print('=' * 20)
    print('Query text: {}'.format(response.query_result.query_text))
    print('Detected intent: {} (confidence: {})\n'.format(
        response.query_result.intent.display_name,
        response.query_result.intent_detection_confidence))
    print('Fulfillment text: {}\n'.format(
        response.query_result.fulfillment_text))

    parameters = []
    for key, value in response.query_result.parameters.items():
        parameters.append({
            'key': key,
            'value': value
        })

    intent = {
        'action': response.query_result.action,
        'intent_detection_confidence': response.query_result.intent_detection_confidence,
        'language_code': response.query_result.language_code,
        'parameters': parameters
    }

    return intent


def intent_to_device_string(intent):
    action = []

    # add room info
    for param in intent['parameters']:
        if param['key'] == 'room':
            action.append(param['value'])

    # add pin and action info
    if intent['action'] == 'smarthome.lights.switch.on':
        action.append('d4')
        action.append('on')
    elif intent['action'] == 'smarthome.lights.switch.off':
        action.append('d4')
        action.append('off')

    return '|'.join(action)
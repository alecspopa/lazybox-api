import os
import dialogflow
import http
import re
import firebase_admin

from firebase_admin import db
from google.cloud import translate

from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
cors = CORS(app, resources={"*": {"origins": "*"}})


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/intent", methods=['GET', 'POST'])
def intent():
    state_db = StateDB()

    if request.method == 'POST':
        payload = request.get_json()

        text_en = translate_text(payload['text'])
        intent = detect_intent('lazybox-5fc02', 'sess1', text_en, 'en')

        state_db.push(intent)

        return jsonify(intent)
    else:
        latest_state = state_db.pop()

        if latest_state is None:
            return '', http.HTTPStatus.NO_CONTENT

        return latest_state


@app.route("/intent/delete")
def intent_delete():
    state_db = StateDB()
    state_db.pop_delete()

    return '', http.HTTPStatus.NO_CONTENT


class StateDB:
    class __StateDB:
        def __init__(self):
            firebase_admin.initialize_app(None, {
                'databaseURL': os.environ['FIREBASE_DATABASE_URL']
            })

            self.db_ref = db.reference('states')

    instance = None

    def __init__(self):
        if not StateDB.instance:
            StateDB.instance = StateDB.__StateDB()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def push(self, intent):
        device_state = self.__intent_to_device_state(intent)

        print('-' * 20)
        print(device_state)
        print('-' * 20)

        if device_state is not '':
            self.db_ref.push(device_state)

    def pop(self):
        latest_state = None

        # pop from stack latest state
        snapshot = self.db_ref.order_by_key().limit_to_first(1).get()

        if not snapshot:
            return latest_state

        for key, val in snapshot.items():
            latest_state = val

        return latest_state

    def pop_delete(self):
        # pop from stack latest state
        snapshot = self.db_ref.order_by_key().limit_to_first(1).get()

        if snapshot:
            for key in snapshot:
                del_ref = db.reference('states/' + key)
                del_ref.delete()

    @staticmethod
    def __intent_to_device_state(intent):
        action = []

        # add room info
        for param in intent['parameters']:
            if param['key'] == 'room':
                action.append(param['value'])

        intent_triggers = get_intent_triggers(intent['action'])

        if intent_triggers is not None:
            action.append(intent_triggers['device'])
            action.append(intent_triggers['toggle_action'])

        return '|'.join(action)


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

    intent_triggers = get_intent_triggers(response.query_result.action)
    voice_action = get_voice_action(intent_triggers)

    intent = {
        'action': response.query_result.action,
        'intent_detection_confidence': response.query_result.intent_detection_confidence,
        'language_code': response.query_result.language_code,
        'parameters': parameters,
        'voice_action': voice_action
    }

    return intent


def get_intent_triggers(action):
    pattern = re.compile('smarthome\.([a-z]*)\.switch\.([a-z]*)')
    matches = pattern.match(action)

    intent_triggers = None

    if matches:
        intent_triggers = {
            'device': matches.group(1),
            'toggle_action': matches.group(2)
        }

    return intent_triggers


def get_voice_action(intent_triggers):
    voice_action = ''

    if intent_triggers is not None:
        if intent_triggers['device'] == 'lights' and intent_triggers['toggle_action'] == 'on':
            voice_action = 'Am aprins lumina!'
        if intent_triggers['device'] == 'lights' and intent_triggers['toggle_action'] == 'off':
            voice_action = 'Am stins lumina!'

    return voice_action


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
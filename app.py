import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template
from flask_bootstrap import Bootstrap
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


from python.helpers.print_style import PrintStyle
from agent import Agent, AgentConfig
import models

app = Flask(__name__)
Bootstrap(app)

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == os.environ['APP_USERNAME'] and \
            check_password_hash(os.environ['APP_USERPASS'], password):
        return username


# Initialize Agent Zero
def initialize_agent():
    chat_llm = models.get_openai_chat(temperature=0)
    utility_llm = models.get_openai_chat(temperature=0)
    embedding_llm = models.get_embedding_openai()

    config = AgentConfig(
        chat_model=chat_llm,
        utility_model=utility_llm,
        embeddings_model=embedding_llm,
        code_exec_docker_enabled=False,
        code_exec_ssh_enabled=False,
    )

    agent = Agent(number=0, config=config)
    return agent

agent = initialize_agent()


@app.route('/chat', methods=['POST'])
@auth.login_required
def chat():
    user_input = request.json.get('question')
    if user_input:
        PrintStyle(font_color="white", padding=False, log_only=True).print(f"> {user_input}")
        response = agent.message_loop(user_input)
    answer = ""
    if PrintStyle.log_file_path:
        with open(PrintStyle.log_file_path) as filep:
            answer = filep.read()
    return jsonify({'output': answer})


@app.route('/output', methods=['POST'])
def get_output():
    output = ""
    if PrintStyle.log_file_path:
        with open(PrintStyle.log_file_path) as filep:
            output = filep.read()
    return jsonify({'output': output})

@app.route('/', methods=['GET'])
@auth.login_required

def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


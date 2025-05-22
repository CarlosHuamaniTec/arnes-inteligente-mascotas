from flask import Flask, request
from celery import Celery

app = Flask(__name__)
celery = Celery('ai', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    # Enviar tarea a Celery
    task = celery.send_task('tasks.run_ai_analysis', args=[data])
    return {'task_id': task.id}
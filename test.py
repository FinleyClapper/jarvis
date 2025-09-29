import ollama
import subprocess

# Ask Ollama a simple question
response = ollama.chat(
    model='llama3',
    messages=[{'role': 'user', 'content': 'Hello!'}]
)
print("Ollama response:", response['message']['content'])

# Check GPU usage (NVIDIA)
try:
    output = subprocess.check_output(['nvidia-smi'], encoding='utf-8')
    print("GPU status:\n", output)
except FileNotFoundError:
    print("nvidia-smi not found. Are you using an NVIDIA GPU?")
except subprocess.CalledProcessError as e:
    print("Error checking GPU:", e)

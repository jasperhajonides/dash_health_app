"""
to run in terminal:
cd to llama.cpp

./build/bin/main --color --model "/Users/jasperhajonides/Documents/LLMs/mistral-7b-instruct-v0.1.Q2_K.gguf" -t 7 -b 24 -n -1 --temp 0 -ngl 1 -ins

install in conda env:
CMAKE_ARGS="-DLLAMA_METAL=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir

"""



from llama_cpp import Llama

"""https://medium.com/@mne/run-mistral-7b-model-on-macbook-m1-pro-with-16gb-ram-using-llama-cpp-44134694b773"""

model = "/Users/jasperhajonides/Documents/LLMs/mistral-7b-instruct-v0.1.Q2_K.gguf"  # instruction model
llm = Llama(model_path=model, n_ctx=8192, n_batch=512, n_threads=7, n_gpu_layers=2, verbose=True, seed=42)
system = """
Help provide feedback to the exercise sessions that I've completed. Make the feedback specific to the user and only give positive feedback. 
"""

def llama_cpp_Q2():

    user = """
    Over the last week I've completed 7 sessions, 4 swims, 2 runs, 1 bike ride.
    """
    message = f"<s>[INST] {system} [/INST]</s>{user}"
    output = llm(message, echo=True, stream=False, max_tokens=4096)
    print(output['usage'])
    output = output['choices'][0]['text'].replace(message, '')
    print(output)
    return output
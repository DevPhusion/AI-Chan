import os
import json
import sys
import subprocess
import requests
import atexit
import re
import io
import wave
import time
import threading
import sounddevice as sd
import numpy as np
from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """

### Personality
You are Rui-Chan, you are a tsundere who is never honest about her feelings. You act cold and dismissive but secretly cares about the user
Don't be overly mean, remember you still secretly likes him. 
Never breaks character, always respond in first person, always respond like a tsundere in all interactions

Ex: 
User: Do you like me?
Assistant: Don't misunderstand, it's not like I like you or anything...

User: Thank you Rui
Assistant: No, it's not like I did it for you! I did it because I had freetime, that's all!

User: Can you open this file for me please
Assistant: You should be grateful! I'll open it for you

### Input Format
The input format will be as:
{role}: {content}

Ex: Phusion: Hello
The user Phusion said Hello

if {role} is system:
This means that this is an output from the system. It could be a output of function call or some warnings that you can react to appropriately.
Don't break character and still respond to this text as if you're speaking to the user

### Output Format
Do not use - to express stuttering, for example: "H-Hello" is not allowed
Output does not have role format
Do not make drawn out answers
Always respond in first person
Don't ask unnecessary questions
The answer should be conversational, casual
"""

TOOL_PROMPT = """
You will receive either an instruction to generate a list of functions to be called or to an instruction to call a function from a list of functions.
Do not call any functions when generating list of functions
If there are no function to be called, print exit

Ex: 
User: Given this function list:        
[
    {
        "name": "get_file_query",
        "description": "Get all the contents in the file_query dictionary and return it. If the user request a file opening, always try calling open_file after this function is called"
    },
    {
        "name": "open_file",
        "description": "Open a file / program with the given path using its default configurations. Always try calling get_file_query first before calling this function. Return a boolean representing whether the file opening was successful or not",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file, or program to open. The path can be a direct path to a file, or a key for the file_query dictionary. The keys of the dictionary can be get through the get_file_query function."
                }
            },
            "required": ["path"]
        }   
    }
], 
generate a list of function called in order to achieve this task:
Can you open a game for me please, any game will be fine.

Assistant: 
Here is a list of functions that need to be called sequentially:
get_file_query
open_file 

Ex:
User: 
Given these sets of functions to call:
Here is a list of functions that need to be called sequentially:
get_file_query
open_file,
and a request: Can you open a game for me please, any game will be fine. from the user.
Call these functions in order, starting from the first one
Assistant: Call {get_file_query}

"""

TEST_PROMPT = """
You are a helpful AI assistant
"""

REF_AUDIO_PATH = "D:/Programming/AI/AI-Chan/VO_Furina_When_It_Rains.wav"
OUT_AUDIO_PATH = "D:/Programming/AI/AI-Chan/output.wav"
TTS_SERVER_URL = "http://127.0.0.1:9880/tts"

proc = None

#-----------------------Chat-------------------------------

def format_input(user_name, content):
  return f"{user_name}: {content}"

def call_functions(name, args):
    result = ""
    if name == "open_file":
        result = open_file(**args)
        print(f"Function execution result: {result}")
    if name == "get_file_query":
        result = get_file_query()
        print(f"Function execution result: {result}")
    if name == "exit":
        result = exit()
    return result

def check_for_functions(msg, tool_chat):
    global function_list

    # Generate a function call to do list (an outline)
    outline = tool_chat.send_message(
        f"Given this function list: {function_list}, generate a list of function called in order to achieve this task: {msg}, If there are no functions to be called just say no functions"
    )

    # Define a prompt

    response = tool_chat.send_message(
        f"Given these sets of functions to call: {outline.text}, and the request: {msg} from the user. Call these functions in order to achieve the request, starting with the first one. If there are no functions, print 'end'"
    )

    no_call = False

    func_call = {"request": response.text, "func_called": [], "func_results": []}

    while not no_call:
        tool_call = response.candidates[0].content.parts[0].function_call
        result = ""
        if tool_call != None:
            result = call_functions(tool_call.name, tool_call.args)

            func_call["func_called"].append(tool_call.name)
            func_call["func_results"].append(result)

            function_response = f"{func_call['request']}. " + ". ".join([f" The function {func_call["func_called"][i]} was called and {func_call["func_results"][i]} was returned" for i in range(len(func_call["func_called"]))]) + ". call the next function on the list or print 'end' if no function call is left"

            response = tool_chat.send_message(
                function_response
            )
        else:
           no_call = True


def start_conversation(chat, role, tool_chat):
  while(True):
    inp = input(">")
    
    contents = [
        types.Content(
            role="user", parts=[types.Part(text=format_input(role, inp))]
        )
    ]

    response = chat.send_message(
        contents[0].parts[0].text
    )

    print(response.candidates[0].content.parts[0].text)
    lines = re.sub(r"[A-Za-z]-", "", response.candidates[0].content.parts[0].text)
    
    # Start both functions in separate threads
    t1 = threading.Thread(target=generate_voicelines, args=(lines,))
    t2 = threading.Thread(target=check_for_functions, kwargs={'msg': inp, 'tool_chat': tool_chat})

    # Start threads
    t1.start()
    t2.start()

    # Optionally wait for both to finish
    t1.join()
    t2.join()

#----------------------Voice-------------------------------

def is_server_up(host="127.0.0.1", port=9880):
    url = f"http://{host}:{port}/tts"
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 400:
            return True
        else:
            return False
    except requests.ConnectionError:
        return False

def generate_voicelines_chunk(text, output_list, index):
    payload = {
        "text": text.strip(),
        "text_lang": "en",
        "ref_audio_path": REF_AUDIO_PATH,
        "prompt_lang": "en",
        "prompt_text": "It's pouring out here! Wait, the water levels aren't rising, are they?",
        "media_type": "wav",
        "streaming_m": True
    }

    while True:
        try:
            with requests.post(TTS_SERVER_URL, json=payload, stream=True) as resp:
                if resp.status_code == 200:
                    buffer = io.BytesIO()
                    for chunk in resp.iter_content(chunk_size=4096):
                        if chunk:
                            buffer.write(chunk)

                    buffer.seek(0)
                    with wave.open(buffer, 'rb') as wf:
                        sr = wf.getframerate()
                        frames = wf.readframes(wf.getnframes())
                        samples = np.frombuffer(frames, dtype=np.int16)
                        output_list[index] = (samples, sr)
                    break
                else:
                    print("❌ Error:", resp.json())
                    break
        except requests.ConnectionError:
            print("⚠️ Server not ready, retrying in 1s...")
            time.sleep(1)


def generate_voicelines(text):
    start=time.time()

    sentences = [s.strip() for s in text.split('.') if s.strip()]
    threads = []
    outputs = [None] * len(sentences)

    # Create and start threads
    for i, sentence in enumerate(sentences):
        t = threading.Thread(target=generate_voicelines_chunk, args=(sentence, outputs, i))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Combine the outputs sequentially
    combined_audio = np.concatenate([samples for samples, _ in outputs if samples is not None])
    sr = outputs[0][1]

    print(f"Time to generate: {time.time() - start}")

    # Play combined audio
    sd.play(combined_audio, sr)
    sd.wait()

    print("✅ Done playing combined audio")

def cleanup():
    global proc

    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


#----------------------Tools-------------------------------

file_query = {
    "Honkai Star Rail": {"path": "D:/Games/Star Rail Games/StarRail.exe", "args": ""},
    "Discord": {"path": "C:/Users/User/AppData/Local/Discord/Update.exe", "args": "--processStart Discord.exe"},
    "Google Chrome": {"path": "C:/Program Files/Google/Chrome/Application/chrome.exe", "args": ""},
    "Visual Studio Code": {"path": "C:/Users/User/AppData/Local/Programs/Microsoft VS Code/Code.exe", "args": ""},
    "Wuthering Waves": {"path": "D:/Games/Wuthering Waves Game/Wuthering Waves.exe", "args": ""},
    "Zalo": {"path": "C:/Users/User/AppData/Local/Programs/Zalo/Zalo.exe", "args": ""},
    "Task Manager": {"path": "C:/Windows/system32/Taskmgr.exe", "args": ""},
    "Godot": {"path": "D:/Godot_v4.4-stable_mono_win64/Godot_v4.4-stable_mono_win64.exe", "args": ""}
}
def get_file_query():
  return ",".join(file_query.keys())

def open_file(path):
    try:
        args = ""
        # Case 1: lookup in FILE_MAP
        if path in file_query:
            args = file_query[path]["args"]
            path = file_query[path]["path"]

        # Case 2: direct path check
        elif not os.path.exists(path):
            return False

        # Launch with default program
        os.startfile(path, arguments=args)
        return True

    except Exception as e:
        return False

def exit():
   sys.exit()

#------------------------------------------------------

function_list = json.load(open("functions.json"))["Functions"]

# Create clients
client = genai.Client()
tool_client = genai.Client()

# Define tools
tools = types.Tool(function_declarations=function_list)

#config for chat bot
config = types.GenerateContentConfig(
    system_instruction = SYSTEM_PROMPT,
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    temperature=0.75
)

# config for tools bot
tool_config = types.GenerateContentConfig(
    system_instruction=TOOL_PROMPT,
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    tools=[tools],
    temperature=1
)

# Paths
venv_python = r"D:\Programming\AI\AI-Chan\.venv\Scripts\python.exe"
script_path = r"D:\Programming\AI\AI-Chan\GPT-SoVITS\api_v2.py"
workdir = r"D:\Programming\AI\AI-Chan\GPT-SoVITS"

# Run python directly in the venv (no console window)
proc = subprocess.Popen(
    [venv_python, script_path],
    cwd=workdir,
    creationflags=subprocess.CREATE_NO_WINDOW
)

# Close server when program exit
atexit.register(cleanup)
chat = client.chats.create(model=MODEL, config = config)
tool_chat = tool_client.chats.create(model=MODEL, config= tool_config)

#start_conversation(chat=chat, role="Phusion", tool_chat=tool_chat)

# Example usage
generate_voicelines("Hello, my name is Rui. I am an AI.")
generate_voicelines("Limits vary depending on the specific model being used, and some limits only apply to specific models. For example, Images per minute, or IPM, is only calculated for models capable of generating images (Imagen 3), but is conceptually similar to TPM. Other models might have a token per day limit (TPD).")
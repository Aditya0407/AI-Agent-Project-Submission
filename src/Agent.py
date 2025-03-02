import os
import sounddevice as sd
from scipy.io.wavfile import write
from gtts import gTTS
from playsound import playsound
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import HuggingFacePipeline
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class ColdCallAgent:
    def __init__(self):
        self.llm = self._initialize_llm()
        self.memory = ConversationBufferMemory()
        self.scenario_templates = {
            "demo": self._demo_template(),
            "interview": self._interview_template(),
            "payment": self._payment_template()
        }
        
    def _initialize_llm(self):
        model_name = "sarvamai/openhathi-7b-hi-v0.1-base"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=256,
            temperature=0.7,
            repetition_penalty=1.2
        )
        
        return HuggingFacePipeline(pipeline=pipe)

    def _demo_template(self):
        return PromptTemplate(
            input_variables=["history", "input"],
            template="""
            You are an ERP sales agent. Speak in Hinglish. Goal: Schedule demo.
            History: {history}
            Customer: {input}
            Agent:"""
        )

    def _interview_template(self):
        return PromptTemplate(
            input_variables=["history", "input"],
            template="""
            You are HR interviewer. Speak Hinglish. Goal: Screen candidate.
            History: {history}
            Candidate: {input}
            Interviewer:"""
        )

    def _payment_template(self):
        return PromptTemplate(
            input_variables=["history", "input"],
            template="""
            You are payment collector. Speak Hinglish. Goal: Get payment.
            History: {history}
            Customer: {input}
            Agent:"""
        )

    def text_to_speech(self, text):
        try:
            tts = gTTS(text=text, lang='hi', slow=False)
            tts.save("response.mp3")
            playsound("response.mp3")
            os.remove("response.mp3")
        except Exception as e:
            print(f"TTS Error: {e}")

    def record_audio(self, duration=5, fs=16000):
        print("Recording...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        write("input.wav", fs, recording)
        return "input.wav"

    def transcribe_audio(self, filename):
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(filename)
        return result["text"]

    def handle_scenario(self, scenario):
        template = self.scenario_templates[scenario]
        conversation = ConversationChain(
            llm=self.llm,
            prompt=template,
            memory=self.memory
        )
        
        # Generate initial message
        if scenario == "demo":
            response = conversation.predict(input="Hello, I want to schedule a demo")
        elif scenario == "interview":
            response = conversation.predict(input="Start the interview")
        else:
            response = conversation.predict(input="Remind about payment")
            
        self.text_to_speech(response)
        
        while True:
            audio_file = self.record_audio()
            user_input = self.transcribe_audio(audio_file)
            
            if any(word in user_input.lower() for word in ["bye", "thank you", "later"]):
                break
                
            response = conversation.predict(input=user_input)
            self.text_to_speech(response)
            
        self.memory.clear()
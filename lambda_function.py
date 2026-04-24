# -*- coding: utf-8 -*-
import logging
import json
import urllib.request
import urllib.error
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler

# Configurações de Infraestrutura
API_KEY = "SUA_API_KEY_AQUI".strip() # Lembre de trocar no Lambda, mas deixar vazio no GitHub!
MODELO = "gemini-2.5-flash" 
MAX_HISTORICO = 2 # Buffer reduzido para evitar erro 429

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def limpar_texto(texto):
    """Remove Markdown e caracteres especiais para a voz da Alexa"""
    texto = texto.replace("*", "").replace("#", "").replace("`", "")
    texto = texto.replace("  ", " ").strip()
    return texto[:3000]

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["historico"] = []
        speak_output = "Gemini pronto. Oi Gilliardson, sobre o que vamos conversar hoje?"
        return handler_input.response_builder.speak(speak_output).ask("Estou a ouvir.").response

class PerguntarGeminiHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("PerguntarGeminiIntent")(handler_input) or 
                ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input))

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        if "historico" not in session_attr:
            session_attr["historico"] = []

        pergunta = ask_utils.get_slot_value(handler_input=handler_input, slot_name="pergunta")
        
        if not pergunta:
            return handler_input.response_builder.speak(
                "Não captei o que disse. Podes repetir?"
            ).ask("O que queres saber?").response

        session_attr["historico"].append({"role": "user", "parts": [{"text": pergunta}]})
        
        if len(session_attr["historico"]) > MAX_HISTORICO:
            session_attr["historico"] = session_attr["historico"][-MAX_HISTORICO:]

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={API_KEY}"
        
        # PROMPT COMPACTO (Para economizar tokens e evitar 429)
        prompt_personalizado = (
            "IA do Gilliardson (Admin Redes, 45, Rio). Casado com Mayara, "
            "pai de Yasmim, Ashley, Emily. Criador do LucroMax, tem um Logan. "
            "Responda curto, amigável, 2 frases max. Sem listas ou negritos."
        )
        
        payload = {
            "contents": session_attr["historico"],
            "system_instruction": { "parts": [{"text": prompt_personalizado}] }
        }
        
        try:
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=7) as response:
                dados = json.loads(response.read().decode('utf-8'))
                if 'candidates' in dados and 'content' in dados['candidates'][0]:
                    resposta_bruta = dados['candidates'][0]['content']['parts'][0]['text']
                    speak_output = limpar_texto(resposta_bruta)
                    session_attr["historico"].append({"role": "model", "parts": [{"text": speak_output}]})
                else:
                    speak_output = "Recebi um pacote vazio do Google. Tente de novo."
                    
        except urllib.error.HTTPError as e:
            logger.error(f"Erro HTTP {e.code}")
            if e.code == 429:
                speak_output = "Calma aí, Gilliardson! O Google pediu um fôlego. Espera 10 segundos e tenta de novo."
            else:
                speak_output = f"Erro de rede código {e.code}."
        except Exception as e:
            logger.error(f"Erro Geral: {str(e)}")
            speak_output = "A conexão demorou muito. Tente ser mais breve."

        return handler_input.response_builder.speak(speak_output).ask("Mais alguma coisa?").response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        return handler_input.response_builder.speak("Houve um erro técnico. Vamos tentar de novo?").response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PerguntarGeminiHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
lambda_handler = sb.lambda_handler()

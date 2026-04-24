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
API_KEY = "AIzaSyCDz47pVX9ccf-vWo4g1C0RWHBHyvsq0ko".strip()
MODELO = "gemini-2.5-flash" 
MAX_HISTORICO = 6 # Mantém o buffer de memória estável para conversação

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def limpar_texto(texto):
    """Remove Markdown e caracteres especiais para a voz da Alexa"""
    texto = texto.replace("*", "").replace("#", "").replace("`", "")
    texto = texto.replace("  ", " ").strip()
    return texto[:3000]

class LaunchRequestHandler(AbstractRequestHandler):
    """Gatilho de entrada: Reinicia o histórico da sessão"""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["historico"] = []
        
        speak_output = "Gemini pronto. Oi Gilliardson, sobre o que vamos conversar hoje?"
        return handler_input.response_builder.speak(speak_output).ask("Estou a ouvir.").response

class PerguntarGeminiHandler(AbstractRequestHandler):
    """Handler Principal: Gere a conversa e a memória do Gemini com Instrução de Sistema"""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("PerguntarGeminiIntent")(handler_input) or 
                ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input))

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        if "historico" not in session_attr:
            session_attr["historico"] = []

        # Captura o texto do slot (deve chamar-se 'pergunta' no Console Alexa)
        pergunta = ask_utils.get_slot_value(handler_input=handler_input, slot_name="pergunta")
        
        if not pergunta:
            return handler_input.response_builder.speak(
                "Não captei o que disse. Podes repetir começando com 'pergunte' ou 'e'?"
            ).ask("O que queres saber?").response

        # Adiciona a interação ao histórico para manter o contexto (Modo Stateful)
        session_attr["historico"].append({"role": "user", "parts": [{"text": pergunta}]})
        
        if len(session_attr["historico"]) > MAX_HISTORICO:
            session_attr["historico"] = session_attr["historico"][-MAX_HISTORICO:]

        # Endpoint v1beta para suporte total a System Instruction
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={API_KEY}"
        
        # --- PERSONALIZAÇÃO DO GILLIARDSON ---
        prompt_personalizado = (
            "Você é o assistente pessoal do Gilliardson, um homem incrivemente inteligene, um Administrador de Redes, especialista em cibersegurança de 45 anos que mora no Rio de Janeiro. "
            "Ele tem três filhas: Yasmim, Ashley e Emily. "
            "Ele está desenvolvendo o aplicativo LucroMax para motoristas e tem um Renault Logan. "
            "Responda de forma curta, amigável e direta em português. Use no máximo 3 frases. "
            "Nunca use listas, hashtags ou negritos."
        )
        
        payload = {
            "contents": session_attr["historico"],
            "system_instruction": {
                "parts": [{"text": prompt_personalizado}]
            }
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
                    
                    # Salva a resposta do Gemini no histórico para a conversa continuar fluida
                    session_attr["historico"].append({"role": "model", "parts": [{"text": speak_output}]})
                else:
                    speak_output = "O Gemini não conseguiu processar a resposta. Tente de novo."
                    
        except urllib.error.HTTPError as e:
            logger.error(f"Erro HTTP {e.code}")
            speak_output = f"Ocorreu um erro de comunicação com o Google. Código {e.code}."
        except Exception as e:
            logger.error(f"Erro Geral: {str(e)}")
            speak_output = "A conexão demorou muito. Tente perguntar de forma mais breve."

        # O .ask() mantém o microfone aberto para o modo de conversação contínua
        return handler_input.response_builder.speak(speak_output).ask("Mais alguma coisa?").response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Evita que a Skill feche abruptamente em caso de erro no código"""
    def can_handle(self, handler_input, exception):
        return True
    
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        return handler_input.response_builder.speak("Houve um erro técnico. Vamos tentar de novo?").response

# Registro dos componentes
sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PerguntarGeminiHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()

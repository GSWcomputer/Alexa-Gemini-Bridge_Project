# 🚀 Alexa-Gemini-Bridge: Conversational AI with Stateful Memory
<img width="2816" height="1536" alt="Gemini_Generated_Image_a8jndaa8jndaa8jn" src="https://github.com/user-attachments/assets/04159e1a-2208-4088-8102-e33ef19608fc" />

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Alexa](https://img.shields.io/badge/Alexa-blue?style=for-the-badge&logo=amazonalexa&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-orange?style=for-the-badge&logo=google&logoColor=white)

Este projeto integra o poder do modelo **Google Gemini 2.5 Flash** à linha Amazon Echo (Alexa), transformando uma assistente baseada em comandos em uma IA conversacional com memória de contexto e personalidade customizada.

### 🎯 Por que este projeto é diferente?
Diferente das Skills básicas de "pergunta e resposta", este projeto implementa um **Stateful Buffer** que permite conversas fluidas. A Alexa "lembra" do que foi dito anteriormente na sessão, permitindo diálogos complexos sem a necessidade de repetir o contexto a cada frase.

---

## 🛠️ Arquitetura e Stack Técnica

* **Backend:** AWS Lambda (Python 3.12).
* **LLM:** Google Gemini API (Model: `gemini-2.5-flash`).
* **SDK:** `ask-sdk-core` (Alexa Skills Kit para Python).
* **Comunicação:** Chamadas REST via `urllib` com tratamento rigoroso de HTTP Errors (429, 404, 400).
* **Estado:** Implementação de `Session Attributes` para gestão de histórico (Memory Context).

### ⚡ Destaques Técnicos

* **Sanitização de Markdown:** Filtro em Python para converter as respostas ricas do Gemini em texto puro compatível com o motor de voz da Alexa.
* **System Instructions:** Injeção de contexto em nível de sistema para garantir que a IA mantenha a personalidade e limites de tokens (max 3 frases), evitando *timeouts*.
* **Memory Management:** Buffer FIFO (First-In, First-Out) para o histórico, respeitando o limite de MTU (24KB) das sessões da Alexa.

---

## 🚀 Funcionalidades

* **[LIVE MODE]** Conversação contínua mantendo o microfone ativo via `.ask()`.
* **[CONTEXT AWARE]** Reconhecimento de contexto (Ex: "Quem é o dono da casa?" seguido de "Quantos anos ele tem?").
* **[PERSONALIZAÇÃO]** Perfil customizado via `system_instruction` para reconhecimento de usuários específicos.
* **[ERROR RESILIENCE]** Tratamento de falhas de rede e cota de API com respostas amigáveis.

---

## 📦 Como Instalar

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/GSWcomputer/alexa-gemini-bridge.git
    ```

2.  **Configuração do Google AI Studio:**
    * Obtenha sua API KEY no [Google AI Studio](https://aistudio.google.com/).
    * Certifique-se de habilitar o modelo `gemini-2.5-flash`.

3.  **Configuração da Alexa Skill:**
    * Crie uma nova Skill no [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask).
    * Use o tipo de slot `AMAZON.SearchQuery` para o slot chamado `pergunta`.
    * Adicione *Carrier Phrases* (âncoras) como "pergunte", "fale", "e", "sobre".

4.  **Deploy no Lambda:**
    * O código principal está localizado em `lambda_function.py`.
    * Configure a variável `API_KEY` com sua chave secreta.

---

## 🛠️ Troubleshooting Log: Desafios e Soluções

Documentação dos desafios superados durante a integração entre Amazon e Google:

### 🔴 Erro 429: Too Many Requests (Rate Limit)
* **Sintoma:** Falha de conexão após as primeiras perguntas.
* **Causa:** Cota restrita de RPM no modelo inicial.
* **Solução:** Migração para o modelo **Gemini 2.5 Flash** e implementação de `timeout` de 7s no código Python.

### 🟠 Erro 404: Not Found (Endpoint Mismatch)
* **Sintoma:** Erro de "Recurso não encontrado" ao disparar o payload.
* **Causa:** Incompatibilidade entre a versão da API (`v1` vs `v1beta`) para uso de `system_instruction`.
* **Solução:** Atualização da URL de requisição para o endpoint `v1beta` e sanitização da `API_KEY` com `.strip()`.

### 🟡 Erro: 'NoneType' object has no attribute 'get'
* **Sintoma:** O código quebrava quando a Alexa não entendia a fala.
* **Causa:** Tentativa de acessar o slot `pergunta` quando ele vinha nulo.
* **Solução:** Implementação de lógica de verificação de integridade do pacote no Handler.

---

## 🤝 Contribuições
Sinta-se à vontade para abrir Issues ou enviar Pull Requests:
* Integração com DynamoDB para memória persistente.
* Suporte a SSML para entonação de voz.

## 📄 Licença
Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---
<table>
  <tr>
    <td width="150px"><img src="https://github.com/GSWcomputer.png" width="100px;" alt="Gilliardson"/></td>
    <td>
      <strong>Gilliardson</strong><br>
      Administrador de Redes, Especialista em Cybersecurity & Desenvolvedor Python. <br>
      Com sólida experiência em infraestrutura de missão crítica (BGP, MikroTik, Huawei e Cisco). Baseado no Rio de Janeiro, utiliza sua expertise técnica para explorar as fronteiras da Inteligência Artificial e Automação. É o desenvolvedor por trás do projeto **LucroMax** e entusiasta de soluções que unem hardware e software para resolver problemas do cotidiano.

📫 **Conecte-se comigo:**
* [LinkedIn] https://bit.ly/gilliardson-swy
    </td>
  </tr>
</table>

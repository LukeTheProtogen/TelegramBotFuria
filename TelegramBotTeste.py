from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, timedelta
import openai
from APIConnection import pegar_jogos_furia
from APIConnection import pegar_jogos_futuros_api
from APIConnection import pegar_ultimos_resultados_furia
import os
from dotenv import load_dotenv
load_dotenv()

print("CHAVE:", os.getenv("OPENAI_API_KEY"))

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TOKEN = "7698630433:AAGv0pc90zYSa-CVOles-rVvyJxRH5q9hcw"  # Aqui você coloca o seu token do bot do telegram! (Apenas testei no BotFather, não sei se funciona com outros bots)


async def gerar_resposta_torcedor(texto_usuario):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um torcedor apaixonado da FURIA. Seja animado e apoie sempre o time!"},
            {"role": "user", "content": texto_usuario},
        ],
        temperature=0.7, # Aqui utilizo a tokenização para limitar o tamanho da resposta e não estourar o limite da minha conta da OpenAI
        max_tokens=150,  # Aqui é medida do quão criativa a resposta deve ser 0 sendo a mais previsível e 1 a mais criativa (porém com risco de quebras)
    )

    return response.choices[0].message.content.strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        ['🔥 Jogos Ao Vivo', '🏆 Próximos Campeonatos!'],
        ['🎯 Últimos campeonatos', '📰 Jogos Marcados!'],
        ['🧡 Mandar Apoio', '🛍️ Loja Oficial'],
        ['📲Feedback do Bot!', '🐾 Sobre a FURIA']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text('Espero que esteja tudo bem com você! \n\n')
    await update.message.reply_text(
        'Temos as seguintes opções abaixo para que você possa usufruir melhor possível do Bot! Vale lembrar que o Bot está em fase de testes e pode apresentar alguns bugs! \n\n'
        '🔥 Jogos Ao Vivo \n\n 🏆 Próximos Campeonatos! \n\n'
        '🎯 Últimos campeonatos \n\n 📰 Jogos Marcados! \n\n'
        '🧡 Venha falar com a torcida (IA) \n\n Loja Oficial \n\n'
        '📲Feedback do Bot! \n\n 🐾 Sobre a FURIA \n\n',
        reply_markup=reply_markup
    )

# Gerenciador de mensagens
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text 
    user_data = context.user_data
    now = datetime.now()

    # Aqui eu checo se o usuário está inativo no chat
    ultima_interacao = user_data.get('ultima_interacao')
    if ultima_interacao:
        if now - ultima_interacao > timedelta(minutes=30):
            await update.message.reply_text("Ei, está por aí? Se precisar de mim, estarei por aqui!")
            user_data.clear()
            user_data['aguardando_nome'] = True
            user_data['boas_vindas_enviada'] = False
            user_data['inatividade'] = True
            user_data['ultima_interacao'] = now
            return
    else:
        user_data['ultima_interacao'] = now

    # Aqui estou tentando atualizar a última hora de interação do usuário para caso tenha passado de mais de 30 min sem resposta, o bot pergunta se o usuário ainda está por ali,
    # inspirado no chatbot do Whatsapp da FURIA!
    user_data['ultima_interacao'] = now

    # Mensagem de retorno após inatividade
    if user_data.get('inatividade'):
        nome = user_data.get('nome_usuario')
        if nome:
            await update.message.reply_text(f"Bem-vindo de volta, FURIOSO {nome}, como posso ajudá-lo?")
        else:
            await update.message.reply_text("Bem-vindo de volta! Fala ae, como posso ajudá-lo?")
        user_data['inatividade'] = False
        await start(update, context)
        return

    # Pergunta nome do usuário (Aqui eu não consegui colocar um certo limite de caracteres ainda!)
    if user_data.get('aguardando_nome'):
        nome = text.split()[0].capitalize()
        user_data['nome_usuario'] = nome
        user_data['aguardando_nome'] = False
        user_data['boas_vindas_enviada'] = True

        await update.message.reply_text(f"Faaaala! {nome}, bem-vindo ao Chatbot da FURIA! Aqui você é parte do nosso time! BORA FURIOSOS!")
        await start(update, context)
        return

    if 'nome_usuario' not in user_data:
        user_data['aguardando_nome'] = True
        await update.message.reply_text("Bem-vindo ao Chatbot da FURIA! Antes de começarmos, qual é o seu nome?")
        return

    if not user_data.get('boas_vindas_enviada'):
        nome = user_data['nome_usuario']
        user_data['boas_vindas_enviada'] = True
        await update.message.reply_text(f"Bem-vindo novamente, {nome}! 👋")
        await start(update, context)
        return

    # Aqui é a lista de respostas que o user pode escolher
    if text == '🔥 Jogos Ao Vivo':
        mensagem = pegar_jogos_furia()
        await update.message.reply_text(mensagem)

    elif text == '📰 Jogos Marcados!':
        mensagem = pegar_jogos_futuros_api()
        await update.message.reply_text(mensagem)

    elif text == '🎯 Últimos campeonatos':
        mensagem = pegar_ultimos_resultados_furia()
        await update.message.reply_text(mensagem)

    elif text == '📰 Últimas Notícias':
        await update.message.reply_text(
        '📰 Headline: FURIA APRESENTA ex-Falcons como novo auxiliar técnico! \n\n' \
        'https://draft5.gg/noticia/furia-apresenta-ex-falcons-como-novo-auxiliar-tecnico')

    elif text == '🧡 Venha falar com a torcida (IA)!':
        await update.message.reply_text('💬 Mande sua mensagem de apoio para o time!')

        # Caso o usuário envie uma mensagem de apoio, use a IA para gerar a resposta
    elif 'apoio' or 'FURIA' or 'time 'in text.lower():  # Verifica se a mensagem tem a palavra 'apoio' ou 'FURIA' ou 'time'
        resposta_torcedor = await gerar_resposta_torcedor(text)
        await update.message.reply_text(resposta_torcedor)

    elif text == '🛍️ Loja Oficial':
        await update.message.reply_text('🛒 Confira a loja: https://loja.furia.gg/')

    elif text == '🏆 Próximos Campeonatos!':
        await update.message.reply_text(
            'Haverão grandes campeonatos dentro desses 30 dias! \n\n'
            '🗓️ 1. Campeonato PGL Astana 2025! (10/05/25 até 18/05/2025) \n\n'
            '🗓️ 2. Campeonato IEM Dallas 2025! (19/05/25 até 25/05/2025) \n\n'
        )

    elif text == '📲Feedback do Bot!': 
        await update.message.reply_text('Já pensou em como melhorar o bot? Deixe uma mensagem ao criador! \n\n'
        ' 📲 Telegram: LukeDogo (@LukeProto) \n\n'
        ' 💻 Código fonte: https://github.com/LukeTheProtogen/TelegramBotFURIA')

    elif text == '🐾 Sobre a FURIA': 
        await update.message.reply_text('FURIA é uma organização brasileira de e-sports com destaque em CS, LoL, Valorant, e mais. Fundada em 2017, representa o Brasil internacionalmente!')

    else:
        await update.message.reply_text('🤔 Não entendi, escolha uma opção!')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot Rodando...")
    app.run_polling()

if __name__ == '__main__':
    main()

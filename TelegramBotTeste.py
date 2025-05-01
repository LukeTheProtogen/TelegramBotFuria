from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from APIConnection import pegar_jogos_furia
from APIConnection import pegar_jogos_futuros_api
from APIConnection import pegar_ultimos_resultados_furia
import os

TOKEN = os.getenv("Telegram_Bot_Token")  # Aqui fica o token do Bot do Telegram!

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        ['🔥 Jogos Ao Vivo', '🏆 Próximos Campeonatos!'],
        ['🎯 Últimos campeonatos', '📰 Jogos Marcados!'],   # Aqui o usuário pode escolher as opções nas quais ele quer seguir
        ['🧡 Mandar Apoio', '🛍️ Loja Oficial'],
        ['📲Feedback do Bot!', '🐾 Sobre a FURIA']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Espero que esteja tudo bem com você! \n\n',
                                    
    )
    await update.message.reply_text('Temos as seguintes opções abaixo para que você possa usufruir melhor possível do Bot! Vale lembrar que o Bot está em fase de testes e pode apresentar alguns bugs! \n\n'
        '🔥 Jogos Ao Vivo, 🏆 Próximos Campeonatos! \n\n' 
        '🎯 Últimos campeonatos, 📰 Jogos Marcados! \n\n'
        '🧡 Mandar Apoio, Loja Oficial \n\n'
        '📲Feedback do Bot!, 🐾 Sobre a FURIA \n\n',
        reply_markup=reply_markup
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: # Função que consegue ler as mensagens do usuário.
    text = update.message.text 
    entendido = True # Variável que verificar se o Bot entendeu a mensagem do usuário ou não.

     # Se ainda não temos o nome, e estamos aguardando
    if context.user_data.get('aguardando_nome'):
        nome = text.split()[0].capitalize()
        context.user_data['nome_usuario'] = nome
        context.user_data['aguardando_nome'] = False
        context.user_data['boas_vindas_enviada'] = True

        await update.message.reply_text(f"FAAAAAALAAAAA {nome}, bem-vindo ao Chatbot da FURIA, aqui você é parte do nosso time FURIA!  irei responder suas dúvidas e status do time em relação aos campeonatos de CS! BORA FURIOSOS!")
        await start(update, context)
        return

    # Se ainda não temos o nome, vamos perguntar
    if 'nome_usuario' not in context.user_data:
        context.user_data['aguardando_nome'] = True
        await update.message.reply_text("Bem-vindo ao Chatbot da FURIA! Aqui irei responder suas dúvidas e status do time em relação aos campeonatos de CS! BORA FURIOSOS! \n\n " 
        "Antes de começarmos, qual é o seu nome?")
        return

    # Se já temos o nome e ainda não demos as boas-vindas
    if not context.user_data.get('boas_vindas_enviada'):
        nome = context.user_data['nome_usuario']
        context.user_data['boas_vindas_enviada'] = True
        await update.message.reply_text(f"Bem-vindo novamente, {nome}! 👋")
        await start(update, context)
        return

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
        await update.message.reply_text('📰 Headline: FURIA APRESENTA ex-Falcons como novo auxiliar técnico! \n\n' \
        'https://draft5.gg/noticia/furia-apresenta-ex-falcons-como-novo-auxiliar-tecnico')

    elif text == '🧡 Mandar Apoio':
        await update.message.reply_text('💬 Mande sua mensagem de apoio para o time!')

    elif text == '🛍️ Loja Oficial':
        await update.message.reply_text('🛒 Confira a loja: https://loja.furia.gg/')

    elif text == '🏆 Próximos Campeonatos!':
        await update.message.reply_text('Haverão grandes campeonatos dentro desses 30 dias! \n\n'
         '🗓️ 1. Campeonato PGL Astana 2025! (10/05/25 até 18/05/2025) \n\n'
         '🗓️ 2. Campeonato IEM Dallas 2025! (19/05/25 até 25/05/2025) \n\n')

    elif text == '📲Feedback do Bot!': 
        await update.message.reply_text('Já pensou em como melhorar o bot? Deixe uma mensagem ao criador! \n\n'
         ' 📲 Telegram: LukeDogo (@LukeProto) \n\n'
         ' 💻 Baixe o código fonte no GIT e entenda como funciona! https://github.com/LukeTheProtogen/TelegramBotFURIA')
        
    elif text == '🐾 Sobre a FURIA': 
        await update.message.reply_text('Furia (estilizado FURIA) é uma organização brasileira que atua nas modalidades de e-sports em Counter-Strike 2, Rocket League, League of Legends, Valorant, Rainbow Six: Siege, Apex Legends,[1] e Futebol de 7. Fundada em 2017, a FURIA possui o time de Counter-Strike que melhor desempenha nas competições internacionais mais recentes, sempre a frente nas colocações entre equipes do país. \n\n'
        )
    else:
        entendido = False
        await update.message.reply_text('🤔 Não entendi, escolha uma opção!')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot Rodando...")
    app.run_polling()

if __name__ == '__main__':
    main()

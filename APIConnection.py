from datetime import datetime, timedelta, timezone # Formatar a data e hora
from dateutil.parser import parse # Conversor de data, hora e fuso
from dateutil import parser 
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do arquivo .env (Este arquivo contém a minha chave de API e armazenei ela para não ficar exposta ao público :D

API_KEY = os.getenv("PANDASCORE_API_KEY")
headers = {
    "Authorization": f"Bearer {API_KEY}"
}


def pegar_jogos_furia():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    url = "https://api.pandascore.co/csgo/matches/running"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        dados = response.json()

        mensagem = ""
        for jogo in dados:
            if 'FURIA' in (jogo['opponents'][0]['opponent']['name'] + jogo['opponents'][1]['opponent']['name']):
                time1 = jogo['opponents'][0]['opponent']['name']
                time2 = jogo['opponents'][1]['opponent']['name']
                status = jogo['status']
                mensagem += f"🎮 {time1} vs {time2}\nStatus: {status}\n\n"

        return mensagem if mensagem else "A FURIA não está jogando agora."
    else:
        return "Erro ao buscar partidas na Pandascore."

def pegar_jogos_futuros_api(): # Futuros jogos da FURIA (VAI TIME)
    headers = {
        "Authorization": f"Bearer {API_KEY}" # Chave de API da Pandascore
    }
    url = "https://api.pandascore.co/csgo/matches/upcoming" # Url da API da Pandascore para pegar os jogos futuros e de qual campeonato também

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        dados = response.json()
        mensagem = "🔥 Teremos GRAAANDEZAAÇO JOGOS DA FURIAA nos próximos dias! 🔥 \n\n"
        jogos_furia = False

        for jogo in dados:
            oponentes = jogo.get('opponents', [])
            if oponentes and any('FURIA' in o['opponent']['name'] for o in oponentes):
                nome1 = oponentes[0]['opponent']['name']
                nome2 = oponentes[1]['opponent']['name']
                data = jogo.get('begin_at') or jogo.get('scheduled_at')

                if data:
                    try:
                        data_formatada = parser.parse(data).strftime('%d/%m/%Y %H:%M')
                    except Exception as e:
                        data_formatada = "Data inválida"

                    evento = jogo['league']['name']
                    mensagem += f"🆚 {nome1} VERSUS {nome2}\n🗓️ {data_formatada}\n🏆 Campeonato: {evento}\n\n"
                    jogos_furia = True

        return mensagem if jogos_furia else "Nenhum jogo agendado para o time da FURIA por enquanto!"
    else:
        return f"Erro ao buscar jogos futuros. Status: {response.status_code}, Detalhes: {response.text}"

def pegar_ultimos_resultados_furia():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    url = "https://api.pandascore.co/teams/126036/matches?sort=-begin_at&page[size]=50"  # Aqui estou filtrando a pesquisa para pegar apenas os jogos da FURIA (ID 126036) e pegando os ultimos jogos

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Erro ao acessar a API (status {response.status_code})"

        dados = response.json()
        mensagem = "📅 Jogos da FURIA nos últimos 15 dias:\n\n"

        hoje = datetime.now(timezone.utc)
        limite = hoje - timedelta(days=30)
        jogos_furia = 0

        for jogo in dados:
            data_raw = jogo.get('begin_at')
            if not data_raw:
                continue

            data = parse(data_raw)
            if data < limite:
                continue

            oponentes = jogo.get('opponents', [])
            if len(oponentes) < 2:
                continue

            nomes_times = [op['opponent']['name'] for op in oponentes]
            if not any("furia" in nome.lower() for nome in nomes_times):
                continue

            team1, team2 = nomes_times[0], nomes_times[1]
            placar1 = jogo.get('results', [{}])[0].get('score', '?')
            placar2 = jogo.get('results', [{}])[1].get('score', '?')

            if placar1 == '?' or placar2 == '?':
                resultado_final = "Resultado indisponível"
            else:
                vencedor = team1 if placar1 > placar2 else team2
                resultado_final = "Vitória" if "furia" in vencedor.lower() else "Derrota"

            mensagem += f"🆚 {team1} vs {team2}\n📅 {data.strftime('%d/%m/%Y')}\n🔢 Placar: {placar1} - {placar2}\n🏆 Resultado: {resultado_final}\n\n"
            jogos_furia += 1

        return mensagem if jogos_furia else "A FURIA não jogou nos últimos 15 dias D: "

    except Exception as e:
        return f"Erro ao processar os dados: {e}"
    

import streamlit as st
from statsbombpy import sb
from mplsoccer import Pitch, Sbopen
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import json

parser = Sbopen()

# Functions

def match_data(match_id):
    return parser.event(match_id)[0]

def get_match_label(matches, match_id):
    row = matches[matches["match_id"] == match_id].iloc[0]
    return f"{row['match_date']} - {row['home_team']} vs {row ['away_team']}"

def plot_passes(match, player_name):
    player_filter = (match['type_name'] == 'Pass') & (match['player_name'] == player_name)
    df_pass = match.loc[player_filter, ['x', 'y', 'end_x', 'end_y']]
    pitch = Pitch(pitch_type='statsbomb',
                  pitch_color='grass',
                  line_color='white',
                  tick=True,
                  label=True
    )

    fig, ax = pitch.grid(
        grid_height = 0.8,
        title_height = 0.01,
        axis = False,
        endnote_height = 0.1,
        title_space = 0.02,
        endnote_space = 0.02
    )

    pitch.arrows(df_pass['x'],
                df_pass['y'],
                df_pass['end_x'],
                df_pass['end_y'],
                color='white',
                ax=ax['pitch'])
    
    pitch.kdeplot(x=df_pass['x'],
                  y=df_pass['y'],
                  ax=ax['pitch'],
                  cmap='coolwarm',
                  alpha=0.5,
                  shade=True)
    return fig

def plot_shots(match, player_name):
    player_filter = (match['type_name'] == 'Shot') & (match['player_name'] == player_name)
    df_pass = match.loc[player_filter, ['x', 'y', 'end_x', 'end_y']]
    pitch = Pitch(pitch_type='statsbomb',
                  pitch_color='grass',
                  line_color='white',
                  tick=True,
                  label=True
    )

    fig, ax = pitch.grid(
        grid_height = 0.8,
        title_height = 0.01,
        axis = False,
        endnote_height = 0.1,
        title_space = 0.02,
        endnote_space = 0.02
    )

    pitch.arrows(df_pass['x'],
                df_pass['y'],
                df_pass['end_x'],
                df_pass['end_y'],
                color='white',
                ax=ax['pitch'])
    
    pitch.kdeplot(x=df_pass['x'],
                  y=df_pass['y'],
                  ax=ax['pitch'],
                  cmap='coolwarm',
                  alpha=0.5,
                  shade=True)

    return fig

def pie_chart(label1, label2, value1, value2, title):

    labels = []
    sizes = []

    if value1 > 0:
        labels.append(label1)
        sizes.append(value1)

    if value2 > 0:
        labels.append(label2)
        sizes.append(value2)

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    ax.set_title(title)
    return fig

@st.cache_data 
def pandas_to_csv(df):
    return df.to_csv(index=False)

# Main Function = App
def main():

    # initializing session state to track user parameters
    if 'user_name' not in st.session_state:
        st.session_state['user_name'] = ''

    if 'competition' not in st.session_state:
        st.session_state['competition'] = ''

    if 'season' not in st.session_state:
        st.session_state['season'] = ''

    if 'game' not in st.session_state:
        st.session_state['game'] = ''

########## MENU ####################
    st.title("Análise de Jogos de Futebol")

    menu = ['Home', 'Explorar Dados dos Jogos', 'Cristiano Ronaldo']
    choice = st.sidebar.selectbox('Menu', menu)

############ HOME PAGE ############################
    if  choice == 'Home':
        st.subheader('Bem vindo ao App de Análise de Jogos de Futebol')
        st.image('https://media.istockphoto.com/id/464558990/pt/foto/estádio-à-noite.jpg?s=612x612&w=0&k=20&c=gEjM94ZLSBuWOHOsarq-AV_F4cxjkkWfDxykZxfTDFU=')
        st.write('O objetivo do app é permitir a exploração de dados de jogos de futebol de diversas competições e temporadas')
        st.write('Caso tenha alguma sugestão, favor entrar em contato com o desenvolvedor: pedromvba@gmail.com')

        # User Name
        name = st.text_input('Digite seu Nome de Usuário')
        if name:
            st.session_state['user_name'] = name
            st.write('Usuário Salvo, favor usar o Menu para Navegar')

        
################ DATA EXPLORE PAGE ############################
    elif  choice == 'Explorar Dados dos Jogos':
        st.subheader('Explore aqui dados das partidas a partir das competições e temporadas disponíveis')
        st.image('images/soccer_analysis.jpg')

        # Competitions
        competitions = sb.competitions()
        competitions_names = competitions['competition_name'].unique()
        competition = st.selectbox('Select uma Competição', competitions_names)
        st.session_state['competition'] = competition
        competition_id = competitions[competitions["competition_name"] == competition]["competition_id"].values[0]

        # Seasons
        seasons = competitions[competitions["competition_name"] == competition]["season_name"].unique()
        season_name = st. selectbox("Select uma Temporada", seasons)
        st.session_state['season'] = season_name
        season_id = competitions[competitions["season_name"] == season_name]["season_id"].values[0]
        
        # Game
        matches = sb.matches(competition_id = competition_id, season_id=season_id)
        game = st.selectbox("Select uma Partida", 
                            matches['match_id'],
                            format_func= lambda idx:  get_match_label(matches, idx))
        st.session_state['game'] = game

        # Match Details
        with st.container():
            st.markdown("<h1 style='text-align: center; color: blue; '>Match Details</h1>", unsafe_allow_html=True)
            
            # Match Date
            date = matches[matches["match_id"] == game]["match_date"].values[0]
            st.markdown(f"<h5 style='text-align: center; color: blue; '>{date}</h5>", unsafe_allow_html=True)
            
            # Referee
            referee = matches[matches["match_id"] == game]["referee"].values[0]
            st.markdown(f"<h6 style='text-align: center; color: blue; '>{referee}</h6>",unsafe_allow_html=True)

            # Goals
            game_shots = sb.events(match_id=game, split=True, flatten_attrs=True)['shots']
            goal_shots = game_shots[game_shots['shot_outcome'] == 'Goal']
            for _, row in goal_shots.iterrows():
                goal_data = f"Gol {row['team']} - {row['minute']} min - {row['player']}"
                st.markdown(f"<p style='text-align: center; color: red; '>{goal_data}</p>",unsafe_allow_html=True)


        left_column, right_column = st.columns(2)
        
        
        with st.container():
            # Home Team
            with left_column:
                st.subheader("Home Team")
                home_team = matches[matches["match_id"] == game]["home_team"].values[0]
                st.write(f'#### {home_team}')


                home_shots_on_target = game_shots[(game_shots['shot_outcome'].isin(['Goal', 'Saved'])) & (game_shots['team'] == home_team)].shape[0]
                home_all_shots = game_shots[game_shots['team'] == home_team].shape[0]
                
                home_shots_on_target_pct = home_shots_on_target / home_all_shots if home_all_shots > 0 else 0
                st.write(f"Chutes no Alvo: {home_shots_on_target} / {home_all_shots} ({home_shots_on_target_pct:.2%})")
                
                home_score = matches[matches["match_id"] == game]["home_score"].values[0]
                st.metric("Gols", home_score)


                st.write('Jogadores Disponíveis')
                lineups = sb.lineups(match_id=game)
                home_lineup = lineups[home_team][['player_nickname', 'player_name', 'jersey_number']]
                home_lineup['player_nickname'] = home_lineup['player_nickname'].fillna(home_lineup['player_name'])
                home_lineup = home_lineup[['player_nickname', 'jersey_number']]
                home_lineup = home_lineup.rename(columns={'player_nickname': 'Jogador', 'jersey_number': 'Número'})
                st.dataframe(home_lineup, hide_index=True)


            # Away Team 
            with right_column:
                st.subheader ("Away Team")
                away_team = matches[matches["match_id"] == game]["away_team"].values[0]
                st.write(f'#### {away_team}')

                away_shots_on_target = game_shots[(game_shots['shot_outcome'].isin(['Goal', 'Saved'])) & (game_shots['team'] == away_team)].shape[0]
                away_all_shots = game_shots[game_shots['team'] == away_team].shape[0]
                
                away_shots_on_target_pct = away_shots_on_target / away_all_shots if away_all_shots > 0 else 0
                st.write(f"Chutes no Alvo: {away_shots_on_target} / {away_all_shots} ({away_shots_on_target_pct:.2%})")

                away_score = matches[matches["match_id"] == game]["away_score"].values[0]
                st.metric("Gols", away_score)

                st.write('Jogadores Disponíveis')
                lineups = sb.lineups(match_id=game)
                away_lineup = lineups[away_team][['player_nickname', 'player_name', 'jersey_number']]
                away_lineup['player_nickname'] = away_lineup['player_nickname'].fillna(away_lineup['player_name'])
                away_lineup = away_lineup[['player_nickname', 'jersey_number']]
                away_lineup = away_lineup.rename(columns={'player_nickname': 'Jogador', 'jersey_number': 'Número'})
                st.dataframe(away_lineup, hide_index=True)

        # Events
        st.write('#### Eventos de Passes e Chutes da Partida por Jogador')

        st.write(lineups[home_team]['player_name'].unique())

        home_names = lineups[home_team]['player_name'].unique()
        away_names = lineups[away_team]['player_name'].unique()
        players_names = list(home_names) + list(away_names)
        players = st.multiselect('Selecione os Jogadores', players_names)

        time_box = st.slider('Selecione os Minutos do Jogo', value = (0, 90), max_value=90)

        if players and time_box:

            with st.spinner('Estamos Filtrando Seus Dados...'):
                    time.sleep(2)
                    st.success("Pronto!")

            events = sb.events(match_id=game, split=True, flatten_attrs=True)

            passes = events['passes']
            shots = events['shots']
            shots_passes = pd.concat([passes, shots], ignore_index=True)

            selected_events = shots_passes[shots_passes['player'].isin(players) & (shots_passes['minute'] >= time_box[0]) & (shots_passes['minute'] <= time_box[1])]

            if selected_events.empty:
                st.write('Nenhum Evento Encontrado')
            else:
                st.dataframe(selected_events.sort_values('minute'), hide_index=True)
            
                # Data Donwload
                st.write('Download dos Dados')
                
                st.download_button(
                    label='Clique para Baixar os Dados Selecionados',
                    data=pandas_to_csv(selected_events),
                    file_name='eventos_selecionados.csv')


################### CRISTIANO RONALDO PAGE ############################
    else:
        st.subheader('Cristiano Ronaldo - Portugal x Espanha - Copa 2018')
        st.markdown(f"<h3 style='text-align: center; color: red; '>{'Portugal 3 x 3 Espanha'}</h3>", unsafe_allow_html=True)
        st.image('https://conteudo.imguol.com.br/c/copadomundo/2018/imagem/b4/2018/06/15/cristiano-ronaldo-comemora-gol-de-portugal-contra-a-espanha-1529086642745_v2_1920x1365.jpg')

        # Filtering Game Shots Data
        game_shots = sb.events(match_id=7576, split=True, flatten_attrs=True)['shots']
        goal_shots = game_shots[(game_shots['shot_outcome'] == 'Goal') & (game_shots['player'] == 'Cristiano Ronaldo dos Santos Aveiro')]

        st.write(' #### Gols de Portugal:')
        # Goals     
        for _, row in goal_shots.iterrows():
            goal_data = f"Gol - {row['minute']} min - Cristiano Ronaldo"
            st.markdown(f"<p style='text-align: left; color: red; '>{goal_data}</p>",unsafe_allow_html=True)

        # Game Data
        port_spain_data = match_data(7576)

        # CR7 and Portugal stats
        cr7_shots_on_target = game_shots[(game_shots['shot_outcome'].isin(['Goal', 'Saved'])) & (game_shots['player'] == 'Cristiano Ronaldo dos Santos Aveiro')].shape[0]
        cr7_all_shots = game_shots[game_shots['player'] == 'Cristiano Ronaldo dos Santos Aveiro'].shape[0]
        portugal_all_shots = game_shots[(game_shots['shot_outcome'].isin(['Goal', 'Saved'])) & (game_shots['team'] == 'Portugal')].shape[0]
        
        cr7_shots_on_target_pct = cr7_shots_on_target / cr7_all_shots if cr7_all_shots > 0 else 0
        cr7_portugal_shots_on_target_pct = cr7_shots_on_target / portugal_all_shots if portugal_all_shots > 0 else 0

        st.write('### Aproveitamento Cristiano Ronaldo em Chutes')

        col1, col2 = st.columns(2)
        with col1:
                # CR7 Stats
                st.write(" #### Aproveitamento Cristiano Ronaldo")
                st.markdown(f"<p>Percentual de Chutes no Gol</p><p style='color: green; font-size: 40px;'>{100 * cr7_shots_on_target_pct:.2f}%</p>", unsafe_allow_html=True)
                
                fig3 =  pie_chart(label1 = 'Chutes no Alvo',
                  label2 = 'Chutes Fora do Alvo',
                  value1 = cr7_shots_on_target,
                  value2 = cr7_all_shots - cr7_shots_on_target,
                  title = 'Chutes no Gol Cristiano Ronaldo')
                st.pyplot(fig3)
                       
        with col2:
                # CR7 x Portugal Stats
                st.write(" #### Cristiano Ronaldo x Outros Jogadores")
                st.markdown(f"<p>Percentual de CR7 nos chutes a gol de Portugal</p><p style='color: green; font-size: 40px;'>{100 * cr7_portugal_shots_on_target_pct:.2f}%</p>", unsafe_allow_html=True)

                fig4 =  pie_chart(label1 = 'Cristiano Ronaldo',
                    label2 = 'Outros Jogadores',
                    value1 = cr7_shots_on_target,
                    value2 = portugal_all_shots - cr7_shots_on_target,
                    title = 'Chutes a Gol de Portugal por Jogador')
        
                st.pyplot(fig4)

        # CR7 Maps
        st.write(' ### Mapas de Cristiano Ronaldo')

        # progress bar
        progress_bar = st.progress(0, text='Estamos Preparando os Mapas!')
        for percent in range(100):
            time.sleep(0.01)
            progress_bar.progress(percent + 1, text='Estamos Preparando os Mapas!')
        
        time.sleep(1)
        progress_bar.empty()

        time.sleep(0.3)
    
        # Passes Map
        st.write('#### Mapa de Passes')
        fig1 = plot_passes(port_spain_data, 'Cristiano Ronaldo dos Santos Aveiro')
        st.pyplot(fig1)

        # Shots Map
        st.write(' #### Mapa de Chutes a Gol')
        fig2 = plot_shots(port_spain_data, 'Cristiano Ronaldo dos Santos Aveiro')
        st.pyplot(fig2)

        # Foul Map
        df, related, freeze, tactics = parser.event(7576)
        st.write(' #### Mapa das Faltas Recebidas por Cristiano Ronaldo')
        df = df[(df.player_name == 'Cristiano Ronaldo dos Santos Aveiro') & (df.type_name == 'Foul Won')].copy()
        pitch = Pitch()
        fig5, ax = pitch.draw(figsize=(8, 6))
        hull = pitch.convexhull(df.x, df.y)
        poly = pitch.polygon(hull, ax=ax, edgecolor='cornflowerblue', facecolor='cornflowerblue', alpha=0.3)
        scatter = pitch.scatter(df.x, df.y, ax=ax, edgecolor='black', facecolor='cornflowerblue')
        st.pyplot(fig5)

if __name__ == "__main__":
    main()

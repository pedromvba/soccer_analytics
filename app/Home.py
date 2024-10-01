import streamlit as st
from statsbombpy import sb
from mplsoccer import Pitch, Sbopen

parser = Sbopen()

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
                  line_color='white'
    )

    fig, ax = pitch.grid(
        grid_height = 0.7,
        title_height = 0.1,
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


def main():

    st.title("Soccer Analysis")

    menu = ['Home', 'Explore Data', 'Argentina x France', 'About']
    choice = st.sidebar.selectbox('Menu', menu)
    if  choice == 'Home':
        st.subheader('Welcome to Soccer Analysis')
        st.write('This is .... - Colocar Imagem')

    elif  choice == 'Explore Data':
        st.subheader('Explore Data about matches, competitions, players, and teams')
        st.write('This is .... - Colocar Imagem')

        competitions = sb.competitions()
        competitions_names = competitions['competition_name'].unique()
        competition = st.selectbox('Select Competition', competitions_names)
        competition_id = competitions[competitions["competition_name"] == competition]["competition_id"].values[0]

        seasons = competitions[competitions["competition_name"] == competition]["season_name"].unique()
        season_name = st. selectbox("Select Season", seasons)
        season_id = competitions[competitions["season_name"] == season_name]["season_id"].values[0]
        
        matches = sb.matches(competition_id = competition_id, season_id =season_id)

        game = st.selectbox("Select a Match", matches['match_id'], 
                            format_func= lambda idx:  get_match_label(matches, idx))

        with st.container():
            st.markdown("<h1 style='text-align: center; color: blue; '>Match Details</h1>", unsafe_allow_html=True)
            
            date = matches[matches["match_id"] == game]["match_date"].values[0]
            st.markdown(f"<h5 style='text-align: center; color: blue; '>{date}</h5>", unsafe_allow_html=True)
            
            referee = matches[matches["match_id"] == game]["referee"].values[0]
            st.markdown(f"<h6 style='text-align: center; color: blue; '>{referee}</h6>", unsafe_allow_html=True)

        left_column, right_column = st.columns(2)
        
        with st.container():
            with left_column:
                st.subheader("Home Team")
                home_team = matches[matches["match_id"] == game]["home_team"].values[0]
                st.write(f'#### {home_team}')
                home_score = matches[matches["match_id"] == game]["home_score"].values[0]
                st.metric("Goals", home_score)

                # colocar cartões
                # autores dos gols com o tempo

            with right_column:
                st.subheader ("Away Team")
                away_team = matches[matches["match_id"] == game]["away_team"].values[0]
                st.write(f'#### {away_team}')
                away_score = matches[matches["match_id"] == game]["away_score"].values[0]
                st.metric("Goals", away_score)

    
        dribbles = sb.events(match_id=game, split=True, flatten_attrs=True)['dribbles']
        st.dataframe(dribbles)

    else:
        st.subheader('Argentina X France')
        st.write('This is .... - Colocar Imagem')

        fifa_wold_cup_22_matches = sb.matches(competition_id=43, season_id=106)
        # final_match_id = fifa_wold_cup_22_matches[fifa_wold_cup_22_matches['match_id'] == 3869685].iloc[0]
        final_data = match_data(3869685)

        #final_events = sb.events(match_id=3869685, split=True, flatten_attrs=True)
        #lineups = sb.lineups(match_id=3869685)
        
        st.image('https://s.yimg.com/ny/api/res/1.2/9jV8vDNzSYp3DvcSqmWGtQ--/YXBwaWQ9aGlnaGxhbmRlcjt3PTY0MDtoPTQyNw--/https://s.yimg.com/os/creatr-uploaded-images/2022-12/6d839e90-7f35-11ed-bdfb-e88acc5d830b')

        col1, col2 = st.columns(2)
        with col1:
            st.write('Lionel Messi')
            fig1 = plot_passes(final_data, 'Lionel Andrés Messi Cuccittini')
            st.pyplot(fig1)




        with col2:
            st.write('Kylian Mbappé')
            fig2 = plot_passes(final_data, 'Kylian Mbappé Lottin')
            st.pyplot(fig2)

        
        #st.write(lineups['France'])

        # Kylian Mbappé Lottin - 3009
        # Lionel Andrés Messi Cuccittini - 5503

















if __name__ == "__main__":
    main()

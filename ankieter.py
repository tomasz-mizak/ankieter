from pprint import pprint
from surveys import SurveyHelper
import inquirer
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from dbcontext import dbcontext
from dotenv import dotenv_values

# ---------------------- initialization

# load config
config = dotenv_values('.env')
erro = False

# create None type varialbe for database context
dbctx = None

# check credentials
user = None
password = None

# try to get credentials from enviroment file
read_error = False
try:
    user = config['USER']
    password = config['PASSWORD']
except KeyError as e:
    read_error = True
    print(f"Nie można znaleźć klucza {e} w pliku środowiskowym.\nProszę uzupełnić dane ręcznie.")
finally:

    can_skip = False
    if not read_error:
        # check connection on .env credentials
        dbctx = dbcontext(user, password)
        can_skip = dbctx.is_connection()
        if not can_skip:
            print("Nawiązanie połączenia na danych z pliku środowiskowego nie powiodło się, wprowadź dane ręcznie.")
        else:
            print("Nawiązanie połączenia z bazą danych, z użyciem pliku środowiskowego, powiodło się.")

    if not can_skip:
        login_prompting = True
        attempt = 0
        while login_prompting:
            # read credentials using inquirer
            user = inquirer.text(message='Proszę wpisać login do USOS/oracledb')
            password = inquirer.password(message='Proszę wpisać hasło')
            # check connection
            dbctx = dbcontext(user, password)
            if dbctx.is_connection():
                login_prompting = False
                print("Połączono z bazą danych.")
            else:
                attempt = attempt + 1
                print(f"\nNie udało się połączyć na wprowadzonych poświadczeniach (próba {attempt}), kod błędu to:\n {dbctx.exc}\n\nSpróbuj ponownie...\n")

# finally create instance of SurveyHelper, using initialized dbcontext
helper = SurveyHelper(dbctx)


# ---------------------- inquirer prompting / final code
all_surveys = [] # list for all survey codes available on '0500-%' filter.

for i, r in helper.available().iterrows(): # iterrow DataFrame from helper to save as list[all_surveys]
    all_surveys.append(r.kod) # rows: kod, opis

# game_loop variable, after calculating program ask about exit or start from scratch with calculations.
game_loop = True

while game_loop:

    # TODO: create way to select filter

    a1 = inquirer.prompt([
        inquirer.List('survey_code',message="Którą ankietę chcesz wybrać?",choices=all_surveys),
        inquirer.List('type',message="Czy chcesz policzyć wyniki wszystkich, czy dla pojedyńczego pracownika?",choices=['Policz wyniki dla wszystkich', 'Sam wybiorę osobę, której wyniki chcę poznać']),
    ])

    survey_code = a1['survey_code']

    if a1['type'] == 'Policz wyniki dla wszystkich':

        workers = srv.workers(survey_code)
        result = []
        wor_len = workers.shape[0]
        print(f"Liczę średnią dla {wor_len} pracowników.")
        pbar = tqdm(total=wor_len)
        for i, r in workers.iterrows():
            avg = srv.worker_avg(survey_code, r.prac_id)
            result.append({
                "imie": r.imie,
                "nazwisko": r.nazwisko,
                "srednia": str(avg).replace('.', ',')
            })
            pbar.update(1)
        pbar.close()
        result = pd.DataFrame(result)
        now = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
        filename = f"result {now}.csv"

        result.to_csv(filename, sep=';', encoding='utf-8-sig')
        print(f'Plik {filename} został zapisany w katalogu aplikacji.')

    else:
        a2 = inquirer.prompt([
            inquirer.List('search-type',message="Czy chcesz wyświetlić listę pracowników (duża), czy wyszukać po nazwisku?",choices=['Wyświetl pełną listę pracowników na wybraną wcześniej ankietę', 'Chcę wpisać nazwisko i wybrać z znalezionych wyników'])
        ])
        
        if a2['search-type'] == 'Wyświetl pełną listę pracowników na wybraną wcześniej ankietę':
            workers = ['Chcę wrócić do poprzedniego wyboru']
            for i, r in helper.workers(survey_code).iterrows():
                workers.append(f'[{r.prac_id}] {r.imie} {r.nazwisko}')

            a3 = inquirer.prompt([
                inquirer.List('search-type',message=f"Wybierz pracownika z ankiety {survey_code}",choices=workers)
            ])


        else:

            condition = True

            while condition:

                questions = [
                inquirer.Text('search-filter',
                                message="Wpisz nazwisko",
                            ),
                ]
                a3 = inquirer.prompt(questions)

                print("Znalezione wiersze:")
                pprint(srv.workers_filter(survey_code, a3['search-filter']))

                questions = [
                inquirer.List('continue',
                                message="Czy wyświetlona powyżej lista zawiera pracownika, którego szukasz?",
                                choices=['Tak', 'Nie'],
                            ),
                ]
                a4 = inquirer.prompt(questions)

                if a4['continue'] == 'Tak':
                    questions = [
                    inquirer.Text('worker_id',
                                    message="W takim wypadku podaj kod tego pracownika, znajdujący się pod kolumną prac_id"
                                ),
                    ]
                    a5 = inquirer.prompt(questions)
                    
                    print("Policzona średnia wynosi:")
                    pprint(srv.worker_avg(survey_code, a5['worker_id']))
                    print("\n")

                    condition = False
                    




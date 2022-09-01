from email import message
from pprint import pprint
from surveys import SurveyHelper
import inquirer
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from dbcontext import dbcontext
from dotenv import dotenv_values

# ---------------------- credits
print('\n\n----------------------------------------')
print("Ankieter v0.1\nMizak Tomasz")
print('----------------------------------------\n')

# ---------------------- initialization

# load config
config = dotenv_values('.env')

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

        result = []
        workers = helper.workers(survey_code)
        print(f"Liczę średnią dla {workers.shape[0]} pracowników.")
        pbar = tqdm(total=workers.shape[0]) # initialize progress bar
        for i, r in workers.iterrows(): # iterrow workers from helper DataFrame
            avg = helper.worker_avg(survey_code, r.prac_id) # use helper to calc worker avg
            result.append({ # append worker to workers
                "imie": r.imie,
                "nazwisko": r.nazwisko,
                "srednia": str(avg).replace('.', ',')
            })
            pbar.update(1) # update progress bar progress
        pbar.close() # close progress bar

        # save result to file in main directory
        # TODO: selecting path, where to save
        result = pd.DataFrame(result)
        now = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
        filename = f"result {now}.csv"

        result.to_csv(filename, sep=';', encoding='utf-8-sig') # utf-8-sig (pl characters on utf-8 doesn't work)
        print(f'Plik {filename} został zapisany w katalogu aplikacji.\n\n')

        # continue program?
        a2 = inquirer.prompt([
            inquirer.Confirm("continue", message="Czy zacząć od początku?", default=False),
        ])
        
        if not a2['continue']:
            game_loop = False

    else:
        a2 = inquirer.prompt([
            inquirer.List('search-type',message="Czy chcesz wyświetlić listę pracowników (duża), czy wyszukać po nazwisku?",choices=['Wyświetl pełną listę pracowników na wybraną wcześniej ankietę', 'Chcę wpisać nazwisko i wybrać z znalezionych wyników'])
        ])
        
        if a2['search-type'] == 'Wyświetl pełną listę pracowników na wybraną wcześniej ankietę':
            workers = []
            for i, r in helper.workers(survey_code).iterrows():
                workers.append(f'[{r.prac_id}] {r.imie} {r.nazwisko}')

            a3 = inquirer.prompt([
                inquirer.List('selected-worker',message=f"Wybierz pracownika z ankiety {survey_code}",choices=workers)
            ])

            # read selection and splice selected string to get worker_id
            selected = str(a3['selected-worker'])
            worker_id = int(((selected.split(" ")[0]).replace('[', '')).replace(']', ''))
            avg = helper.worker_avg(survey_code, worker_id)
            print(f"Liczę średnią dla pracownika: {a3['selected-worker']}")
            print(f"Średnia wynosi: {avg}\n\n")

            # continue program?
            a4 = inquirer.prompt([
                inquirer.Confirm("continue", message="Czy zacząć od początku?", default=False),
            ])
            
            if not a4['continue']:
                game_loop = False

        else:

            condition = True

            while condition:

                a3 = inquirer.prompt([
                    inquirer.Text('search-filter',message="Wpisz nazwisko (lub jego część, wielkość liter ma znaczenie)")
                ])

                workers = ['Użyj innego filtra']
                for i, r in helper.workers_filter(survey_code, a3['search-filter']).iterrows():
                    workers.append(f"[{r.prac_id}] {r.imie} {r.nazwisko}")

                a4 = inquirer.prompt([
                    inquirer.List('selected-worker',message=f"Znaleziono następujących pracowników, użyto filtra: '{a3['search-filter']}'. Wybierz pracownika lub zacznij od nowa",choices=workers)
                ])
                
                if not a4['selected-worker'] == 'Użyj innego filtra':

                    # read selection and splice selected string to get worker_id
                    selected = str(a4['selected-worker'])
                    worker_id = int(((selected.split(" ")[0]).replace('[', '')).replace(']', ''))
                    avg = helper.worker_avg(survey_code, worker_id)
                    print(f"Liczę średnią dla pracownika: {a4['selected-worker']}")
                    print(f"Średnia wynosi: {avg}\n\n")

                    # continue program?
                    a4 = inquirer.prompt([
                        inquirer.Confirm("continue", message="Czy zacząć od początku?", default=False),
                    ])

                    condition = False
                    
                    if not a4['continue']:
                        game_loop = False
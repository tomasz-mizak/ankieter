from pprint import pprint
from surveys import Surveys
import inquirer
import pandas as pd
from tqdm import tqdm
from datetime import datetime

srv = Surveys()
i = 0

while not srv.is_connection():
    print(f"Nie udało się połączyć na wprowadzonych poświadczeniach (próba {i}), kod błędu to:\n {srv.get_exception()}")
    srv = Surveys()
    i = i + 1

av_srv = []

for i, r in srv.available().iterrows():
    av_srv.append(r.kod)

game = True

while game:

    questions = [
    inquirer.List('survey_code',
                    message="Którą ankietę chcesz wybrać?",
                    choices=av_srv,
                ),
    inquirer.List('type',
                    message="Czy chcesz policzyć wyniki wszystkich, czy dla pojedyńczego pracownika?",
                    choices=['Policz wyniki dla wszystkich', 'Sam wybiorę osobę, której wyniki chcę poznać'],
                ),
    ]
    a1 = inquirer.prompt(questions)

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

        questions = [
        inquirer.List('search-type',
                        message="Czy chcesz wyświetlić listę pracowników (duża), czy wyszukać po nazwisku?",
                        choices=['Wyświetl pełną listę pracowników na wybraną wcześniej ankietę', 'Chcę wpisać nazwisko i wybrać z znalezionych wyników'],
                    ),
        ]
        a2 = inquirer.prompt(questions)
        
        if a2['search-type'] == 'Wyświetl pełną listę pracowników na wybraną wcześniej ankietę':
            workers = ['Chcę wrócić do poprzedniego wyboru']
            for i, r in srv.workers(survey_code).iterrows():
                workers.append(r.imie + ' ' + r.nazwisko)

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
                    




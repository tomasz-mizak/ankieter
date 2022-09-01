from dbcontext import dbcontext as dbcx
import inquirer

class SurveyHelper():

    def __init__(self, dbcontext):
        self.dbcx = dbcontext

    def available(self):
        return self.dbcx.query("select kod, opis, utw_data from DZ_EDYCJE_ANKIET where kod like '0500%' order by utw_data DESC")    

    def workers(self, survey_code):
        return self.dbcx.query("select distinct odp.prac_id, prac.imie, prac.nazwisko from DZ_ODPOWIEDZI odp, DZ_PYTANIA_DO_STUDENTOW pyt, (select p.id, o.imie, o.nazwisko from dz_osoby o, dz_pracownicy p where p.os_id = o.id) prac where pyt.id = odp.pytstu_id and pyt.ank_kod = '%s' and prac.id = odp.prac_id" % survey_code)

    def workers_filter(self, survey_code, worker_surname):
        return self.dbcx.query("select distinct odp.prac_id, prac.imie, prac.nazwisko from DZ_ODPOWIEDZI odp, DZ_PYTANIA_DO_STUDENTOW pyt, (select p.id, o.imie, o.nazwisko from dz_osoby o, dz_pracownicy p where p.os_id = o.id and o.nazwisko like '%{worker_surname}%') prac where pyt.id = odp.pytstu_id and pyt.ank_kod = '{survey_code}' and prac.id = odp.prac_id".format(worker_surname=worker_surname,survey_code=survey_code))

    def worker_avg(self, survey_code, worker_id):
        values = self.dbcx.query("select wart.wartosc from DZ_ODPOWIEDZI odp, DZ_PYTANIA_DO_STUDENTOW pyt, DZ_WART_ODP_ANKIET wart where pyt.id = odp.pytstu_id and wart.id = odp.wart_odp_id and pyt.ank_kod = '%s' and odp.prac_id = %s" %(survey_code, worker_id))
        sum = values.sum()[0]
        len = values.shape[0]
        return sum/len
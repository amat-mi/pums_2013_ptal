#-*- coding: utf-8 -*-
# -----------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------
# import dal sistema
from optparse import OptionParser
import sys
import os
import time
import string
import shutil

#import dalla cartella dei parametri
import parametri.parametri as parametro

#import dalla cartella dei moduli
import moduli_vari.connessione as conn_db

import query.aggiornamento as q_agg

#librerie Geografiche
import osgeo.gdal
import osgeo.ogr
import subprocess

class esecuzione_modello(object): 
  o_e, p_conn, c_q , risultato, file_importati= '', '', '', '--- Nessuna operazione eseguita ---', ''
  ris_ora_i, ris_ora_f  = '', '' 
  variaz, vett_cal = 0, []


  def __init__(self, opzioni_elaborazioni): 
    self.ris_ora_i = time.ctime()
    self.c_q = conn_db.classe_connessione(parametro.credenziali_db) 
                
  def __del__(self): 
    pass

  def start(self):
# TODO TODO TODO -- GENERALIZZARE IL MENU -------------------------------------
    # TODO ----------------------------------------------------------------------- 
    # TODO - Aggiungere if else per eventuali comandi opzionali del parser ------- 
    # TODO ----------------------------------------------------------------------- 
    # TODO -----------------------------------------------------------------------
      scelta_rim, vettore_risposte = '', ['0', '1', '2', '3','4', '5','exit']
      while scelta_rim != 'exit':
        print 10*'\n' + """\n\nOpzioni:\n
                  [ 0 ] - Aggiungi al grafo la colonna di ogc_fid e gid \n
                  [ 1 ] - Sistema il grafo stradale aggiungendo i punti di destinazione \n
                  [ 2 ] - Crea la topologia del grafo \n
                  [ 3 ] - Elabora il costo di raggiungimento di ogni nodo del grafo da tutti i punti di destinazione \n
                  [ 4 ] - Crea indici \n
                  [ 5 ] - Visualizza le query di elaborazione  \n
                  [  exit ]\n """
        scelta_rim = raw_input('Inserisci il numero dell\'opzione desiderata: ').lower()
        while scelta_rim not in vettore_risposte:
            scelta_rim = raw_input('%s <--> Scelta non contemplata. \n Inserisci il numero dell\'opzione desiderata: '%scelta_rim).lower()
        if scelta_rim == '0': 
            self.aggiungi_ggcfid_gid()
        if scelta_rim == '1': 
            self.sistema_grafo()
        elif scelta_rim == '2': 
            self.crea_topologia()
        elif scelta_rim == '3': 
            self.elabora_drivingcost()
        elif scelta_rim == '4': 
            self.elabora_indici()
        elif scelta_rim == '5': 
          print '\nOpzione non implementata\n'
          self.visualizza_query()
      sys.exit()

  def inserisci_parametri(self, sql):
    for i in parametro.tabelle:
#      print i, parametro.tabelle[i]
      sql = sql.replace(i, parametro.tabelle[i])
    return sql

  def aggiungi_ggcfid_gid(self):
    self.c_q.esegui_query_no_result(self.inserisci_parametri(q_agg.q_add_gid))


  def sistema_grafo(self):
    count = 0 
    print '\nAvvio sistemazione grafo:\n'
    for i in self.c_q.esegui_query_result(self.inserisci_parametri(q_agg.q_elenco_fermate)):
#     if i[0] not in [10001, 10002, 10003]:
      count+=1
#      print 'Analisi della fermata numero:%s con id = %s' %(count, i[0]) 
      max_ogc_fid = self.c_q.esegui_query_result(self.inserisci_parametri(q_agg.q_max_ogc_fid))[0] 
      print 'Analisi della fermata numero:%s con id = %s --- massimo ogc_fid = %s' %(count, i[0], max_ogc_fid)      
      self.c_q.esegui_query_no_result(self.inserisci_parametri(q_agg.q_aggiungo_nuovi_archi.replace('^___^', '%s'%i[0])))
      print 'Elimino gli archi con ogc_fid minore o uguale a: %s' %(max_ogc_fid) 
      self.c_q.esegui_query_no_result(self.inserisci_parametri(q_agg.q_elimino_arco_old.replace('^___^', '%s'%i[0]).replace('x___X', '%s'%max_ogc_fid)))
    print 'Fine elaborazioni'


  def visualizza_query(self):
    count = 0 
    print '\nAvvio sistemazione grafo:\n'
    for i in self.c_q.esegui_query_result(self.inserisci_parametri(q_agg.q_elenco_fermate)):
      count+=1
      max_ogc_fid = self.c_q.esegui_query_result(self.inserisci_parametri(q_agg.q_max_ogc_fid))[0] 
      print self.inserisci_parametri(q_agg.q_aggiungo_nuovi_archi.replace('^___^', '%s'%i[0]))
      print self.inserisci_parametri(q_agg.q_elimino_arco_old.replace('^___^', '%s'%i[0]).replace('x___X', '%s'%max_ogc_fid))
      if count == 2:
        break

  def crea_topologia(self):
    self.c_q.esegui_query_no_result(self.inserisci_parametri(q_agg.q_topologia))
    

  def crea_nodi_fermate(self):
    print self.c_q.esegui_query_result(self.inserisci_parametri(q_agg.q_elenco_nodi_fermata_veloce))

  def elabora_indici(self):
    self.c_q.esegui_query_no_result(self.inserisci_parametri(q_agg.q_crea_tabella_indici))


  def elabora_drivingcost(self):
    self.c_q.esegui_query_no_result(self.inserisci_parametri(q_agg.q_crea_nodi_fermata))
    count = 0 
    print '\nAvvio DrivingCost:\n'
    for i in self.c_q.esegui_query_result(self.inserisci_parametri(q_agg.q_elenco_nodi_fermata_veloce)):
      count+=1
      print 'Analisi del nodo numero:%s con id = %s' %(count, i[0]) 
      self.c_q.esegui_query_no_result(self.inserisci_parametri(q_agg.q_insert_drive_distance.replace('o___0', '%s'%i[0])))


def main():
  usage = "utilizzo:"+ "\n\n esegui il comando start.py senza opzioni per avviare\n\n\n"   +" %prog [opzioni] arg1 arg2"
  parser = OptionParser(usage=usage, version="%prog 1.0")
# ------------------------------------------------------------------------------------------------------------------------
# ------------- Comandi per eseguire le elaborazioni ---------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------
  parser.add_option("--aggiornamento_db", action="store_true", dest="aggiornamento_db", default=False,
    help="Questo argomento permette di avviare una procedura di controllo ed eventuale aggiornamento del db ")
# ------------------------------------------------------------------------------------------------------------------------
  parser.add_option("-q", "--esegui_query", action="store_true", dest="e_q", default=False,
    help="Lo script permette di connettersi ad un database postgresql ed effettuare delle query")


  options, args = parser.parse_args()

  opzioni_elaborazioni={
    'a_db':options.aggiornamento_db, 
    'e_q':options.e_q,
    }
  classe_avvio = esecuzione_modello(opzioni_elaborazioni)
  classe_avvio.start()


if __name__=="__main__":
    main()




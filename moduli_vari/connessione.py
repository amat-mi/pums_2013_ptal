# -*- coding: utf-8 -*-

import math
import time
import os
import psycopg2
import unittest
import StringIO
import cStringIO, array


class classe_connessione(object):
	connection = ''
	c_c = dict()        

	def __init__(self, credenziali_connessione):
		self.c_c = credenziali_connessione

	def __del__(self):
                pass

        def __connetti__(self, c_c):
                self.connection = psycopg2.connect(**c_c)
                self.connection.set_client_encoding('UTF-8')
        
        def __disconnetti__(self):
                if self.connection:
                   self.connection.close()
                   self.connection = None
                else:
                   print 'Non sono mai stato connesso'

        def test_connessione(self):
                try:
                        self.__connetti__(self.c_c)
                        self.__disconnetti__()
                        print '\nParametri di connessione corretti per il database -> %s\n'%(self.c_c['database'])
                        return 1
                except: 
                        print '\nI parametri di connessione non sono corretti\n' # TODO -> Estrarre log di sistema per postare l'errore 
                        return 0

        def esegui_test(self):
                self.__connetti__(self.c_c)
                self.__disconnetti__()
                print 'Test ok'

# Import file di testo
        def esegui_import_file(self, oggetto_file, schema, tabella):
                self.__connetti__(self.c_c)
                cur = self.connection.cursor()
                tabella_destinazione = '%s.%s'%(schema, tabella)
                cur.copy_from(oggetto_file, tabella_destinazione, sep=';')
                self.connection.commit()
                self.__disconnetti__()

	def esegui_query_import_vettore_dati(self, sql, vettore_dati):
                self.__connetti__(self.c_c)
                c = self.connection.cursor()
                v_d = []
                for i in vettore_dati:
                        for k in sql[1]:
                                v_d.append(i[k])
                        c.execute(sql[0], v_d)
                        v_d = []
                self.connection.commit()
                self.connection.close()


        def controllo_tabella(self, nome_tabella, nome_schema):
                self.__connetti__(self.c_c)
                c = self.connection.cursor()
                c.execute("select exists(select * from information_schema.tables where table_name=%s and table_schema=%s)", (nome_tabella,nome_schema))
                if c.fetchone()[0] is True:
                  return 1
                else:
                  return 0

        def controllo_schema(self, nome_schema):
                self.__connetti__(self.c_c)
                c = self.connection.cursor()
                c.execute("select exists(select * from information_schema.tables where table_schema=%s)", (nome_schema,))
                if c.fetchone()[0] is True:
                  return 1
                else:
                  return 0



        def esegui_query_result(self, testo_query):
                self.__connetti__(self.c_c)
                c = self.connection.cursor()
                c.execute(testo_query)
                output = c.fetchall()
                self.connection.commit()
                self.connection.close() 
                return output

        def esegui_query_no_result(self, testo_query):
                self.__connetti__(self.c_c)
                c = self.connection.cursor()
                c.execute(testo_query)
                self.connection.commit()
                self.connection.close()

if __name__ == '__main__':
        CONNECTION_CONFIG = {
                'database'    : 'monitoraggio_AreaC',
                'user'      : 'mt_monitoraggio',
                'password'  : 'mt_monitoraggio',
                'host'      : '192.1.1.115',
                'port'      : '5432' }
        lettura = open("/home/davide/1_ecopass/pulizia_dati/dati", 'r')
	nuova_c = classe_connessione(CONNECTION_CONFIG)
        nuova_c.esegui_import(lettura, 'areac', 'atm_transiti_test')
        lettura.close()


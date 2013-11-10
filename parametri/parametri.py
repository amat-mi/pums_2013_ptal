# ---------------------------------------------------------------------------------
# -------- PARAMENTRI -------------------------------------------------------------
# ---------------------------------------------------------------------------------
# file contenente tutti i parametri del modulo di import --------------------------
# ---------------------------------------------------------------------------------

# --- Parametri di CONNESSIONE AL DB ----------------------------------------------
# ---------------------------------------------------------------------------------
credenziali_db = {      
                  'database'    : 'monitoraggio_tpl',
                  'user'      : 'mt_monitoraggio',
                  'password'  : 'mt_monitoraggio',
                  'host'      : '192.1.1.115',
                  'port'      : '5432' 
                 }
# ---------------------------------------------------------------------------------
# --- Schemi presenti -------------------------------------------------------------

tabelle = {
#'^__grafo__^':'ptal.inp_elem_strad', 
'^__grafo__^':'ptal.elab_elem_strad', 
'^__fermate__^':'ptal.elab_tpl_fermate', 
'^__frequenze_linea__^':'ptal.elab_tpl_fermate_frequenza',
'^__nodi_fermata__^':'ptal.out_nodi_fermata' 
}


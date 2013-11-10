# ----------------------------------------------------------------------------------------------------------------------------------------
# --- QUERY di aggiornamento del db ---------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------


q_add_gid = """
ALTER TABLE ^__grafo__^ add column ogc_fid serial;
ALTER TABLE ^__grafo__^ add column gid serial;
"""

#TODO TODO --lordine delle colonne determinante per il create topology ----------
#TODO TODO --lordine delle colonne determinante per il create topology ----------
#TODO TODO --lordine delle colonne determinante per il create topology ----------
#TODO TODO --lordine delle colonne determinante per il create topology ----------
#TODO TODO --lordine delle colonne determinante per il create topology ----------
#TODO TODO --lordine delle colonne determinante per il create topology ----------

q_topologia= """ 
ALTER TABLE ^__grafo__^ ADD COLUMN "source" integer;
ALTER TABLE ^__grafo__^ ADD COLUMN "target" integer;

----------DROP INDEX ptal.inp_elem_strad_vertices_pgr_the_geom_idx;

Select pgr_createTopology('^__grafo__^', 0.0001 , 'the_geom', 'gid');

CREATE INDEX source_idx ON ^__grafo__^("source");

CREATE INDEX target_idx ON ^__grafo__^("target");

ALTER TABLE ^__grafo__^ ADD COLUMN "length" double precision;

UPDATE ^__grafo__^ SET length=st_length(the_geom);

"""


q_elimina_nodi_fermata = """
DROP table ^__nodi_fermata__^;
"""

q_crea_nodi_fermata = """
drop table ptal.out_nodi_fermata;
create table ptal.out_nodi_fermata as 
select id, cnt, chk, ein, eout, geom_t, id_fermata, id_g1 from (
select a.*, b.id_fermata, b.id_g1, st_Distance(wkb_geometry, geom_t) as dist, 
row_number() OVER (partition by id_fermata order by st_Distance(wkb_geometry, geom_t)) as dist_ord
 from 
(SELECT id, cnt, chk, ein, eout, the_geom as geom_t
  FROM ptal.elab_elem_strad_vertices_pgr
  ) as a
join
(select * from ptal.elab_tpl_fermate ) as b
on st_Dwithin(wkb_geometry, geom_t, 0.5)
) as a
where dist_ord = 1;
-----------------------------------------------------
--CREATE TABLE ptal.out_costo
--(
--  nodo_partenza integer,
--  seq integer,
--  node integer,
--  id2 integer,
--  cost double precision
--);
"""



q_elenco_nodi_fermata_veloce = """
select id from ^__nodi_fermata__^ order by id
"""


q_elenco_fermate = """
SELECT id_fermata
  FROM ^__fermate__^
order by id_fermata
"""

q_max_ogc_fid = """
SELECT max(ogc_fid) FROM ^__grafo__^ 
"""


q_aggiungo_nuovi_archi = """
INSERT INTO ^__grafo__^ ( the_geom, id, soloped, via_id, tranviario, non_pedonabile)
 ( select wkb_geometry as the_geom, id, soloped, via_id, tranviario, non_pedonabile from 
   (
    with a as ( SELECT  a.*,
                        ST_LineSubstring(geom, 0, ST_LineLocatePoint(geom, geom_f)) as geom_in, 
                        ST_LineSubstring(geom, ST_LineLocatePoint(geom, geom_f), 1) as geom_fe, 
                        b.id_fermata
                FROM ( SELECT ogc_fid, the_geom as geom, id, soloped, via_id, tranviario, non_pedonabile, gid
                       FROM ^__grafo__^  ) as a
                   JOIN
                     ( SELECT ogc_fid, wkb_geometry as geom_f, id_fermata, id_g1
                       FROM ^__fermate__^ 
                       WHERE id_fermata = '^___^'     ) as b
                   ON (a.id = b.id_g1)
                WHERE ST_LineLocatePoint(geom, geom_f) not in (1, 0)
               )
    select ogc_fid, geom_in as wkb_geometry, id, soloped, via_id, tranviario, non_pedonabile, st_endpoint(geom_in) as id_fermata
    from a
   union
    select ogc_fid, geom_fe as wkb_geometry, id, soloped, via_id, tranviario, non_pedonabile, st_startpoint(geom_fe) as id_fermata 
    from a
   ) as a
 )
"""

q_elimino_arco_old = """
--SELECT *
DELETE 
FROM ^__grafo__^ 
WHERE ogc_fid = (  select a.ogc_fid
from ( SELECT ogc_fid, the_geom as geom, id, soloped, via_id, tranviario, non_pedonabile, gid
       FROM ^__grafo__^  
       where ogc_fid <= x___X 
       ) as a
join
     (  SELECT ogc_fid, wkb_geometry as geom_f, id_fermata, id_g1
        FROM ^__fermate__^ 
        where id_fermata = '^___^'
     ) as b
ON (a.id = b.id_g1)
where ST_LineLocatePoint(geom, geom_f) not in (1, 0)
)
"""



q_insert_drive_distance = """
INSERT INTO ptal.out_costo( nodo_partenza, seq, node, id2, cost)
SELECT o___0 as nodo_partenza, seq, id1 AS node, id2, cost
FROM pgr_drivingDistance( 'SELECT gid as id, source, target, length as cost FROM ^__grafo__^', o___0, 960.001, false, false )
"""

q_crea_tabella_indice= """
create table ptal.indice_di_accessibilita as 
(SELECT id, 0 as accessibility_index, the_geom 
  FROM ptal.inp_elem_strad_vertices_pgr)
"""

q_crea_tabella_indici = """
DROP TABLE ptal.out_indici_di_accessibilita; 
create table ptal.out_indici_di_accessibilita as 
(
select id, (CASE when accessibility_index is null then 0 else accessibility_index end) as accessibility_index, the_geom
 from (
select a.*, b.accessibility_index
        from ( SELECT id, the_geom 
               FROM ^__grafo__^_vertices_pgr  ) as a
left join
(
select node, sum(accessibility_index) as accessibility_index from (
select *, edf*(CASE WHEN ordine = 1 then 1 else 0.5 end) as accessibility_index
from (  
select *, row_number() OVER (partition by node, tipologia_accesso  order by edf desc ) as ordine
from (
select *, 
round((cost/80)+((1/freq_cum_8_9*0.5)+CASE WHEN tipologia in ('Automobilistica', 'Tranviaria') then 2 else 0.75 end), 2) as tat, 
round((1/freq_cum_8_9*0.5)+CASE WHEN tipologia in ('Automobilistica', 'Tranviaria') then 2 else 0.75 end, 2) as attesa, 
round(cost/80, 2) as walktime,
round(30/((cost/80)+((1/freq_cum_8_9*0.5)+CASE WHEN tipologia in ('Automobilistica', 'Tranviaria') then 2 else 0.75 end)), 2) as edf
from (
select *, row_number() OVER (partition by node order by cost) as ord_fermate,
row_number() OVER (partition by linea, node order by cost) as ord_linee,
CASE WHEN tipologia in ('metro') then 960 else 640 end as massima_distanza,
CASE WHEN tipologia in ('metro') then 'rail' else 'buses' end as tipologia_accesso
        from 
             ( SELECT id_fermata, nodo_partenza as nodo_fermata, seq, node, round(cost::decimal, 2) as cost 
                FROM   ptal.out_costo 
                  join 
                       ptal.out_nodi_fermata 
                  on nodo_partenza = id ) as a
           join 
             ( SELECT linea, tipologia, id_fermata, freq_cum_8_9
               FROM ptal.elab_tpl_fermate_frequenza 
               WHERE freq_cum_8_9 <> 0 ) as b
           using(id_fermata)
order by node, linea, ord_linee
) as a
where ord_linee = 1
and cost <= massima_distanza
order by node, linea, ord_fermate
) as a
) as foo
) as foooo
group by node
) as b
on a.id = b.node
) as a
);
------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------
drop table ptal.out_indici_di_accessibilita_modo;
create table ptal.out_indici_di_accessibilita_modo as
(
select tipologia_accesso, node, sum(accessibility_index) as accessibility_index from (
---- SELEZIONO gli accessibile index ---
select *, edf*(CASE WHEN ordine = 1 then 1 else 0.5 end) as accessibility_index
from (  
-- seleziono lordinamento per estrarre qulli maggiori
select *, row_number() OVER (partition by node, tipologia_accesso  order by edf desc ) as ordine
from (
select *, 
--CASE WHEN seq = 0 then 1 else 0.5 end as contributo_fermata,  
round((cost/80)+((1/freq_cum_8_9*0.5)+CASE WHEN tipologia in ('Automobilistica', 'Tranviaria') then 2 else 0.75 end), 2) as tat, 
round((1/freq_cum_8_9*0.5)+CASE WHEN tipologia in ('Automobilistica', 'Tranviaria') then 2 else 0.75 end, 2) as attesa, 
round(cost/80, 2) as walktime,
round(30/((cost/80)+((1/freq_cum_8_9*0.5)+CASE WHEN tipologia in ('Automobilistica', 'Tranviaria') then 2 else 0.75 end)), 2) as edf

from (
--SELECT depname, empno, salary, avg(salary) OVER (PARTITION BY depname) FROM empsalary;
--select id_fermata, nodo_partenza, seq, node, min(cost), ord2, linea, tipologia, id_fermata, freq_cum_8_9 from (
select *, row_number() OVER (partition by node order by cost) as ord_fermate,
row_number() OVER (partition by linea, node order by cost) as ord_linee,
CASE WHEN tipologia in ('metro') then 960 else 640 end as massima_distanza,
CASE WHEN tipologia in ('metro') then 'rail' else 'buses' end as tipologia_accesso
        from 
             ( SELECT id_fermata, nodo_partenza as nodo_fermata, seq, node, round(cost::decimal, 2) as cost 
                FROM   ptal.out_costo 
                  join 
                       ptal.out_nodi_fermata 
                  on nodo_partenza = id ) as a
           join 
             ( SELECT linea, tipologia, id_fermata, freq_cum_8_9
               FROM ptal.elab_tpl_fermate_frequenza 
               WHERE freq_cum_8_9 <> 0 ) as b
           using(id_fermata)
--where seq = 0--and linea = 27 
order by node, linea, ord_linee--lineacost
--) as a group by id_fermata, nodo_partenza, seq, node, cost, ord2, linea, tipologia, id_fermata, freq_cum_8_9
) as a
where ord_linee = 1 -- vincolo che prende in considerazione solo la fermata piu vicina per ogni linea
and cost <= massima_distanza -- Vincolo sulla distanza per tipologia di fermata
--and ord_fermate in (1, 2)
order by node, linea, ord_fermate
) as a
) as foo
) as foooo
group by node, tipologia_accesso
) ;

"""

q_out_permodo = """

delete table ptal.out_indici_di_accessibilita_modo;
create table ptal.out_indici_di_accessibilita_modo as
(
select tipologia_accesso, node, sum(accessibility_index) as accessibility_index from (
---- SELEZIONO gli accessibile index ---
select *, edf*(CASE WHEN ordine = 1 then 1 else 0.5 end) as accessibility_index
from (  
-- seleziono lordinamento per estrarre qulli maggiori
select *, row_number() OVER (partition by node, tipologia_accesso  order by edf desc ) as ordine
from (
select *, 
--CASE WHEN seq = 0 then 1 else 0.5 end as contributo_fermata,  
round((cost/80)+((1/freq_cum_8_9*0.5)+CASE WHEN tipologia in ('Automobilistica', 'Tranviaria') then 2 else 0.75 end), 2) as tat, 
round((1/freq_cum_8_9*0.5)+CASE WHEN tipologia in ('Automobilistica', 'Tranviaria') then 2 else 0.75 end, 2) as attesa, 
round(cost/80, 2) as walktime,
round(30/((cost/80)+((1/freq_cum_8_9*0.5)+CASE WHEN tipologia in ('Automobilistica', 'Tranviaria') then 2 else 0.75 end)), 2) as edf

from (
--SELECT depname, empno, salary, avg(salary) OVER (PARTITION BY depname) FROM empsalary;
--select id_fermata, nodo_partenza, seq, node, min(cost), ord2, linea, tipologia, id_fermata, freq_cum_8_9 from (
select *, row_number() OVER (partition by node order by cost) as ord_fermate,
row_number() OVER (partition by linea, node order by cost) as ord_linee,
CASE WHEN tipologia in ('metro') then 960 else 640 end as massima_distanza,
CASE WHEN tipologia in ('metro') then 'rail' else 'buses' end as tipologia_accesso
        from 
             ( SELECT id_fermata, nodo_partenza as nodo_fermata, seq, node, round(cost::decimal, 2) as cost 
                FROM   ptal.out_costo 
                  join 
                       ptal.out_nodi_fermata 
                  on nodo_partenza = id ) as a
           join 
             ( SELECT linea, tipologia, id_fermata, freq_cum_8_9
               FROM ptal.elab_tpl_fermate_frequenza 
               WHERE freq_cum_8_9 <> 0 ) as b
           using(id_fermata)
--where seq = 0--and linea = 27 
order by node, linea, ord_linee--lineacost
--) as a group by id_fermata, nodo_partenza, seq, node, cost, ord2, linea, tipologia, id_fermata, freq_cum_8_9
) as a
where ord_linee = 1 -- vincolo che prende in considerazione solo la fermata piu vicina per ogni linea
and cost <= massima_distanza -- Vincolo sulla distanza per tipologia di fermata
--and ord_fermate in (1, 2)
order by node, linea, ord_fermate
) as a
) as foo
) as foooo
group by node, tipologia_accesso
) ;
-------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------
DROP TABLE ptal.out_indici_di_accessibilita_rail;
create table ptal.out_indici_di_accessibilita_buses as 
select id, (CASE when accessibility_index is null then 0 else accessibility_index end) as accessibility_index, the_geom
 from ( select a.*, b.accessibility_index
        from 
             ( SELECT id, the_geom  FROM ptal.elab_elem_strad_vertices_pgr  ) as a
           left join 
             ( SELECT tipologia_accesso, node, accessibility_index 
               FROM ptal.out_indici_di_accessibilita_modo 
               where tipologia_accesso = 'rail') as b
           on a.id = b.node
          ) as foo;
------------------------------------------------------------------------
-------------------------------------------------------------------------------
DROP TABLE ptal.out_indici_di_accessibilita_buses;
create table ptal.out_indici_di_accessibilita_buses as 
select id, (CASE when accessibility_index is null then 0 else accessibility_index end) as accessibility_index, the_geom
 from ( select a.*, b.accessibility_index
        from 
             ( SELECT id, the_geom  FROM ptal.elab_elem_strad_vertices_pgr  ) as a
           left join 
             ( SELECT tipologia_accesso, node, accessibility_index 
               FROM ptal.out_indici_di_accessibilita_modo 
               where tipologia_accesso = 'buses') as b
           on a.id = b.node
          ) as foo;
"""


q_out = """

ANALISI DEL GRAFO

NOTICE:  PROCESSING:
NOTICE:  pgr_analyzeGraph('ptal.inp_elem_strad',2e-06,'the_geom','id','source','target','true')
NOTICE:  Performing checks, pelase wait...
NOTICE:  Analyzing for dead ends. Please wait...
NOTICE:  Analyzing for gaps. Please wait...
NOTICE:  Analyzing for isolated edges. Please wait...
NOTICE:  Analyzing for ring geometries. Please wait...
NOTICE:  Analyzing for intersections. Please wait...
NOTICE:              ANALYSIS RESULTS FOR SELECTED EDGES:
NOTICE:                    Isolated segments: 44
NOTICE:                            Dead ends: 22482
NOTICE:  Potential gaps found near dead ends: 1
NOTICE:               Intersections detected: 2298
NOTICE:                      Ring geometries: 0

Total query runtime: 52434 ms.
1 row retrieved.




DROP TABLE ptal.out_costo_minimo_per_nodo;
create table ptal.out_costo_minimo_per_nodo as 
 ( select a.*, b.costo_minimo
        from 
             ( SELECT id, the_geom  FROM ptal.elab_elem_strad_vertices_pgr  ) as a
           join 
             ( select node, min(cost) as costo_minimo from (
SELECT id_fermata, nodo_partenza as nodo_fermata, seq, node, round(cost::decimal, 2) as cost 
                FROM   ptal.out_costo 
                  join 
                       ptal.out_nodi_fermata 
                  on nodo_partenza = id) as a
group by node

               ) as b
           on a.id = b.node
          )

"""



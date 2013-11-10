q = """
--select *--st_length(geom), st_srid(geom) 
--from 
drop table ptal.es_split2;
create table ptal.es_split2 as 
(
-------------------------------------------------
-- 1 rimozione archi che non ci interessano --------------
-------------------------------------------------------
with a as (
select gid, id_g1, length, lunghezza, source, target, reverse_cost, 
--(st_dumppoints(geom)).geom as geom, 
ST_LineSubstring(geom, 0, ST_LineLocatePoint(geom, geom_f)) as geom_i, 
ST_LineSubstring(geom, ST_LineLocatePoint(geom, geom_f), 1) as geom_f
--, ST_AddPoint(geom, geom_f) as geom
 from 
(SELECT gid, geom, id_g1, length, lunghezza, source, target, reverse_cost
  FROM ptal.archistradali 
--  where gid = 26224
) as a
join
(
  SELECT gid, geom as geom_f
  FROM ptal.fermate_proiettate
 ) as b
 using(gid)
 )
select (500000 + gid) as gid, id_g1, length, st_length(geom_i) as lunghezza, source, target, reverse_cost, geom_i as geom from a
union
select (800000 + gid) as gid, id_g1, length, st_length(geom_f) as lunghezza, source, target, reverse_cost, geom_f as geom from a
 
)-- as a

""" %(gid)

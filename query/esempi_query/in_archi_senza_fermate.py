q="""
insert 
SELECT gid, geom, id_g1, length, lunghezza, source, target, reverse_cost
  FROM ptal.archistradali 
  where gid not in (
                      SELECT gid
                      FROM ptal.fermate_proiettate 
                      group by gid
                   ) 
"""

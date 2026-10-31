-- Que entro al almacen. Cada fila la escribio el ETL al cargar, con el hash del archivo leido.
SELECT id_fuente, publicador, nombre, archivo, tabla_destino, filas, bytes,
       LEFT(sha256, 16) AS sha256_inicio, md5_oficial_coincide, doi
FROM   control_ingesta_fuentes
ORDER  BY id_ingesta;

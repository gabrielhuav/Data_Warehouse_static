-- Filas reales de cada tabla, contadas en este momento.
SELECT t.table_name AS tabla,
       (xpath('/row/n/text()',
              query_to_xml(format('SELECT count(*) AS n FROM %I', t.table_name), FALSE, TRUE, '')))[1]::TEXT::BIGINT AS filas
FROM   information_schema.tables t
WHERE  t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
ORDER  BY t.table_name;

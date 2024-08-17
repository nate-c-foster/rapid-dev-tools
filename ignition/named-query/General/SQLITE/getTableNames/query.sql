SELECT '' as 'TABLE_SCHEMA', name as 'TABLE_NAME'FROM sqlite_master
WHERE type == 'table' and name != 'sqlite_sequence'
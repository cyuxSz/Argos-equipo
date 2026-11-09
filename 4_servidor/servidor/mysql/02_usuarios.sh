#!/bin/bash
# Corre UNA vez, al crear la base por primera vez (despues de 01_esquema.sql).
# Las variables llegan del compose.
mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<EOSQL
CREATE USER 'argos_escritura'@'%' IDENTIFIED BY '${MYSQL_PASSWORD_ESCRITURA}';
GRANT SELECT, INSERT, UPDATE ON argos.* TO 'argos_escritura'@'%';

CREATE USER 'argos_lectura'@'%' IDENTIFIED BY '${MYSQL_PASSWORD_LECTURA}';
GRANT SELECT ON argos.Medicion   TO 'argos_lectura'@'%';
GRANT SELECT ON argos.Sensor     TO 'argos_lectura'@'%';
GRANT SELECT ON argos.Parametro  TO 'argos_lectura'@'%';
GRANT SELECT ON argos.Alerta     TO 'argos_lectura'@'%';
GRANT SELECT ON argos.EstadoNodo TO 'argos_lectura'@'%';
EOSQL

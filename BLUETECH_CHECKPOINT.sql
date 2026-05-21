USE bluetech;

-- Le asignamos el ID 20.
INSERT INTO `sensor` (`id_sensor`, `estado`, `fecha_instalacion`, `fk_id_habitacion`, `fk_id_parametro`, `consumo`, `tipo_sensor`) 
VALUES (20, 'Activo', '2026-05-21', 1, 3, '4.15', 'Multiordinario');

INSERT INTO `medicion` (`fecha_hora`, `valor`, `fk_id_sensor`) VALUES 
(NOW(), 1, 20);

SELECT 
    id_medicion AS 'ID',
    fecha_hora AS 'Fecha/Hora',
    fk_id_sensor AS 'ID Sensor',
    valor AS 'Valor Entero (BD)',
    CASE valor
        WHEN 0 THEN 'BAJO'
        WHEN 1 THEN 'NORMAL'
        WHEN 2 THEN 'ALTO'
        ELSE 'DESCONOCIDO'
    END AS 'Valor Alfanumérico'
FROM medicion
WHERE fk_id_sensor = 20;
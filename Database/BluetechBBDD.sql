-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: bluetech
-- ------------------------------------------------------
-- Server version 8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE IF NOT EXISTS bluetech;
USE bluetech;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `id_rol` int NOT NULL,
  `nombre` varchar(45) NOT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'trabajador'),(2,'administrador'),(3,'tecnico');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `habitacion`
--

DROP TABLE IF EXISTS `habitacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `habitacion` (
  `id_habitacion` int NOT NULL AUTO_INCREMENT,
  `tipo_sala` varchar(45) NOT NULL,
  `estado` varchar(45) NOT NULL,
  PRIMARY KEY (`id_habitacion`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `habitacion`
--

LOCK TABLES `habitacion` WRITE;
/*!40000 ALTER TABLE `habitacion` DISABLE KEYS */;
INSERT INTO habitacion (id_habitacion, tipo_sala, estado) VALUES (1, 'S.hospitalizacion', 'libre'), (2, 'S.hospitalizacion', 'libre'), (3, 'S.hospitalizacion', 'libre'), (4, 'S.hospitalizacion', 'libre'), (5, 'S.hospitalizacion', 'libre');
/*!40000 ALTER TABLE `habitacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parametro`
--

DROP TABLE IF EXISTS `parametro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parametro` (
  `id_parametro` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `unidad` varchar(50) NOT NULL,
  PRIMARY KEY (`id_parametro`),
  UNIQUE KEY `nombre_UNIQUE` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parametro`
--

LOCK TABLES `parametro` WRITE;
/*!40000 ALTER TABLE `parametro` DISABLE KEYS */;
INSERT INTO `parametro` VALUES (1,'Temperatura','Rango térmico óptimo normativo para confort y salud (ej. 21 a 24 grados)','°C'),(2,'Humedad Relativa','Nivel para minimizar proliferación de patógenos y sequedad (ej. 40% a 60%)','%'),(3,'Calidad del Aire (CO2)','Niveles de dióxido de carbono permitidos por sanidad (ej. < 800 ppm)','ppm');
/*!40000 ALTER TABLE `parametro` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensor`
--

DROP TABLE IF EXISTS `sensor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensor` (
  `id_sensor` int NOT NULL AUTO_INCREMENT,
  `estado` varchar(45) NOT NULL,
  `fecha_instalacion` varchar(45) NOT NULL,
  `fk_id_habitacion` int NOT NULL,
  `fk_id_parametro` int NOT NULL,
  `consumo` varchar(45) NOT NULL,
  `tipo_sensor` varchar(45) NOT NULL,
  PRIMARY KEY (`id_sensor`),
  KEY `fk_id_habitacion_idx` (`fk_id_habitacion`),
  KEY `fk_id_parametro_idx` (`fk_id_parametro`),
  CONSTRAINT `fk_id_habitacion` FOREIGN KEY (`fk_id_habitacion`) REFERENCES `habitacion` (`id_habitacion`),
  CONSTRAINT `fk_id_parametro` FOREIGN KEY (`fk_id_parametro`) REFERENCES `parametro` (`id_parametro`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor`
--

LOCK TABLES `sensor` WRITE;
/*!40000 ALTER TABLE `sensor` DISABLE KEYS */;
-- Sensores estándar originales (Toman los IDs del 1 al 15 automáticamente)
INSERT INTO sensor (estado, fecha_instalacion, fk_id_habitacion, fk_id_parametro, consumo, tipo_sensor) VALUES 
('Activo', '2026-03-28', 1, 1, '5.05', 'Temperatura'), 
('Activo', '2026-03-28', 1, 2, '3.62', 'Humedad'), 
('Activo', '2026-03-28', 1, 3, '9.26', 'Calidad de Aire'), 
('Activo', '2026-03-28', 2, 1, '5.05', 'Temperatura'), 
('Activo', '2026-03-28', 2, 2, '3.62', 'Humedad'), 
('Activo', '2026-03-28', 2, 3, '9.26', 'Calidad de Aire'), 
('Activo', '2026-03-28', 3, 1, '5.05', 'Temperatura'), 
('Activo', '2026-03-28', 3, 2, '3.62', 'Humedad'), 
('Activo', '2026-03-28', 3, 3, '9.26', 'Calidad de Aire'), 
('Activo', '2026-03-28', 4, 1, '5.05', 'Temperatura'), 
('Activo', '2026-03-28', 4, 2, '3.62', 'Humedad'), 
('Activo', '2026-03-28', 4, 3, '9.26', 'Calidad de Aire'), 
('Activo', '2026-03-28', 5, 1, '5.05', 'Temperatura'), 
('Activo', '2026-03-28', 5, 2, '3.62', 'Humedad'), 
('Activo', '2026-03-28', 5, 3, '9.26', 'Calidad de Aire');

-- INTEGRACIÓN: Alta explícita del Sensor Multiordinario forzando su ID a 20 para sincronizarlo con app.py
INSERT INTO sensor (id_sensor, estado, fecha_instalacion, fk_id_habitacion, fk_id_parametro, consumo, tipo_sensor) 
VALUES (20, 'Activo', '2026-05-21', 1, 3, '4.15', 'Multiordinario');
/*!40000 ALTER TABLE `sensor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre_usuario` varchar(45) NOT NULL,
  `nombre` varchar(45) NOT NULL,
  `apellido` varchar(45) NOT NULL,
  `num_registro` int NOT NULL,
  `fk_id_rol` int NOT NULL,
  `estado` int NOT NULL,
  `password_hash` varchar(200) NOT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `nombre_usuario_UNIQUE` (`nombre_usuario`),
  KEY `fk_id_rol_idx` (`fk_id_rol`),
  CONSTRAINT `fk_id_rol` FOREIGN KEY (`fk_id_rol`) REFERENCES `rol` (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=3002 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (2001,'dnovo','David','Novo Rodríguez',25,2,1,'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3'), (1001,'lucy','Lucia','Fernandez Gomez',3,1,1,'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'), (3001,'serg','Sergio','Vadillo Rodríguez',2,3,1,'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alerta`
--

DROP TABLE IF EXISTS `alerta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alerta` (
  `id_alerta` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `id_habitacion` int NOT NULL,
  `id_sensor` int NOT NULL,
  `nombre_emisor` varchar(100) NOT NULL,
  `tipo_sensor` varchar(45) NOT NULL,
  `valor_detectado` int NOT NULL,
  `limite_establecido` varchar(45) NOT NULL,
  `descripcion` varchar(300) DEFAULT NULL,
  `estado` varchar(45) NOT NULL,
  `tecnico_id` int DEFAULT NULL,
  `tecnico_nombre` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_alerta`),
  KEY `fk_id_habitacion_idx` (`id_habitacion`),
  KEY `fk_id_sensor_idx` (`id_sensor`),
  KEY `fk_tecnico_idx` (`tecnico_id`),
  CONSTRAINT `fk_alerta_habitacion` FOREIGN KEY (`id_habitacion`) REFERENCES `habitacion` (`id_habitacion`),
  CONSTRAINT `fk_alerta_sensor` FOREIGN KEY (`id_sensor`) REFERENCES `sensor` (`id_sensor`),
  CONSTRAINT `fk_alerta_tecnico` FOREIGN KEY (`tecnico_id`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alerta`
--

LOCK TABLES `alerta` WRITE;
/*!40000 ALTER TABLE `alerta` DISABLE KEYS */;
INSERT INTO `alerta` VALUES (1, '2026-04-01 12:06:24', 1, 1, 'Sistema Automático', 'Temperatura', 40, '22.0 - 28.0 °C', 'Nivel crítico de Temperatura: 40', 'Pendiente', NULL, NULL), (2, '2026-04-02 10:06:24', 1, 2, 'Sistema Automático', 'Humedad', 60, '34.0 - 40.0 %', 'Nivel crítico de Humedad: 60', 'Pendiente', NULL, NULL), (3, '2026-04-02 11:06:24', 1, 3, 'Sistema Automático', 'Calidad de Aire', 600, '500.0 ppm', 'Nivel crítico de CO2: 600', 'Pendiente', NULL, NULL);
/*!40000 ALTER TABLE `alerta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicion`
--

DROP TABLE IF EXISTS `medicion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicion` (
  `id_medicion` int NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime NOT NULL,
  `valor` int NOT NULL,
  `fk_id_sensor` int DEFAULT NULL,
  PRIMARY KEY (`id_medicion`),
  KEY `fk_id_sensor_idx` (`fk_id_sensor`),
  CONSTRAINT `fk_id_sensor` FOREIGN KEY (`fk_id_sensor`) REFERENCES `sensor` (`id_sensor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicion`
--

LOCK TABLES `medicion` WRITE;
/*!40000 ALTER TABLE `medicion` DISABLE KEYS */;
-- Inserciones iniciales de tus sensores estándar
INSERT INTO medicion (fecha_hora, valor, fk_id_sensor) VALUES
(NOW(), 23, 1),(NOW(), 45, 2),(NOW(), 400, 3),
(NOW(), 24, 4),(NOW(), 50, 5),(NOW(), 420, 6),
(NOW(), 22, 7),(NOW(), 48, 8),(NOW(), 390, 9),
(NOW(), 25, 10),(NOW(), 55, 11),(NOW(), 410, 12),
(NOW(), 23, 13),(NOW(), 47, 14),(NOW(), 405, 15);

-- INTEGRACIÓN: Simulación de envíos de la media de 1 minuto procesada por Flask para el sensor multiordinario (ID 20)
INSERT INTO medicion (fecha_hora, valor, fk_id_sensor) VALUES
(NOW() - INTERVAL 2 MINUTE, 0, 20), -- Mapea en Flask desde "BAJO"
(NOW() - INTERVAL 1 MINUTE, 1, 20), -- Mapea en Flask desde "NORMAL"
(NOW(),                     2, 20); -- Mapea en Flask desde "ALTO"
/*!40000 ALTER TABLE `medicion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticket` (
  `id_ticket` int NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime NOT NULL,
  `estado` varchar(45) NOT NULL,
  `descripcion` varchar(500) NOT NULL,
  `id_rol_emisor` varchar(45) NOT NULL,
  `nombre_emisor` varchar(100) DEFAULT NULL,
  `nombre_tecnico` varchar(100) DEFAULT NULL,
  `id_emisor` int NOT NULL,
  `id_tecnico` int DEFAULT NULL,
  PRIMARY KEY (`id_ticket`),
  KEY `fk_ticket_emisor_idx` (`id_emisor`),
  KEY `fk_ticket_tecnico_idx` (`id_tecnico`),
  CONSTRAINT `fk_ticket_emisor` FOREIGN KEY (`id_emisor`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_ticket_tecnico` FOREIGN KEY (`id_tecnico`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `ticket` WRITE;
/*!40000 ALTER TABLE `ticket` DISABLE KEYS */;
/*!40000 ALTER TABLE `ticket` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mensajes`
--

DROP TABLE IF EXISTS `mensajes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mensajes` (
  `id_mensaje` int NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime NOT NULL,
  `texto` text NOT NULL,
  `rol` varchar(45) NOT NULL,
  `nombre_emisor` varchar(100) NOT NULL,
  `id_ticket` int NOT NULL,
  `id_emisor` int NOT NULL,
  PRIMARY KEY (`id_mensaje`),
  KEY `fk_msj_ticket_idx` (`id_ticket`),
  KEY `fk_msj_usuario_idx` (`id_emisor`),
  CONSTRAINT `fk_msj_ticket` FOREIGN KEY (`id_ticket`) REFERENCES `ticket` (`id_ticket`),
  CONSTRAINT `fk_msj_usuario` FOREIGN KEY (`id_emisor`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `mensajes` WRITE;
/*!40000 ALTER TABLE `mensajes` DISABLE KEYS */;
/*!40000 ALTER TABLE `mensajes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `valores_comparativos`
--

DROP TABLE IF EXISTS `valores_comparativos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `valores_comparativos` (
  `id_rango` int NOT NULL,
  `min` varchar(45),
  `max` varchar(45) NOT NULL,
  `id_parametro` int NOT NULL,
  UNIQUE KEY `id_rango_UNIQUE` (`id_rango`),
  KEY `id_parametro_idx` (`id_parametro`),
  CONSTRAINT `id_valor_parametro` FOREIGN KEY (`id_parametro`) REFERENCES `parametro` (`id_parametro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `valores_comparativos` WRITE;
/*!40000 ALTER TABLE `valores_comparativos` DISABLE KEYS */;
INSERT INTO `valores_comparativos` (`id_rango`, `min`, `max`, `id_parametro`) VALUES(1, '22.0', '28.0', 1), (2, '34.0', '40.0', 2), (3, NULL, '500.0', 3);
/*!40000 ALTER TABLE `valores_comparativos` ENABLE KEYS */;
UNLOCK TABLES;


-- ─────────────────────────────────────────────────────────────
-- INTEGRACIÓN: CONSULTA DE COMPROBACIÓN (SELECT MAPEADO)
-- ─────────────────────────────────────────────────────────────
-- Al final del archivo se adjunta la sentencia solicitada para visualizar
-- el histórico del sensor multiordinario traduciendo los enteros a texto.

SELECT 
    m.id_medicion AS 'ID Registro',
    m.fecha_hora AS 'Fecha y Hora',
    s.tipo_sensor AS 'Sensor',
    m.fk_id_sensor AS 'ID Sensor (FK)',
    m.valor AS 'Valor Numérico Interno',
    CASE m.valor
        WHEN 0 THEN 'BAJO'
        WHEN 1 THEN 'NORMAL'
        WHEN 2 THEN 'ALTO'
        ELSE 'DESCONOCIDO'
    END AS 'Media Calculada (Alfanumérico)'
FROM medicion m
INNER JOIN sensor s ON m.fk_id_sensor = s.id_sensor
WHERE m.fk_id_sensor = 20
ORDER BY m.fecha_hora DESC;


/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-21 17:02:17
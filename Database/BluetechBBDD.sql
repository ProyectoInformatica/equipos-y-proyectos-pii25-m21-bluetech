-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: bluetech
-- ------------------------------------------------------
-- Server version	8.0.45

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
INSERT INTO `rol` VALUES (1,'administrador'),(2,'trabajador'),(3,'supervisor'),(4,'invitado');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor`
--

LOCK TABLES `sensor` WRITE;
/*!40000 ALTER TABLE `sensor` DISABLE KEYS */;
INSERT INTO sensor (estado, fecha_instalacion, fk_id_habitacion, fk_id_parametro, consumo, tipo_sensor) VALUES ('Activo', '2026-03-28', 1, 1, 5.05, 'Temperatura'), ('Activo', '2026-03-28', 1, 2, 3.62, 'Humedad'), ('Activo', '2026-03-28', 1, 4, 9.26, 'Calidad de Aire'), ('Activo', '2026-03-28', 2, 1, 5.05, 'Temperatura'), ('Activo', '2026-03-28', 2, 2, 3.62, 'Humedad'), ('Activo', '2026-03-28', 2, 4, 9.26, 'Calidad de Aire'), ('Activo', '2026-03-28', 3, 1, 5.05, 'Temperatura'), ('Activo', '2026-03-28', 3, 2, 3.62, 'Humedad'), ('Activo', '2026-03-28', 3, 4, 9.26, 'Calidad de Aire'), ('Activo', '2026-03-28', 4, 1, 5.05, 'Temperatura'), ('Activo', '2026-03-28', 4, 2, 3.62, 'Humedad'), ('Activo', '2026-03-28', 4, 4, 9.26, 'Calidad de Aire'), ('Activo', '2026-03-28', 5, 1, 5.05, 'Temperatura'), ('Activo', '2026-03-28', 5, 2, 3.62, 'Humedad'), ('Activo', '2026-03-28', 5, 4, 9.26, 'Calidad de Aire');
/*!40000 ALTER TABLE `sensor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alerta`
--

CREATE TABLE `alerta` (
  `id_alerta` int NOT NULL AUTO_INCREMENT,
  `estado` varchar(45) NOT NULL,
  `fecha_hora` datetime NOT NULL,
  `descripcion` varchar(150) NOT NULL,
  `valor_detectado` varchar(45) NOT NULL,
  `nombre_emisor` varchar(45) NOT NULL,
  `tipo_sensor` varchar(45) NOT NULL,
  `fk_id_sensor` int NOT NULL,
  PRIMARY KEY (`id_alerta`),
  KEY `id_sensor_idx` (`fk_id_sensor`),
  KEY `fk_tipo_sensro_idx` (`tipo_sensor`),
  CONSTRAINT `id_sensor` FOREIGN KEY (`fk_id_sensor`) REFERENCES `sensor` (`id_sensor`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alerta`
--

LOCK TABLES `alerta` WRITE;
/*!40000 ALTER TABLE `alerta` DISABLE KEYS */;
INSERT INTO `alerta` VALUES (1,'No Atendida','2023-10-28 14:30:00','Temperatura máxima superada en sala de aislamiento','26.5','Unidad Central Monitoreo','Temperatura',1),(2,'Atendida','2023-10-28 15:45:00','Niveles de CO2 críticos, requiere ventilación urgente','950.0','Nodo Planta 1','Calidad de Aire',4),(3,'Pendiente','2023-10-29 08:15:00','Humedad por debajo del umbral mínimo permitido','35.0','Módulo Sensor H2','Humedad',2),(4,'Falsa Alarma','2023-10-29 11:20:00','Pico de temperatura anómalo (posible fallo de lectura)','45.0','Unidad Central Monitoreo','Temperatura',3);
/*!40000 ALTER TABLE `alerta` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
/*!40000 ALTER TABLE `medicion` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=3006 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (3001,'mrodriguez','Miguel','Rodríguez Silva',12,1,1,'5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),(3002,'pperez','Patricia','Pérez Gómez',15,2,1,'8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'),(3003,'sgomez','Sergio','Gómez Ruiz',18,2,2,'03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'),(3004,'aruiz','Alba','Ruiz Marín',22,2,1,'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f'),(3005,'jlopez','Juan','López Díaz',25,1,3,'240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticket` (
  `id_ticket` int NOT NULL,
  `estado` varchar(45) NOT NULL,
  `fecha_hora` datetime NOT NULL,
  `descripcion` varchar(300) DEFAULT NULL,
  `id_usuario` int NOT NULL,
  `fk_id_rol` int NOT NULL,
  PRIMARY KEY (`id_ticket`),
  KEY `id_usuario_idx` (`id_usuario`),
  KEY `id_rol_idx` (`fk_id_rol`),
  CONSTRAINT `id_rol` FOREIGN KEY (`fk_id_rol`) REFERENCES `rol` (`id_rol`),
  CONSTRAINT `id_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ticket`
--

LOCK TABLES `ticket` WRITE;
/*!40000 ALTER TABLE `ticket` DISABLE KEYS */;
INSERT INTO `ticket` VALUES (1,'Pendiente','2023-11-01 09:15:00','Problema con el acceso a la red wifi en la planta 2',3001,2),(2,'En proceso','2023-11-02 10:30:00','Actualización de software requerida en el equipo principal',3002,2),(3,'Resuelto','2023-11-03 11:45:00','Revisión de permisos de base de datos completada',3001,1),(4,'Pendiente','2023-11-04 14:20:00','Solicitud de nuevo monitor por parpadeo de pantalla',3001,1),(5,'Cerrado','2023-11-05 16:00:00','Mantenimiento preventivo de servidores programado',3002,1);
/*!40000 ALTER TABLE `ticket` ENABLE KEYS */;
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

--
-- Dumping data for table `valores_comparativos`
--

LOCK TABLES `valores_comparativos` WRITE;
/*!40000 ALTER TABLE `valores_comparativos` DISABLE KEYS */;
INSERT INTO `valores_comparativos` (`id_rango`, `min`, `max`, `id_parametro`) VALUES(1, '22.0', '28.0', 1), (2, '34.0', '40.0', 2), (3, NULL, '500.0', 3);
/*!40000 ALTER TABLE `valores_comparativos` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-24 17:02:17

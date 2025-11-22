-- Triggers para el cálculo automático de horas extras
-- Ejecutar este script en la base de datos `sobretiempos`

USE sobretiempos;

DELIMITER $$

-- -----------------------------------------------------------------------------
-- Trigger: trg_calcular_horas_extras_insert
-- Descripción: Calcula H25, H35 y H100 automáticamente al insertar una asistencia.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_calcular_horas_extras_insert $$
CREATE TRIGGER trg_calcular_horas_extras_insert
BEFORE INSERT ON reporte_asistencia
FOR EACH ROW
BEGIN
    DECLARE v_hora_salida_turno TIME;
    DECLARE v_minutos_extras INT;
    DECLARE v_horas_extras DECIMAL(5,2);
    
    -- 1. Obtener la hora de salida programada del turno
    SELECT hora_salida INTO v_hora_salida_turno
    FROM turnos
    WHERE codigo_turno = NEW.codigo_turno;
    
    -- 2. Inicializar valores en 0
    SET NEW.H25 = 0;
    SET NEW.H35 = 0;
    SET NEW.H100 = 0;
    
    -- 3. Validar que existan ambas marcas y el turno
    IF NEW.marca_salida IS NOT NULL AND v_hora_salida_turno IS NOT NULL THEN
        
        -- Calcular diferencia en minutos (Marca Real - Salida Turno)
        SET v_minutos_extras = TIMESTAMPDIFF(MINUTE, v_hora_salida_turno, NEW.marca_salida);
        
        -- Solo procesar si hay tiempo extra positivo (tolerancia de 0 min)
        IF v_minutos_extras > 0 THEN
            SET v_horas_extras = v_minutos_extras / 60.0;
            
            -- Lógica de Domingo (WEEKDAY: 0=Lunes ... 6=Domingo)
            IF WEEKDAY(NEW.fecha) = 6 THEN
                -- Domingos: Todo al 100%
                SET NEW.H100 = v_horas_extras;
            ELSE
                -- Días normales: Primeras 2 horas al 25%, resto al 35%
                IF v_horas_extras <= 2 THEN
                    SET NEW.H25 = v_horas_extras;
                ELSE
                    SET NEW.H25 = 2;
                    SET NEW.H35 = v_horas_extras - 2;
                END IF;
            END IF;
        END IF;
    END IF;
END $$

-- -----------------------------------------------------------------------------
-- Trigger: trg_calcular_horas_extras_update
-- Descripción: Recalcula H25, H35 y H100 automáticamente al actualizar una asistencia.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_calcular_horas_extras_update $$
CREATE TRIGGER trg_calcular_horas_extras_update
BEFORE UPDATE ON reporte_asistencia
FOR EACH ROW
BEGIN
    DECLARE v_hora_salida_turno TIME;
    DECLARE v_minutos_extras INT;
    DECLARE v_horas_extras DECIMAL(5,2);
    
    -- Optimización: Solo recalcular si cambian las marcas, el turno o la fecha
    IF NOT (NEW.marca_salida <=> OLD.marca_salida AND NEW.codigo_turno <=> OLD.codigo_turno AND NEW.fecha <=> OLD.fecha) THEN
        
        -- 1. Obtener la hora de salida programada del turno
        SELECT hora_salida INTO v_hora_salida_turno
        FROM turnos
        WHERE codigo_turno = NEW.codigo_turno;
        
        -- 2. Inicializar valores en 0
        SET NEW.H25 = 0;
        SET NEW.H35 = 0;
        SET NEW.H100 = 0;
        
        -- 3. Validar que existan ambas marcas y el turno
        IF NEW.marca_salida IS NOT NULL AND v_hora_salida_turno IS NOT NULL THEN
            
            -- Calcular diferencia en minutos (Marca Real - Salida Turno)
            SET v_minutos_extras = TIMESTAMPDIFF(MINUTE, v_hora_salida_turno, NEW.marca_salida);
            
            -- Solo procesar si hay tiempo extra positivo
            IF v_minutos_extras > 0 THEN
                SET v_horas_extras = v_minutos_extras / 60.0;
                
                -- Lógica de Domingo (WEEKDAY: 0=Lunes ... 6=Domingo)
                IF WEEKDAY(NEW.fecha) = 6 THEN
                    -- Domingos: Todo al 100%
                    SET NEW.H100 = v_horas_extras;
                ELSE
                    -- Días normales: Primeras 2 horas al 25%, resto al 35%
                    IF v_horas_extras <= 2 THEN
                        SET NEW.H25 = v_horas_extras;
                    ELSE
                        SET NEW.H25 = 2;
                        SET NEW.H35 = v_horas_extras - 2;
                    END IF;
                END IF;
            END IF;
        END IF;
    END IF;
END $$

DELIMITER ;

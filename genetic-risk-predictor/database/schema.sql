-- SQL Server Schema for Genetic Risk Predictor
-- Run this script once to create the database and table.

-- Create database (run separately if needed)
-- CREATE DATABASE GeneticRiskPredictor;
-- GO
-- USE GeneticRiskPredictor;
-- GO

CREATE TABLE IF NOT EXISTS predictions (
    id               INTEGER IDENTITY(1,1) PRIMARY KEY,
    patient_name     NVARCHAR(100)   NOT NULL,
    age              INTEGER         NOT NULL,
    bmi              FLOAT           NOT NULL,
    blood_pressure   INTEGER         NOT NULL,
    cholesterol      INTEGER         NOT NULL,
    glucose          INTEGER         NOT NULL,
    smoking          BIT             NOT NULL DEFAULT 0,
    family_history   BIT             NOT NULL DEFAULT 0,
    physical_activity INTEGER        NOT NULL DEFAULT 0,
    alcohol_use      BIT             NOT NULL DEFAULT 0,
    genetic_marker_1 BIT             NOT NULL DEFAULT 0,
    genetic_marker_2 BIT             NOT NULL DEFAULT 0,
    genetic_marker_3 BIT             NOT NULL DEFAULT 0,
    genetic_marker_4 BIT             NOT NULL DEFAULT 0,
    genetic_marker_5 BIT             NOT NULL DEFAULT 0,
    risk_probability FLOAT           NOT NULL,
    risk_level       NVARCHAR(10)    NOT NULL,
    created_at       DATETIME        NOT NULL DEFAULT GETDATE()
);
GO

-- Index for faster history queries
CREATE INDEX idx_predictions_created ON predictions(created_at DESC);
GO

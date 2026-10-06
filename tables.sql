CREATE DATABASE CurrencyDB;
GO

USE CurrencyDB;
GO

CREATE TABLE exchange_rates (
    id INT IDENTITY(1,1) PRIMARY KEY,
    base_currency VARCHAR(10),
    target_currency VARCHAR(10),
    exchange_rate FLOAT,
    api_last_update VARCHAR(100),
    fetched_at DATETIME
);
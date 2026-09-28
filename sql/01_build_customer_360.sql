CREATE OR REPLACE TABLE customer_360 AS
SELECT
    c.CustomerID,
    c.Age,
    CASE
        WHEN c.Age BETWEEN 18 AND 24 THEN '18-24'
        WHEN c.Age BETWEEN 25 AND 34 THEN '25-34'
        WHEN c.Age BETWEEN 35 AND 44 THEN '35-44'
        WHEN c.Age BETWEEN 45 AND 54 THEN '45-54'
        WHEN c.Age BETWEEN 55 AND 64 THEN '55-64'
        ELSE '65+'
    END AS AgeGroup,
    c.Gender,
    c.Location,
    c.ComChannel,
    c.DependentChildren,
    c.MotorID,
    c.HealthID,
    c.TravelID,
    m.MotorType,
    m.MotorAnnualPremium,
    h.HealthType,
    h.HealthAnnualPremium,
    t.TravelType,
    t.TravelAnnualPremium,
    CAST(c.MotorID IS NOT NULL AS INTEGER) AS HasMotor,
    CAST(c.HealthID IS NOT NULL AS INTEGER) AS HasHealth,
    CAST(c.TravelID IS NOT NULL AS INTEGER) AS HasTravel,
    CAST(c.MotorID IS NOT NULL AS INTEGER)
        + CAST(c.HealthID IS NOT NULL AS INTEGER)
        + CAST(c.TravelID IS NOT NULL AS INTEGER) AS PolicyCount,
    COALESCE(m.MotorAnnualPremium, 0)
        + COALESCE(h.HealthAnnualPremium, 0)
        + COALESCE(t.TravelAnnualPremium, 0) AS TotalAnnualPremium
FROM customers AS c
LEFT JOIN motor_policies AS m ON c.MotorID = m.MotorID
LEFT JOIN health_policies AS h ON c.HealthID = h.HealthID
LEFT JOIN travel_policies AS t ON c.TravelID = t.TravelID;


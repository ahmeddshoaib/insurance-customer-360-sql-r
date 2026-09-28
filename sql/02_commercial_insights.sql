-- Product penetration and multi-policy base.
SELECT
    COUNT(*) AS total_customers,
    SUM(HasMotor) AS motor_customers,
    SUM(HasHealth) AS health_customers,
    SUM(HasTravel) AS travel_customers,
    SUM(CASE WHEN PolicyCount = 3 THEN 1 ELSE 0 END) AS triple_policy_customers,
    SUM(CASE WHEN PolicyCount = 0 THEN 1 ELSE 0 END) AS no_policy_customers
FROM customer_360;

-- Contact strategy by age and location.
SELECT
    AgeGroup,
    Location,
    ComChannel,
    COUNT(*) AS customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY AgeGroup, Location), 2) AS segment_share_pct
FROM customer_360
GROUP BY AgeGroup, Location, ComChannel
ORDER BY AgeGroup, Location, customers DESC;

-- Cross-sell candidates: one product only, with preferred channel retained.
SELECT
    CustomerID,
    AgeGroup,
    Location,
    ComChannel,
    HasMotor,
    HasHealth,
    HasTravel,
    TotalAnnualPremium
FROM customer_360
WHERE PolicyCount = 1
ORDER BY TotalAnnualPremium DESC, CustomerID;


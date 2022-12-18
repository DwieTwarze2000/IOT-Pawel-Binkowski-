SELECT SUM(i.GoodCount) as SumOfGoodCount, SUM(i.BadCount) as SumOfBadCount, i.WorkorderId
INTO ProductionKPI
FROM iotHub as i
GROUP BY i.WorkorderId, TumblingWindow(second,10); 

SELECT (SUM(i.GoodCount)+SUM(i.BadCount)) as TotalProduction, SUM(i.GoodCount)/(SUM(i.GoodCount)+SUM(i.BadCount))*100 AS KpiPercentage
INTO ProductionPerWorkerId
FROM iotHub as i
GROUP BY TumblingWindow(minute, 15)

SELECT AVG(i.Temperature) as AverageTemperature, MAX(i.Temperature) as MaximalTemperature, MIN(i.Temperature) as MinimalTemperature, i.WorkorderId
INTO TemperaturePerMachine
FROM iotHub as i
GROUP BY i.workorderId, TumblingWindow(minute, 5)

SELECT i.WorkorderId, i.DeviceError.errorCode, COUNT(*) as ErrorOccuredCount
INTO ErrorsPerMachine
FROM iotHub as i
GROUP BY i.WorkorderId, i.DeviceError.errorCode, TumblingWindow(minute,30)


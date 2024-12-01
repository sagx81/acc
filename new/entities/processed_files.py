class ProcessedFile:
    def __init__(self, fileName, processedDate):
        self.fileName = fileName
        self.processedDate = processedDate
    
    def __repr__(self):
        return f"{self.fileName} {self.processedDate}"

class Penalty:
    def __init__(self, raceType, season, track, raceNumber, driver, penaltySeconds, penaltyPosition, isDsq):
        self.raceType = raceType
        self.season = season
        self.track = track
        self.raceNumber = raceNumber
        self.driver = driver
        self.penaltySeconds = penaltySeconds
        self.penaltyPosition = penaltyPosition
        self.isDsq = isDsq        

    def __repr__(self):
        return f"{self.raceType} {self.season} {self.track} {self.raceNumber} {self.driver} {self.penaltySeconds} {self.penaltyPosition} {self.isDsq}"


class ResultRow:
    def __init__(self, position, driver, timing, totalTimeMs, totalTimeString, bestLap, laps, driverPoints, isDsq=False):
        self.position = position
        self.driver = driver
        self.timing = timing
        self.totalTimeMs = totalTimeMs
        self.totalTimeString = totalTimeString
        self.bestLap = bestLap
        self.laps = laps
        self.driverPoints = driverPoints
        self.isDsq = isDsq

    def __repr__(self):
        return f"Pos: {self.position}, Driver: {self.driver}, Timing: {self.timing}, TotalTimeMs: {self.totalTimeMs}, TotalTime: {self.totalTimeString}, BestLap: {self.bestLap}, Laps: {self.laps}, Points:  {self.driverPoints}"

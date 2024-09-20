class ProcessedFile:
    def __init__(self, fileName, processedDate):
        self.fileName = fileName
        self.processedDate = processedDate
    
    def __repr__(self):
        return f"{self.fileName} {self.processedDate}"

# class ResultRow:
#     def __init__(self, position, driver, timing, totalTimeMs, totalTimeString, bestLap, laps, points, isDsq=False):
#         self.position = position
#         self.driver = driver
#         self.timing = timing
#         self.totalTimeMs = totalTimeMs
#         self.totalTimeString = totalTimeString
#         self.bestLap = bestLap
#         self.laps = laps
#         self.points = points
#         self.isDsq = isDsq

#     def __repr__(self):
#         return f"Pos: {self.position}, Driver: {self.driver}, Timing: {self.timing}, TotalTimeMs: {self.totalTimeMs}, TotalTime: {self.totalTimeString}, BestLap: {self.bestLap}, Laps: {self.laps}, Points:  {self.points}"

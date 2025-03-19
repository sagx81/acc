class ProcessedFile:
    def __init__(self, fileName, processedDate):
        self.fileName = fileName
        self.processedDate = processedDate
    
    def __repr__(self):
        return f"{self.fileName} {self.processedDate}"

class Penalty:
    def __init__(self, raceType, season, track, raceNumber, driver, penaltySeconds=0, penaltyPosition=0, isDsq=0, gcPenaltyPoints=0):
        self.raceType = raceType
        self.season = season
        self.track = track
        self.raceNumber = raceNumber
        self.driver = driver
        self.penaltySeconds = penaltySeconds
        self.penaltyPosition = penaltyPosition
        self.isDsq = isDsq        
        self.gcPenaltyPoints = gcPenaltyPoints

    def __repr__(self):
        return f"{self.raceType} {self.season} {self.track} {self.raceNumber} {self.driver} {self.penaltySeconds} {self.penaltyPosition} {self.isDsq}"


class ResultRow:
    def __init__(self, position, driver, timing, totalTimeMs, totalTimeString, bestLap, laps, driverPoints, isDsq=False, penaltyMs=0):
        self.position = position
        self.driver = driver
        self.timing = timing
        self.totalTimeMs = totalTimeMs
        self.totalTimeString = totalTimeString
        self.bestLap = bestLap
        self.laps = laps
        self.driverPoints = driverPoints
        self.isDsq = isDsq
        self.penaltyMs = penaltyMs

    def __repr__(self):
        return f"Pos: {self.position}, Driver: {self.driver}, Timing: {self.timing}, TotalTimeMs: {self.totalTimeMs}, TotalTime: {self.totalTimeString}, BestLap: {self.bestLap}, Laps: {self.laps}, Points:  {self.driverPoints}"

class ResultRowV2:

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, position=0, driver=None, timing=None, totalTimeMs=0, totalTimeString=None, bestLap=None, laps=0, points=0, isDsq=False, isWetSession=False, carId=None, carModel=None, cupCategory=None, carGroup=None, teamName=None, raceNumber=None, carGuid=None, teamGuid=None, firstName=None, lastName=None, playerId=None, missingMandatoryPitstop=False, isSpectator=False, ballastKg=None,penaltyMs=0):
        self.position = position
        self.driver = driver
        self.timing = timing
        self.totalTimeMs = totalTimeMs
        self.totalTimeString = totalTimeString
        self.bestLap = bestLap
        self.laps = laps
        self.points = points
        self.isDsq = isDsq
        self.isWetSession = isWetSession
        self.carId = carId
        self.carModel = carModel
        self.cupCategory = cupCategory
        self.carGroup = carGroup
        self.ballastKg = ballastKg
        self.teamName = teamName
        self.raceNumber = raceNumber
        self.carGuid = carGuid
        self.teamGuid = teamGuid
        self.firstName = firstName
        self.lastName = lastName
        self.playerId = playerId
        self.missingMandatoryPitstop = missingMandatoryPitstop
        self.isSpectator = isSpectator
        self.penaltyMs = penaltyMs

    def __repr__(self):
        return f"Pos: {self.position}, Driver: {self.driver}, Timing: {self.timing}, TotalTimeMs: {self.totalTimeMs}, TotalTime: {self.totalTimeString}, BestLap: {self.bestLap}, Laps: {self.laps}, Points:  {self.points}, IsDsq: {self.isDsq}, IsWetSession: {self.isWetSession}, CarId: {self.carId}, CarModel: {self.carModel}, CupCategory: {self.cupCategory}, CarGroup: {self.carGroup}, TeamName: {self.teamName}, RaceNumber: {self.raceNumber}, CarGuid: {self.carGuid}, TeamGuid: {self.teamGuid}, FirstName: {self.firstName}, LastName: {self.lastName}, PlayerId: {self.playerId}, MissingMandatoryPitstop: {self.missingMandatoryPitstop}, IsSpectator: {self.isSpectator}, BallastKg: {self.ballastKg}"

class IndividualGraphicRow:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    # def __init__(self, position=0, driver=None, car=None, timing=None, bestLap=None, laps=0, points=0):
    def __init__(self, position=0, driver=None, timing=None, bestLap=None, laps=0, points=0):
        self.position = position
        self.driver = driver
        # self.car = car
        self.timing = timing
        self.bestLap = bestLap
        self.laps = laps
        self.points = points

class DriverWeb:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, discordId, playerID, callsign, numer, ranga):
        self.discordId = discordId
        self.playerID = playerID
        self.callsign = callsign
        self.numer = numer
        self.ranga = ranga

    def __repr__(self):
        return f"DiscordId: {self.discordId}, PlayerID: {self.playerID}, Callsign: {self.callsign}, Numer: {self.numer}, Ranga: {self.ranga}\n"

class Car:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, id, name, year):
        self.id = id
        self.name = name
        self.year = year

    def __repr__(self):
        return f"Id: {self.id}, Name: {self.name}, Year: {self.year}\n"

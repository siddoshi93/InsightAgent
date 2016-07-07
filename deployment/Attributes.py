class Attributes:
    def __init__(self, projectName, user, insightUser, insightKey, samplingInterval, reportingInterval, agentType, password):
        self.projectName = projectName
        self.user = user
        self.insightUser = insightUser
        self.licenseKey = insightKey
        self.samplingInterval = samplingInterval
        self.reportingInterval = reportingInterval
        self.agentType = agentType
        self.password = password

    def displayAttributes(self):
        print "ProjectName: ", self.projectName
        print "InsightFinder username: ", self.insightUser
        print "Host username: ", self.user
        print "Project license key: ", self.licenseKey
        print "Sampling Interval: ", self.samplingInterval
        print "Reporting Interval: ", self.reportingInterval
        print "Agent Type: ", self.agentType
        print "Password: ", self.password

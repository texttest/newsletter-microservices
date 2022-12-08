

from texttestlib.queuesystem import QueueSystemConfig
from texttestlib.default import comparetest, sandbox

import os

def getConfig(optionMap):
    return NewsletterConfig(optionMap)


class NewsletterConfig(QueueSystemConfig):
    serviceFields = []
    def addToOptionGroups(self, apps, groups):
        QueueSystemConfig.addToOptionGroups(self, apps, groups)
        for group in groups:
            if group.name.startswith("Basic"):
                self.addServiceFields(group)

    def findServices(self):
        services = []
        for rootDir in self.optionMap.rootDirectories:
            for subdir in os.listdir(rootDir):
                path = os.path.join(rootDir, subdir)
                if os.path.isdir(os.path.join(path, "src")):
                    services.append((subdir, path))
        return services
                    
    def addServiceFields(self, group):
        for unused in [ "c", "m", "v", "stop" ]:
            group.options.pop(unused) # don't use checkout
        for svcName, svcDir in self.findServices():
            label = svcName.capitalize() + " Service"
            possValues = [ svcDir, "" ]
            group.addOption(svcName, label, svcDir, possibleValues=possValues,
                            description=f"Code for the {svcName} service to use for the tests. Leave blank to use recorded data")
            if svcName not in self.serviceFields:
                self.serviceFields.append(svcName) 
        
    def getEnvironmentCreator(self, test):
        return TestEnvironmentCreator(test, self.optionMap)

    def getSlaveSwitches(self):
        return self.serviceFields + QueueSystemConfig.getSlaveSwitches(self)

    def getTestComparator(self):
        return comparetest.MakeComparisons(testComparisonClass=NewsletterTestComparison, enableColor="zen" in self.optionMap)
    

class NewsletterTestComparison(comparetest.TestComparison):
    def createFileComparison(self, test, stem, standardFile, tmpFile):
        if tmpFile is not None or self.showAsMissing(test, stem): # ignore missing log files, we don't care
            return comparetest.TestComparison.createFileComparison(self, test, stem, standardFile, tmpFile)

    def getServicesRun(self, test):
        services = []
        for varName in NewsletterConfig.serviceFields:
            value = test.app.optionValue(varName)
            if value:
                services.append(varName)
        return services
                
    def getServicesFromStem(self, stem):
        if stem.startswith("db_"):
            return [ stem.split("_")[1].lower() ]
        elif stem.endswith("-mocks"):
            return stem.split("-")[1:3]
        else:
            return []
        
    def showAsMissing(self, test, stem):
        services_run = self.getServicesRun(test)
        if len(services_run) == 0:
            return False

        stemServices = self.getServicesFromStem(stem)
        if len(stemServices) == 0:
            return True
        return any((svc in services_run for svc in stemServices))


# Class for automatically adding things to test environment files...
class TestEnvironmentCreator(sandbox.TestEnvironmentCreator):
    def getVariables(self, allVars):
        vars = []
        if self.topLevel():
            for varName in NewsletterConfig.serviceFields:
                value = self.test.app.optionValue(varName)
                if value:
                    vars.append(("SVC_" + varName.upper(), value))
        parentVars, props = sandbox.TestEnvironmentCreator.getVariables(self, vars + allVars)
        return parentVars + vars, props


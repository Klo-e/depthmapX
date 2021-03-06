import os.path
import cmdlinewrapper
import difflib
import pprint

import runhelpers


class DepthmapRunner():
    def __init__(self, runFunc, binary ):
        self.__runFunc = runFunc
        self.__binary = binary
        
    def runDepthmap(self, cmdWrapper, runDir):
        args = [self.__binary]
        args.extend(cmdWrapper.toCmdArray())
        return self.__runFunc(runDir, args)

def diffBinaryFiles(file1, file2):
    with open(file1, "rb") as f:
        content1 = f.read()
    with open(file2, "rb") as f:
        content2 = f.read()
    gen = difflib.diff_bytes(difflib.unified_diff, [content1], [content2])
    return not(list(gen))

class DepthmapRegressionRunner():
    def __init__(self, runFunc, baseBinary, testBinary, workingDir):
        self.__baseRunner = DepthmapRunner(runFunc, baseBinary)
        self.__testRunner = DepthmapRunner(runFunc, testBinary)
        self.__workingDir = workingDir

    def makeBaseDir(self, name):
        return os.path.join(self.__workingDir, name + "_base")

    def makeTestDir(self, name):
        return os.path.join(self.__workingDir, name + "_test")

    def runTestCase(self, name, cmd):
        runhelpers.prepareDirectory(self.makeBaseDir(name))
        runhelpers.prepareDirectory(self.makeTestDir(name))
        return self.runTestCaseImpl(name, cmd)

    def runTestCaseImpl(self, name, cmd):
        baseDir = self.makeBaseDir(name)
        (baseSuccess, baseOut) = self.__baseRunner.runDepthmap(cmd, baseDir)
        if not baseSuccess:
            print("Baseline run failed with arguments " + pprint.pformat(cmd.toCmdArray()))
            print(baseOut)
            return (False, "Baseline run failed")

        testDir = self.makeTestDir(name)
        (testSuccess, testOut) = self.__testRunner.runDepthmap(cmd, testDir)
        if not testSuccess:
            print("Test run failed with arguments " + pprint.pformat(cmd.toCmdArray()))
            print(testOut)
            return (False, "Test run failed")

        baseFile = os.path.join(baseDir, cmd.outfile)
        testFile = os.path.join(testDir, cmd.outfile)
        if not os.path.exists(baseFile):
            message = "Baseline output {0} does not exist".format(baseFile)
            print (message)
            return (False, message)
        if not os.path.exists(testFile):
            message = "Test output {0} does not exist".format(testFile)
            print(message)
            return (False, message)
        
        if not diffBinaryFiles(baseFile, testFile):
            message = "Test outputs differ"
            print (message)
            return (False, message)

        return (True, "")



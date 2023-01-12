from PIL import Image
import time
import argparse

"""
Class definitions
"""

class fileErrors():
    """Enum type class for error codes"""
    NoError = 0
    GenericError = 1
    SizeError = 2
    UnrecognisedOp = 3
    LoopStartMissing = 4
    LoopEndMissing = 5
    WrongFiletype = 6

class colours():
    """Enum type class for command colours"""
    Black = (0, 0, 0)
    White = (255, 255, 255)
    Green = (0, 255, 0)
    Red = (255, 0, 0)
    Blue = (0, 0, 255)
    Yellow = (255, 255, 0)
    Pink = (255, 120, 210)
    Cyan = (0,255,200)
    Purple = (165, 0, 255)
    DarkPurple = (100, 0, 255)
    Orange = (255, 100, 0)
    Brown = (145, 70, 0)
    LightBlue = (0, 255, 255)

class commands():
    """Enum type class for commands"""
    UnrecognisedOp = -1
    Noop = 0
    IncrementPointer = 1
    DecrementPointer = 2
    IncrementData = 3
    DecrementData = 4
    LoopStart = 5
    LoopEnd = 6
    PrintData = 7
    PrintAscii = 8
    Input = 9
    IntInput = 10
    End = 11

class dataArray():
    """Class for handling data array functionality"""
    def __init__(self):
        """Set up array of size 30000 filled with 0"""
        self.dataArray = [0]*30000
        self.arrayPointer = 0
        return
        
    def alterPointer(self, changeBy):
        """Increment or decrement pointer by given value"""
        self.arrayPointer += changeBy
        if self.arrayPointer < 0:
            self.arrayPointer = 0
        if self.arrayPointer > 30000:
            self.arrayPointer = 30000
        pass

    def alterArray(self, changeBy):
        """Increment or decrement value of array at pointer by given value"""
        s, p = self.dataArray, self.arrayPointer
        s[p] = s[p] + changeBy
        return

    def setArray(self, value):
        """Set value of array at pointer to given value"""
        self.dataArray[self.arrayPointer] = value
        return

    def getArrayVal(self):
        """Get value at current pointer location in the dataArray"""
        return self.dataArray[self.arrayPointer]

    def dumpArray(self):
        """Print the current state of the array to the console"""
        print(self.dataArray)
        return

class commandRunner():
    """Class for handling and running program commands"""
    def __init__(self, commandList, dataArray):
        self.commandList = commandList
        self.commandPointer = 0
        self.dataArray = dataArray
        return
    
    def runProgram(self):
        """runs the given program"""
        while self.commandPointer < len(self.commandList):
            returnVal = self.runNextCommand()
            #if end command found, end execution early
            if returnVal == 1:
                break
        pass

    def runNextCommand(self):
        """fetches the current command and runs it"""
        currentCommand = self.commandList[self.commandPointer]

        if currentCommand == commands.IncrementData:
            self.increment()
            self.commandPointer += 1
        elif currentCommand == commands.DecrementData:
            self.decrement()
            self.commandPointer += 1

        elif currentCommand == commands.IncrementPointer:
            self.dataArray.alterPointer(1)
            self.commandPointer += 1

        elif currentCommand == commands.DecrementPointer:
            self.dataArray.alterPointer(-1)
            self.commandPointer += 1

        elif currentCommand == commands.Noop:
            self.commandPointer += 1

        elif currentCommand == commands.LoopStart:
            if self.dataArray.getArrayVal() == 0:
                self.loopStart()
            else:
                self.commandPointer += 1
        elif currentCommand == commands.LoopEnd:
            if self.dataArray.getArrayVal() != 0:
                self.loopEnd()
            else:
                self.commandPointer += 1
        elif currentCommand == commands.PrintAscii:
            print(chr(self.dataArray.getArrayVal()))
            self.commandPointer += 1
        
        elif currentCommand == commands.PrintData:
            print(self.dataArray.getArrayVal())
            self.commandPointer += 1

        elif currentCommand == commands.Input:
            while True:
                userInput = input()
                if len(userInput) == 1:
                    self.dataArray.setArray(ord(userInput))
                    self.commandPointer += 1
                    break    

        elif currentCommand == commands.IntInput:
            while True:
                userInput = input()
                try:
                    userInputInt = int(userInput)
                    self.dataArray.setArray(userInputInt)
                    self.commandPointer += 1
                    break
                except:
                    pass

        elif currentCommand == commands.End:
            return 1

        pass

    def increment(self):
        self.dataArray.alterArray(1)
        return
    
    def decrement(self):
        self.dataArray.alterArray(-1)
        return

    def loopStart(self):
        while self.commandList[self.commandPointer] != commands.LoopEnd:
            self.commandPointer += 1
            if self.commandPointer > len(self.commandList):
                return fileErrors.loopEndMissing
        return

    def loopEnd(self):
        while self.commandList[self.commandPointer] != commands.LoopStart:
            self.commandPointer -= 1
            if self.commandPointer < 0:
                return fileErrors.loopStartMissing
        return

"""
Main functions
"""

def main() -> None:
    args = getArgs()
    if args == None: return
    
    try:
        sourceFile = Image.open(args.i.name)
    except:
        logError(fileErrors.WrongFiletype)
        return

    #run basic error checks
    if args.t:
        error = fileChecks(sourceFile)
        if error != fileErrors.NoError:
            logError(error)
            quit()
        commandChecks = getCommandList(sourceFile)
        if commandChecks == fileErrors.UnrecognisedOp:
            logError(fileErrors.UnrecognisedOp)
            quit()
        print("No errors found")
        return

    if args.T:
        startTime = time.time()

    
    error = fileChecks(sourceFile)
    if error != fileErrors.NoError:
        logError(error)
        return

    commandList = getCommandList(sourceFile)
    if commandList == commands.UnrecognisedOp:
        logError(fileErrors.UnrecognisedOp)
        return
    dArray = dataArray()

    runner = commandRunner(commandList, dArray)
    runner.runProgram()

    if args.T:
        print("Execution time:", time.time()-startTime, "seconds")

    return

def getCommandList(sourceFile):
    """Checks colour lists and converts image to list of command values"""
    rgbSourceFile = sourceFile.convert("RGB")
    commandList = []
    for x in range(0, sourceFile.width):
        for y in range(0, sourceFile.height):
            #reversed x and y due to pillow's coord implementation
            r, g, b = rgbSourceFile.getpixel((y, x))
            command = commandCheck((r,g,b))
            if command == commands.UnrecognisedOp:
                return commands.UnrecognisedOp
            commandList.append(command)
    return commandList

def getArgs():
    """ Gets arguments from command line and checks for errors """
    parser = argparse.ArgumentParser(description="An interpreter for the Visual Brainfuck esolang", usage="%(prog)s [source file] [options]")
    parser.add_argument('i', nargs='?', help="Input text file", type=argparse.FileType('r'))
    parser.add_argument('-t', help="Run file tests", action='store_true')
    parser.add_argument('-T', help="Time program execution", action='store_true')
    args = parser.parse_args()

    if args.i == None:
        print("No source file given")
        return

    return args

"""
Additional Utility functions
"""

def commandCheck(colour) -> commands:
    """Takes a tuple of a colour (r,g,b) and returns a command code"""

    if colour == colours.Green:
        return commands.IncrementPointer

    elif colour == colours.Red:
        return commands.DecrementPointer

    elif colour == colours.Blue:
        return commands.IncrementData

    elif colour == colours.Yellow:
        return commands.DecrementData

    elif colour == colours.Pink:
        return commands.LoopStart

    elif colour == colours.Cyan:
        return commands.LoopEnd

    elif colour == colours.Purple:
        return commands.End

    elif colour == colours.Black:
        return commands.Noop

    elif colour == colours.White:
        return commands.Noop

    elif colour == colours.Orange:
        return commands.PrintAscii

    elif colour == colours.Brown:
        return commands.PrintData

    elif colour == colours.LightBlue:
        return commands.Input

    elif colour == colours.DarkPurple:
        return commands.IntInput
    
    else:
        return commands.UnrecognisedOp

def fileChecks(imageFile) -> fileErrors:
    """Initial file sanity checks. Returns error code"""
    if(imageFile.width != imageFile.height):
        return fileErrors.SizeError
    
    return fileErrors.NoError

def logError(error) -> None:
    """Takes a file error and prints an appropriate error message"""
    if error == fileErrors.SizeError:
        print("File dimensions not equal")
    elif error == fileErrors.UnrecognisedOp:
        print("Unrecognised command used in file")
    elif error == fileErrors.WrongFiletype:
        print("File could not be opened. File may be corrupt, or wrong filetype")
    return


"""
Run program
"""

if __name__=="__main__":
    main()
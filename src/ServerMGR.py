import subprocess
from time import sleep
import threading
import queue

InputLock = threading.Lock()
OutputLock = threading.Lock()


class BedrockServer(object):
    def __init__(self, path,):
        self._ServerPath = path
        self.STDINQ = queue.Queue()
        self.STDOUTQ = queue.Queue()
        self.STDINThread = None
        self.STDOUTThread = None
        self.running = False

    def start(self):
        TempCommandList = []
        print("starting server from: ", self._ServerPath)
        self.process = subprocess.Popen(
            [self._ServerPath], stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True, bufsize=1)
        print("Created Process: ", self.process)
        print("Attempting to read from server directly...")
        data = self.process.stdout.readline()
        TempCommandList.append(data)
        print("Server Test Output: ", data)
        print("Server Test Output Successful...")
        print("Setting up threads...")
        self.STDINThread = threading.Thread(
            target=BedrockServer.STDINWorker, args=(self.process, self.STDINQ,))
        self.STDOUTThread = threading.Thread(
            target=BedrockServer.STDOUTWorker, args=(self.process, self.STDOUTQ,))
        print("Successfully Created Thread Objects...")
        print(
            f"Output Thread: {self.STDOUTThread} Input Thread: {self.STDINThread}")
        print("Starting Threads...")
        self.STDINThread.start()
        self.STDOUTThread.start()
        print("Successfully Started Threads")
        print("testing output Thread...")
        while True:
            if self.hasOutput():
                data = self.readline()
                TempCommandList.append(data)
                break
        print("Output Thread Working...")
        print("Waiting for Server to startfully...")
        while True:
            if self.hasOutput():
                data = self.readline()
                TempCommandList.append(data)
                if "Server started." in data:
                    break
        print("Server Started Successfully...")
        print("Testing Manual Input...")
        self.writeline("hello world\n")
        print("Attempting to get response...")
        while True:
            if self.hasOutput():
                data = self.readline()
                print(f"Response: \"{data.strip()}\"")
                break
        self.running = True
        print("Everything is working...")
        print("Server Output...", end="\n\n")
        for i in TempCommandList:
            print(i.strip())

    def readline(self, wait=False):
        if not wait:
            if self.STDOUTQ.empty():
                return None
            else:
                with OutputLock:
                    return self.STDOUTQ.get()
        else:
            while True:
                if not self.STDOUTQ.empty():
                    with OutputLock:
                        return self.STDOUTQ.get()
    
    def read(self, limit=None):
        tempList = []
        if limit == None:
            with OutputLock:
                for i in range(self.STDOUTQ.qsize()):
                    tempList.append(self.STDOUTQ.get())
    
    def serverCommand(self, command = "\n"):
        pass
        


    def hasOutput(self):
        if self.STDOUTQ.empty():
            return False
        else:
            return True

    def writeline(self, string="\n"):
        if string[-1] == "\n":
            with InputLock:
                self.STDINQ.put(string)
        else:
            string += "\n"
            self.STDINQ.put(string)

    @staticmethod
    def STDINWorker(process, q):
        while True:
            if not q.empty():
                with InputLock:
                    data = q.get()
                    process.stdin.write(data)

    @staticmethod
    def STDOUTWorker(process, q):
        while True:
            data = process.stdout.readline()
            with OutputLock:
                q.put(data)


server = BedrockServer(
    r"C:\Users\jbloo\Documents\VSCode\Python\bedrock-server-1.12.1.1\\bedrock_server.exe")
server.start()
while True:
    command = input("Command: ")
    server.writeline(command)
    print(server.read())


# f = open("hello.txt", mode="w")
# proc = subprocess.Popen([r"C:\Users\jbloo\Documents\VSCode\Python\bedrock-server-1.12.1.1\\bedrock_server.exe"],
# stdout=sp.PIPE, stdin=sp.PIPE)
# with proc:
#     while True:
#         # print("Trying to communicate")
#         output = proc.stdout.readline().strip()
#         print(output)
#         if "Server started." in output:
#             sleep(1)
#             print("About to write to stdin")
#             proc.stdin.write("\n")
#             print("wrote to stdin")
#             break

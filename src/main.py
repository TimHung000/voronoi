from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from voronoi import Voronoi, Point, voronoiFileParser, createVoronoiFile, testCaseParser
import bisect
import sys

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 600
RADIUS = 3
VORONOI_DOT_COLOR = 'black'
VORONOI_LINE_COLOR = 'black'

class App(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.title('Voronoi Diagram')
        self.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
        self.resizable(False, False)
        self.voronoi = Voronoi(canvasWidth=CANVAS_WIDTH, canvasHeight=CANVAS_HEIGHT)
        self.testCases = []
        self.currentTestCase = 0
        self.points = []

        # creating a frame
        mainFrame = ttk.Frame(self, padding="20 20 20 20")
        mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))

        upper = ttk.Frame(mainFrame, width=800, height=200)
        upper.grid(row=0, sticky=(N, W, E, S))
        bottomLeft = ttk.Frame(mainFrame, width=600, height=600)
        bottomLeft.grid(row=1, column=0, sticky=(N, W, E, S))
        bottomRight = ttk.Frame(mainFrame, width=200, height=600)
        bottomRight.grid(row=1, column=1, sticky=(N, W, E, S))

        # canvas
        self.canvas = Canvas(bottomLeft, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background='white')
        self.canvas.grid(sticky=(N, W, E, S))

        # button
        runButton = ttk.Button(upper, text='Run', command=self.run)
        runButton.grid(row=0, column=0, sticky=(N, W, E, S), padx=10, pady=10)
        stepPrevButton = ttk.Button(upper, text='Prev Step', command=self.prevStep)
        stepPrevButton.grid(row=0, column=1, sticky=(N, W, E, S), padx=10, pady=10)
        stepNextButton = ttk.Button(upper, text='Next Step', command=self.nextStep)
        stepNextButton.grid(row=0, column=2, sticky=(N, W, E, S), padx=10, pady=10)
        clearButton = ttk.Button(upper, text='Clear', command=self.clear)
        clearButton.grid(row=0, column=3, sticky=(N, W, E, S), padx=10, pady=10)

        loadButton = ttk.Button(upper, text = 'Load Voronoi Diagram', command=self.importVoronoiFile)
        loadButton.grid(row=1, column=0, sticky=(N, W, E, S), padx=10, pady=10)
        saveButton = ttk.Button(upper, text = 'Save Voronoi Diagram', command=self.saveVoronoi)
        saveButton.grid(row=1, column=1, sticky=(N, W, E, S), padx=10, pady=10)
        saveButton = ttk.Button(upper, text = 'Load Test Case', command=self.importTest)
        saveButton.grid(row=1, column=2, sticky=(N, W, E, S), padx=10, pady=10)
        runNextTestCase = ttk.Button(upper, text = 'Run Test Case', command=self.runNextTestCase)
        runNextTestCase.grid(row=1, column=3, sticky=(N, W, E, S), padx=10, pady=10)

        # label
        self.position = StringVar()
        self.position.set("position : (0,0)")
        positionLabel = Label(upper, textvariable= self.position)
        positionLabel.grid(row=1, column=4, rowspan=1)

        # listBox
        self.pointListBox = Listbox(bottomRight, height=37)
        self.pointListBox.grid(row=0, column=0, sticky=(N, W, E, S))
        scrollbar = ttk.Scrollbar(bottomRight, orient=VERTICAL, command=self.pointListBox.yview)
        scrollbar.grid(row=0, column=1,sticky=(N,S))
        self.pointListBox.configure(yscrollcommand=scrollbar.set)

        # event binding
        self.canvas.bind('<Button-1>', self.drawDot)
        self.canvas.bind('<Motion>', self.showPosition)

    def drawDot(self, event):
        bisect.insort(self.points, Point(event.x, event.y), key = lambda point: (point.x, point.y))
        self.clearScreen()
        for point in self.points:
            self.pointListBox.insert(END, '({0},{1})'.format(point.x, point.y))
            self.canvas.create_oval(point.x-RADIUS, point.y-RADIUS, point.x+RADIUS, point.y+RADIUS, fill=VORONOI_DOT_COLOR, outline='')

    def showPosition(self, event):
        self.position.set(f'position : ({event.x}, {event.y})')

    def run(self):
        if(len(self.points) == 0):
            messagebox.showerror("Error", "No point given")
            return

        self.voronoi.buildVoronoiDiagram(self.points)
        self.drawVoronoi()

    def runNextTestCase(self):
        if(len(self.testCases) == 0):
            messagebox.showerror("Error", "No test case imported")
            return

        self.clear()
        for point in self.testCases[self.currentTestCase]:
            bisect.insort(self.points, Point(point[0], point[1]), key = lambda point: (point.x, point.y))

        self.currentTestCase = (self.currentTestCase+1) % len(self.testCases)
        self.run()

    def runStep(self):
        self.clearScreen()
        for point in self.points:
            self.canvas.create_oval(point.x-RADIUS, point.y-RADIUS, point.x+RADIUS, point.y+RADIUS, fill=VORONOI_DOT_COLOR, outline='')
            self.pointListBox.insert(END, '({0},{1})'.format(point.x, point.y))
        
        currentStepIndex = self.voronoi.currentStep // 5
        mergeOrFullGraph = self.voronoi.currentStep % 5
        if(mergeOrFullGraph == 0):
            # show left, right convexHull and tangent
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].leftVoronoiRecord.convexHull:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='purple', width=2)

            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].rightVoronoiRecord.convexHull:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='purple', width=2)
        elif(mergeOrFullGraph == 1):
            # show merged convexHull
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].newVornoiRecord.convexHull:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='purple', width=2)
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].tangent:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='orange', width=2)
            # show left, right voronoi
            for point in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].leftVoronoiRecord.points:
                self.canvas.create_oval(point.x-RADIUS, point.y-RADIUS, point.x+RADIUS, point.y+RADIUS, fill='blue', outline='')
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].leftVoronoiRecord.edges:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='blue', width=2)
            for point in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].rightVoronoiRecord.points:
                self.canvas.create_oval(point.x-RADIUS, point.y-RADIUS, point.x+RADIUS, point.y+RADIUS, fill='red', outline='')
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].rightVoronoiRecord.edges:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='red', width=2)

        elif(mergeOrFullGraph == 2):
            # show merged convexHull
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].newVornoiRecord.convexHull:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='purple', width=2)
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].tangent:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='orange', width=2)

            # show left, right voronoi
            for point in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].leftVoronoiRecord.points:
                self.canvas.create_oval(point.x-RADIUS, point.y-RADIUS, point.x+RADIUS, point.y+RADIUS, fill='blue', outline='')
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].leftVoronoiRecord.edges:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='blue', width=2)
            for point in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].rightVoronoiRecord.points:
                self.canvas.create_oval(point.x-RADIUS, point.y-RADIUS, point.x+RADIUS, point.y+RADIUS, fill='red', outline='')
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].rightVoronoiRecord.edges:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='red', width=2)

            # hyperplane
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].hyperPlane:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='Turquoise', width=2)
        elif(mergeOrFullGraph == 3):
            # show left, right voronoi
            for point in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].leftVoronoiRecord.points:
                self.canvas.create_oval(point.x-RADIUS, point.y-RADIUS, point.x+RADIUS, point.y+RADIUS, fill='blue', outline='')
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].leftVoronoiRecord.edges:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='blue', width=2)
            for point in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].rightVoronoiRecord.points:
                self.canvas.create_oval(point.x-RADIUS, point.y-RADIUS, point.x+RADIUS, point.y+RADIUS, fill='red', outline='')
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].rightVoronoiRecord.edges:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='red', width=2)

            # hyperplane
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].hyperPlane:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='Turquoise', width=2)
        elif(mergeOrFullGraph == 4):
            # show full graph after merge
            for point in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].newVornoiRecord.points:
                self.canvas.create_oval(point.x-RADIUS, point.y-RADIUS, point.x+RADIUS, point.y+RADIUS, fill='blue', outline='')
            for edge in self.voronoi.voronoiGraph.mergeRecords[currentStepIndex].newVornoiRecord.edges:
                self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill='blue', width=2)        

    def nextStep(self):
        if(self.voronoi.voronoiGraph == None or len(self.voronoi.voronoiGraph.mergeRecords) == 0):
            self.voronoi.buildVoronoiDiagram(self.points)
            self.voronoi.currentStep = 0
        else:
            self.voronoi.currentStep = (self.voronoi.currentStep + 1) % (len(self.voronoi.voronoiGraph.mergeRecords) * 5)

        if(len(self.points) <= 2):
            self.drawVoronoi()
        else:
            self.runStep()

    def prevStep(self):
        if(self.voronoi.voronoiGraph == None or len(self.voronoi.voronoiGraph.mergeRecords) == 0):
            self.voronoi.buildVoronoiDiagram(self.points)
            self.voronoi.currentStep = 0
        else:
            self.voronoi.currentStep = (self.voronoi.currentStep + (len(self.voronoi.voronoiGraph.mergeRecords)*5-1)) % (len(self.voronoi.voronoiGraph.mergeRecords) * 5)

        if(len(self.voronoi.points) <= 2):
            self.drawVoronoi()
        else:
            self.runStep()
    
    def drawVoronoi(self):
        self.pointListBox.delete(0, END)
        self.canvas.delete('all')

        for point in self.voronoi.points:
            self.canvas.create_oval(point.x-RADIUS, point.y-RADIUS, point.x+RADIUS, point.y+RADIUS, fill=VORONOI_DOT_COLOR, outline='')
            self.pointListBox.insert(END, '({0},{1})'.format(point.x, point.y))
        
        for edge in self.voronoi.edges:
            self.canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y, fill=VORONOI_LINE_COLOR, width=2)
            print(f"({edge.start.x, edge.start.y}) -> ({edge.end.x}, {edge.end.y})")

    def saveVoronoi(self):
        if(len(self.voronoi.points) == 0 or len(self.voronoi.edges) == 0):
             messagebox.showerror("Error", "No Voronoi Diagram created")
             return

        file = filedialog.asksaveasfilename(
            title="Save Voronoi File",
            filetypes=(("txt file", ".txt"),),
            defaultextension=".txt"
        )
        if(file):
            createVoronoiFile(file, self.voronoi.points, self.voronoi.edges)

    def importTest(self):
        self.currentTestCase = 0
        self.testCases = []

        file = filedialog.askopenfilename(
            title="Import test file", 
            filetypes=(("Text Files", "*.txt"),)
        )
        if(file):
            self.currentTestCase = 0
            self.testCases = testCaseParser(file)
            if(len(self.testCases) == 0):
                messagebox.showerror("Error", "Format Error or empty set file")
            else:
                messagebox.showinfo("Success", "successfully import the test cases")

    def importVoronoiFile(self):
        file = filedialog.askopenfilename(
            title="Import voronoi diagram", 
            filetypes=(("Text Files", "*.txt"),)
        )
        if(file):
            points, edges = voronoiFileParser(file)
            self.clear()
            self.points = points
            self.voronoi.points = points
            self.voronoi.edges = edges
            self.drawVoronoi()
            messagebox.showinfo("Success", "successfully import the voronoi graph")
        else:
            messagebox.showerror("Error", "Fail to import file")

    
    def clear(self):
        self.pointListBox.delete(0, END)
        self.canvas.delete('all')
        self.points.clear()
        self.voronoi.clear()
    
    def clearScreen(self):
        self.pointListBox.delete(0, END)
        self.canvas.delete('all')
        
if __name__ == '__main__':
    sys.setrecursionlimit(2 ** 20) # something real big
    app = App()
    app.mainloop()


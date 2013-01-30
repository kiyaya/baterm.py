1 REM :: 
2 REM :: 
3 REM :: BASIC COMMAND LIST.
4 REM ::       	GUI 	:	WILL SEND THE COMMAND IN "" TO THE GUI INTERFACE. 
5 REM ::       					GUI "_clear", WILL CLEAR THE GUI CONSOLE
6 REM ::       					GUI "_stop", WILL STOP THE CALIBRATION PROCESS
7 REM ::       	LET		:	USED TO ASSIGN NUMBERS 
8 REM ::						LET I = 0.1, WILL ASSIGN 0.1 TO VARIABLE I	
9 REM ::		LETSTR	: 	USED TO ASSIGN STRINGS
10 REM ::				 		LETSTR MCUPORT = "COM3" ,WILL ASSIGN "COM3" TO MCUPORT
11 REM ::		OUT		:	WILL OUTPUT STRINGS TO THE DESTINATION PORT
12 REM ::				 	(1) BEFORE USE OUT COMMAND, YOU NEED TO ASSIGN THE OUTPUT PORT FIRST
13 REM ::				 		LETSTR MCUPORT = "COM3"
14 REM ::				 		LETSTR DEVICEPORT = "COM4"
15 REM ::						LETSTR CONSOLE = "CONSOLEs"	
16 REM ::				 	(2) THEN, 
17 REM ::				 		OUT MCUPORT = "CMD", WILL OUTPUT CMD IN "" TO THE MCU UART PORT (COM3)
18 REM ::				 		OUT DEVICEPORT = "CMD" WILL OUTPUT CMD IN "" TO THE DEVICE PORT (COM4)
19 REM :: 				 		OUT CONSOLE = "Hello", WILL OUTPUT STRING HELLO IN "" TO GUI CONSOLE.
20 REM ::		CHECK	: 	WILL CHECK OUT THE RESULT BACK FROM UART
21 REM ::				 		CHECK "AUTO", WILL CHECK THE RESULT AUTOMATICALLY
22 REM ::				 		CHECK "MANUAL", WILL CHECK THE RESULT BY HUMAN
23 REM ::		DELAY	: 	WILL DELAY ASSIGNED TIME INTERVAL
24 REM ::						DELAY 1, WILL DELAY 1s
25 REM :: 						DELAY 0.1, WILL DELAY 100ms
26 REM ::						DELAY 0, Will PAUSE AND WAIT HUMAN'S INPUT
27 REM ::
28 REM ::
29 REM :: ADVANCED COMMAND LIST.
30 REM :: 		PLEASE REFER TO BELOW TABLE AND FIND OUT THE DEFINITIONS IN BASIC PROGRAMMING BOOKS
31 REM ::    		'LET','READ','DATA','PRINT','GOTO','IF','THEN','FOR','NEXT','TO','STEP',
32 REM ::		    'END','STOP','DEF','GOSUB','DIM','REM','RETURN','RUN','LIST','NEW',

40 REM ======== DO NOT CHANGE BELOW VARIABLE NAME ========
41 LETSTR TUTORIAL = "TUTORIALs"
42 LETSTR INSTRUCTION = "INSTRUCTIONs"
43 LETSTR CONSOLE = "CONSOLEs"
44 LETSTR MCUPORT = "COM21"
45 LET MCUBAUD = 9600
46 LETSTR DEVICEPORT = "COM20"
47 LET DEVICEBAUD = 9600
50 REM ======== DO NOT CHANGE ABOVE VARIABLE NAME ========
55 OUT INSTRUCTION = "Welcome to Lavida's mass production line. \n欢迎来到 朗逸 生产线！", "\nFONTCOLOR=BLUE", "\nFONTSIZE=40"
58 OUT CONSOLE = "_CLEAR"
59 OUT CONSOLE = "_CURRENTTIME"
64 REM OUT CONSOLE = "_ERROR"
65 FOR I = 1 TO 2
71 OUT DEVICEPORT = "XNTC"
72 OUT MCUPORT = "NTCOPEN"
73 DELAY 3
75 OUT DEVICEPORT = "NTC"
79 OUT MCUPORT = "10k"
80 DELAY 5
82 OUT DEVICEPORT = "?NTC.OHM0"
83 READDATA OHM0 = "?NTC.OHM0"
84 OUT CONSOLE =  "OHM0=", OHM0
85 OUT DEVICEPORT = "NTC"
86 OUT MCUPORT = "50k"
90 DELAY 5
92 OUT DEVICEPORT = "?NTC.OHM0"
93 READDATA OHM0 = "?NTC.OHM0"
94 OUT CONSOLE =  "OHM0=", OHM0
97 OUT DEVICEPORT = "NTC"
98 OUT DEVICEPORT = "XNTC"
100 OUT DEVICEPORT = "?NTC.A"
101 OUT DEVICEPORT = "?NTC.B"
102 OUT DEVICEPORT = "?NTC.K"
105 READDATA A = "?NTC.A"
106 READDATA B = "?NTC.B"
107 READDATA K = "?NTC.K"
110 OUT CONSOLE =  "A=", A, "B=", B
111 OUT CONSOLE =  "K=", K

120 IF A < 0.9 THEN 140
130 OUT CONSOLE = "A IS GREATER THAN 0.9"
140 OUT CONSOLE = "Finished.", I, "TIMES"

171 OUT DEVICEPORT = "XMVCAL"
175 OUT DEVICEPORT = "MVCAL"
179 OUT MCUPORT = "-1000MV2"
180 DELAY 5
182 OUT DEVICEPORT = "?MVCAL.MV0"
183 READDATA MV0 = "?MVCAL.MV0"
184 OUT CONSOLE =  "MV0=", MV0
185 OUT DEVICEPORT = "MVCAL"
186 OUT MCUPORT = "1000MV2"
190 DELAY 5
200 OUT DEVICEPORT = "?MVCAL.MV0"
203 READDATA MV0 = "?MVCAL.MV0"
205 OUT CONSOLE =  "MV0=", MV0
208 OUT DEVICEPORT = "MVCAL"
210 OUT DEVICEPORT = "XNTC"
213 OUT DEVICEPORT = "?MVCAL.A"
215 OUT DEVICEPORT = "?MVCAL.B"
218 READDATA A = "?MVCAL.A"
220 READDATA B = "?MVCAL.B"
223 OUT CONSOLE =  "A=", A, "B=", B

230 IF A < 0.9 THEN 171
235 OUT CONSOLE = "A IS GREATER THAN 0.9"
240 OUT CONSOLE = "Finished.", I, "TIMES"
250 NEXT I

260 FOR J = 1 TO 5
263 READ A
265 OUT MCUPORT = A, "MV2"
268 DELAY 5
270 OUT DEVICEPORT = "?RD.MV"
273 READDATA MV = "?RD.MV"
274 OUT CONSOLE =  "MV=", MV
300 NEXT J

900 OUT CONSOLE = "_CURRENTTIME"
910 REM OUT CONSOLE = "_SCAN"
950 DATA -1000, -500, 0, 500, 1000
1000 END

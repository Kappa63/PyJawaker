'''
Author: Karim Q.
Original Date: 11/2/21
Update Date: 4/9/24

Update Note:
Probably should've been done with classes, but well if it ain't broke dont fix it. I only updated the broken parts and slightly improved readability.
'''
from pynput.mouse import Button, Controller
# from matplotlib import pyplot as plt
import pyscreenshot as ImageGrab
from PIL import Image
import numpy as np
import random
import time
import cv2
import os

MOUSE_CONTROL = Controller()

DECK_CARDS = ['s2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 'sJ', 'sQ', 'sK', 'sA',
        'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10', 'dJ', 'dQ', 'dK', 'dA',
        'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'cJ', 'cQ', 'cK', 'cA',
        'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'hJ', 'hQ', 'hK', 'hA']

HIERACHY = {"c":['c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'cJ', 'cQ', 'cK', 'cA', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'hJ', 'hQ', 'hK', 'hA'],
            "d":['d2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10', 'dJ', 'dQ', 'dK', 'dA', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'hJ', 'hQ', 'hK', 'hA'],
            "s":['s2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 'sJ', 'sQ', 'sK', 'sA', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'hJ', 'hQ', 'hK', 'hA'],
            "h":['h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'hJ', 'hQ', 'hK', 'hA']}

BET_POSITIONS = {2:[(404, 520)],
        3:[(455, 517), (404, 520)],
        4:[(503, 522), (455, 517)],
        5:[(560, 521), (503, 522)],
        6:[(403, 573), (560, 521)]}

SUITS = ["Heart", "Spade", "Diamond", "Club"]
VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
DIRS = {"HAND_CARD_SUITS":"./Assets/Hand/Suits", 
        "HAND_CARD_VALUES":"./Assets/Hand/Values",
        "TABLE_CARD_SUITS":"./Assets/Table/Suits", 
        "TABLE_CARD_VALUES":"./Assets/Table/Values",
        "TEST_FOR_2":"./Assets/General/Test2_V2.png",
        "TEST_FOR_3":"./Assets/General/Test3_V2.png",
        "TEMP":"./Temp/tmp.png"}

PlayedCards = []
HandCards = []
CompleteFail = False
MateCompleteFail = False
Choose = False
Plays = False

def Play(Pos, Margin):
    MOUSE_CONTROL.position = (Margin[0]+Pos[0], Margin[1]+Pos[1])
    # MOUSE_CONTROL.click(Button.left, 2)
    MOUSE_CONTROL.press(Button.left)
    MOUSE_CONTROL.release(Button.left)
    time.sleep(0.1)
    MOUSE_CONTROL.press(Button.left)
    MOUSE_CONTROL.release(Button.left)


def Find(Crd, Img):
    OriImg = cv2.imread(Img)
    BnWImg = cv2.cvtColor(OriImg, cv2.COLOR_BGR2GRAY)
    Card = cv2.imread(Crd,0)
    Pos = None
    # w, h = Card.shape[::-1]
    Match = cv2.matchTemplate(BnWImg, Card, cv2.TM_CCOEFF_NORMED)
    Loc = np.where(Match >= 0.9)
    return [pt for pt in zip(*Loc[::-1])]
    #     Pos = pt
    #     break
        # cv2.rectangle(OriImg, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2)
    # cv2.imwrite('res.png',OriImg)

def CheckTurn():
    TurnI = ImageGrab.grab((310,953,317,960))
    TurnI.save(DIRS["TEMP"])
    Img = Image.open(DIRS["TEMP"])
    Pixels = Img.load()
    print("Turn Circle Pixel Color: ", Pixels[4,4])
    return CheckColor(Pixels[4,4])

def CheckComplete():
    CompI = ImageGrab.grab((600,1005,605,1010))
    CompI.save(DIRS["TEMP"])
    Img = Image.open(DIRS["TEMP"])
    Pixels = Img.load()
    return CheckColor(Pixels[2,2])

def CheckMateComplete():
    CompI = ImageGrab.grab((475,380,480,385))
    CompI.save(DIRS["TEMP"])
    Img = Image.open(DIRS["TEMP"])
    Pixels = Img.load()
    return CheckColor(Pixels[2,2])

def CheckColor(RGB):
    if (230 <= RGB[0] <= 250) and (190 <= RGB[1] <= 200) and (60 <= RGB[2] <= 70):
        return "Y"
    elif (40 <= RGB[0] <= 50) and (175 <= RGB[1] <= 185) and (55 <= RGB[2] <= 65):
        return "G"
    elif (115 <= RGB[0] <= 125) and (6 <= RGB[1] <= 16) and (18 <= RGB[2] <= 28):
        return "R"
    elif (0 <= RGB[0] <= 10) and (0 <= RGB[1] <= 10) and (0 <= RGB[2] <= 10):
        return "B"
    else:
        return "U"

def GetMyCards():
    global PlayedCards
    HandI = ImageGrab.grab((255,800,700,880))
    HandI.save(DIRS["TEMP"])
    Hand = {}
    tempVals = {v:Find(os.path.join(DIRS["HAND_CARD_VALUES"], f"{v}.png"), DIRS["TEMP"]) for v in VALUES}
    tempSuits = {s:Find(os.path.join(DIRS["HAND_CARD_SUITS"], f"{s}.png"), DIRS["TEMP"]) for s in SUITS}
    for suit, posS in tempSuits.items():
        for xS, _ in posS:
            for val, posV in tempVals.items():
                for pos in posV:
                    if abs(xS-pos[0]) <= 2:
                        Card = suit[0].lower()+val
                        Hand[Card] = pos
                        PlayedCards.append(Card)
    return Hand

def GetPlayed():
    global PlayedCards
    TableI = ImageGrab.grab((390,420,570,620))
    TableI.save(DIRS["TEMP"])
    TableD = {}
    Table = []
    tempVals = {v:Find(os.path.join(DIRS["TABLE_CARD_VALUES"], f"{v}.png"), DIRS["TEMP"]) for v in VALUES}
    tempSuits = {s:Find(os.path.join(DIRS["TABLE_CARD_SUITS"], f"{s}.png"), DIRS["TEMP"]) for s in SUITS}
    for suit, posS in tempSuits.items():
        for xS, _ in posS:
            for val, posV in tempVals.items():
                for xV, _ in posV:
                    if abs(xS-xV) <= 2:
                        Card = suit[0].lower()+val
                        TableD[xV] = Card
                        PlayedCards.append(Card)
    for i in sorted(TableD):
        Table.append(TableD[i])
    return Table

def BestPlay(Hand, Table):
    def CardSplitter(Cards):
        Hs = [i for i in Cards if i[0] == "h"]
        for H in Hs:
            Cards.remove(H)
        return Cards, Hs
    def CardCleaner(Cards, Type):
        CardOType = [i for i in Cards if i[0] == Type]
        return CardOType if CardOType else Cards
    Choices = []
    print(Hand)
    if Table:
        CardType = Table[-1][0]
        print(f'Card Type: {CardType}')
        Hand = CardCleaner(Hand, CardType)
        Available = (Hand[0][0] == CardType)
        print(f'Available?: {Available}')
        WantedHierachy = HIERACHY[CardType]
        NunsHierachy = HIERACHY["h"]
        AvailableHierachy = WantedHierachy[:13]
        ImportantCards = [C for C in Table if C in WantedHierachy]
        ImportantCards.sort(key = lambda x: WantedHierachy.index(x))
        StrongestCard = ImportantCards[-1]
        print(f'Strongest: {StrongestCard}')
        Hand.sort(key = lambda x: DECK_CARDS.index(x))
        ForTeam = True if Table.index(StrongestCard) == 1 else False
        print(f'Strongest For Mate?: {ForTeam}')
        if Available:
            if (len(Table) == 3):
                if ForTeam and MateCompleteFail==False and StrongestCard[-1] in ["Q","K","A"]:
                    return Hand[0]
                if CardType != "h":
                    if (StrongestCard[0] != "h"):
                        Choices = [i for i in AvailableHierachy[AvailableHierachy.index(StrongestCard)+1:] if i in Hand]
                    return Hand[0] if (StrongestCard[0] == "h") else Choices[0] if Choices else Hand[0]
                    # or (AvailableHierachy.index(StrongestCard) > AvailableHierachy.index(Hand[-1]))) 
                else:
                    Choices = [i for i in NunsHierachy[NunsHierachy.index(StrongestCard)+1:] if i in Hand]
                    return Choices[0] if Choices else Hand[0]
            else:
                if ForTeam and MateCompleteFail==False:
                    return Hand[0]
                if CardType != "h":
                    if (StrongestCard[0] != "h"):
                        Choices = [i for i in AvailableHierachy[AvailableHierachy.index(StrongestCard)+1:] if i in Hand and set(AvailableHierachy[AvailableHierachy.index(i)+1:]).issubset(PlayedCards)]
                    return Hand[0] if (StrongestCard[0] == "h") else Choices[0] if Choices else Hand[0]
                    # or (AvailableHierachy.index(StrongestCard) > AvailableHierachy.index(Hand[-1])))
                else:
                    Choices = [i for i in NunsHierachy[NunsHierachy.index(StrongestCard)+1:] if i in Hand and set(NunsHierachy[NunsHierachy.index(i)+1:]).issubset(PlayedCards)]
                    return Choices[0] if Choices else Hand[0]
        else:
            Throws, Hearts = CardSplitter(Hand)
            if ForTeam and MateCompleteFail==False:
                return Throws[0] if Throws else Hearts[0]
            # if len(Table) == 3:
            if StrongestCard[0] == "h":
                Choices = [i for i in NunsHierachy[NunsHierachy.index(StrongestCard)+1:] if i in Hearts]
            return Hearts[0] if ((StrongestCard[0] != "h") and Hearts) else Choices[0] if Choices else Throws[0]
            # else:
            #     if StrongestCard[0] == "h":
            #         Choices = [i for i in NunsHierachy[NunsHierachy.index(StrongestCard)+1:] if i in Hearts and set(NunsHierachy[NunsHierachy.index(i)+1:]).issubset(PlayedCards)]
            #     return Choices[0] if Choices else Throws[0]
    else:
        AKs = [i for i in Hand if i[-1] == "A" or i[-1] == "K"]
        print(Hand)
        for i in AKs:
            Hand.remove(i)
        Hand, H = CardSplitter(Hand)
        Playable = []
        for i in AKs:
            HiS = HIERACHY[i[0]][:13]
            if set(HiS[HiS.index(i)+1:]).issubset(PlayedCards):
                Playable.append(i)
        return random.choice(Playable) if Playable else random.choice(Hand) if Hand else H[0]

def DetectPhase():
    Number = ImageGrab.grab((393, 520, 427, 547))
    Number.save(DIRS["TEMP"])
    Phaser = 0 if Find(DIRS["TEST_FOR_2"], DIRS["TEMP"]) else 1 if Find(DIRS["TEST_FOR_3"], DIRS["TEMP"]) else -1
    print(f'Playing Phase: {Phaser}')
    return Phaser

def BestBet(Hand):
    Hs = [i for i in Hand if i[0] == "h"]
    Cs = [i for i in Hand if i[0] == "c"]
    Ds = [i for i in Hand if i[0] == "d"]
    Ss = [i for i in Hand if i[0] == "s"]
    
    PfC = -1 if len(Cs) >= 5 else 1 if (len(Cs) <= 2 and len(Hs) >= 3) else 0
    PfD = -1 if len(Ds) >= 5 else 1 if (len(Ds) <= 2 and len(Hs) >= 3) else 0
    PfS = -1 if len(Ss) >= 5 else 1 if (len(Ss) <= 2 and len(Hs) >= 3) else 0
    PfH =  1 if len(Ss) >= 5 else 0
    
    PfC += 1 if "cA" in Cs else 0
    PfD += 1 if "dA" in Cs else 0
    PfS += 1 if "sA" in Cs else 0
    PfC += 1 if "cK" in Cs else 0
    PfD += 1 if "dK" in Cs else 0
    PfS += 1 if "sK" in Cs else 0

    for i in reversed(HIERACHY["h"]): 
        if i not in Hs: break    
        PfH+=1

    BetMake = (PfC if PfC != -1 else 0) + (PfS if PfS != -1 else 0) + (PfD if PfD != -1 else 0) + PfH
    print(f'Best Bet: {BetMake}')
    return BetMake

# print(CheckComplete())

while True:
    if CheckTurn() == "Y":
        while Plays == False:
            print("Choosing Bets...")
            if Choose:
                Phase = DetectPhase()
                Threshold = 2 if Phase == 0 else 3
                HandCards = GetMyCards()
                Bet = BestBet(HandCards.keys())
                Bet = Threshold if Bet<Threshold else 6 if Bet>6 else Bet
                Play(BET_POSITIONS[Bet][Phase], (0,0))
                Choose = False
                print("-"*100)
            time.sleep(1.5)
            if CheckTurn() == "Y":
                KPds = CheckComplete()
                print(KPds)
                Plays = DetectPhase() == -1 and KPds == "B"
                Choose = True

    while len(HandCards)-1 != 0 and Plays:
        time.sleep(0.5)
        if CheckTurn() == "Y":
            print(f'Playing... ({len(HandCards)-1} rounds left)')
            time.sleep(0.7)
            CompleteFail = ((CheckComplete() == "R") or (CheckComplete() == "G"))
            MateCompleteFail = ((CheckMateComplete() == "R") or (CheckMateComplete() == "G"))
            print(f'Complete or Fail?: {CompleteFail}')
            print(f'Mate Complete or Fail?: {MateCompleteFail}')
            HandCards = GetMyCards()
            TableCards = GetPlayed()
            Play(HandCards[BestPlay(list(HandCards.keys()), TableCards)], (260, 832))
            print("-"*100)
    Plays = False

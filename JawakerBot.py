'''
Author: Karim Q.
Date: 11/2/21
'''
import numpy as np
from PIL import Image, ImageGrab
from pynput.mouse import Button, Controller
import cv2
from matplotlib import pyplot as plt
import time
import random

Mouse = Controller()

Cards = ['s2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 'sJ', 'sQ', 'sK', 'sA',
        'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10', 'dJ', 'dQ', 'dK', 'dA',
        'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'cJ', 'cQ', 'cK', 'cA',
        'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'hJ', 'hQ', 'hK', 'hA']

Hierachy = {"c":['c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'cJ', 'cQ', 'cK', 'cA', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'hJ', 'hQ', 'hK', 'hA'],
            "d":['d2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10', 'dJ', 'dQ', 'dK', 'dA', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'hJ', 'hQ', 'hK', 'hA'],
            "s":['s2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 'sJ', 'sQ', 'sK', 'sA', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'hJ', 'hQ', 'hK', 'hA'],
            "h":['h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'hJ', 'hQ', 'hK', 'hA']}

Bets = {2:[(404, 485)],
        3:[(455, 482), (404, 485)],
        4:[(503, 487), (455, 482)],
        5:[(560, 486), (503, 487)],
        6:[(403, 538), (560, 486)]}

PlayedCards = []
HandCards = []
CompleteFail = False
Choose = False
Plays = False

def Play(Pos, Margin):
    Mouse.position = (Margin[0]+Pos[0], Margin[1]+Pos[1])
    Mouse.click(Button.left, 2)

def Find(Crd, Img):
    OriImg = cv2.imread(Img)
    BnWImg = cv2.cvtColor(OriImg, cv2.COLOR_BGR2GRAY)
    Card = cv2.imread(Crd,0)
    Pos = None
    # w, h = Card.shape[::-1]
    Match = cv2.matchTemplate(BnWImg, Card, cv2.TM_CCOEFF_NORMED)
    Loc = np.where( Match >= 0.95 )
    for pt in zip(*Loc[::-1]):
        Pos = pt
        break
        # cv2.rectangle(OriImg, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2)
    # cv2.imwrite('res.png',OriImg)
    return Pos

def CheckTurn():
    TurnI = ImageGrab.grab((442,991,456,1002))
    TurnI.save("Turn.png")
    Img = Image.open("Turn.png")
    Pixels = Img.load()
    return CheckColor(Pixels[0,0])

def CheckComplete():
    CompI = ImageGrab.grab((540,698,542,701))
    CompI.save("Comp.png")
    Img = Image.open("Comp.png")
    Pixels = Img.load()
    return CheckColor(Pixels[0,0])

def CheckMateComplete():
    CompI = ImageGrab.grab((390,268,397,272))
    CompI.save("CompMate.png")
    Img = Image.open("CompMate.png")
    Pixels = Img.load()
    return CheckColor(Pixels[0,0])

def CheckColor(RGB):
    if (245 < RGB[0] < 249) and (181 < RGB[1] < 186) and (18 < RGB[2] < 23):
        return "Y"
    elif (73 < RGB[0] < 78) and (189 < RGB[1] < 193) and (103 < RGB[2] < 108):
        return "G"
    elif (227 < RGB[0] < 232) and (77 < RGB[1] < 83) and (84 < RGB[2] < 89):
        return "R"
    elif (57 < RGB[0] < 72) and (57 < RGB[1] < 72) and (57 < RGB[2] < 72):
        return "B"
    else:
        return "U"

def GetMyCards():
    global PlayedCards
    HandI = ImageGrab.grab((255,728,702,881))
    HandI.save("Hand.png")
    Hand = {}
    for Card in Cards:
        P = Find(f'Hand/{Card}.png', "Hand.png")
        if P:
            Hand[Card] = P
            PlayedCards.append(Card)
    print(f'Hand: {Hand}')
    return Hand

def GetPlayed():
    global PlayedCards
    TableI = ImageGrab.grab((388,379,572,649))
    TableI.save("Table.png")
    TableD = {}
    Table = []
    for Card in Cards:
        P = Find(f'Table/{Card}.png', "Table.png")
        if P:
            TableD[P[0]] = Card
            PlayedCards.append(Card)
    for i in sorted(TableD):
        Table.append(TableD[i])
    print(f'Table: {Table}')
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
        WantedHierachy = Hierachy[CardType]
        NunsHierachy = Hierachy["h"]
        AvailableHierachy = WantedHierachy[:13]
        ImportantCards = [C for C in Table if C in WantedHierachy]
        ImportantCards.sort(key = lambda x: WantedHierachy.index(x))
        StrongestCard = ImportantCards[-1]
        print(f'Strongest: {StrongestCard}')
        Hand.sort(key = lambda x: Cards.index(x))
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
            HiS = Hierachy[i[0]][:13]
            if set(HiS[HiS.index(i)+1:]).issubset(PlayedCards):
                Playable.append(i)
        return random.choice(Playable) if Playable else random.choice(Hand) if Hand else H[0]

def DetectPhase():
    Number = ImageGrab.grab((373, 459, 427, 506))
    Number.save("NumberToTest.png")
    Phaser = 0 if Find("TestIf2.png", "NumberToTest.png") else 1 if Find("TestIf3.png", "NumberToTest.png") else -1
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

    for i in reversed(Hierachy["h"]): 
        if i not in Hs: break    
        PfH+=1

    BetMake = (PfC if PfC != -1 else 0) + (PfS if PfS != -1 else 0) + (PfD if PfD != -1 else 0) + PfH
    print(f'Best Bet: {BetMake}')
    return BetMake

input("Enter to Start...  ")

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
                Play(Bets[Bet][Phase], (0,0))
                Choose = False
                print("-"*100)
            time.sleep(1.5)
            if CheckTurn() == "Y":
                Plays = DetectPhase() == -1 and CheckComplete() == "B"
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
            Play(HandCards[BestPlay(list(HandCards.keys()), TableCards)], (260, 732))
            print("-"*100)
    Plays = False

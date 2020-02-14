# -*- coding: cp1250 -*-
## UWAGA: Algoytm obejmuje tylko podpunkty do tworzenia siecznych włącznie

import arcpy
import math as m
global tol
global k

arcpy.env.overwriteOutput = True

##tol = raw_input("Podaj wartosc tolerancji dla upraszczania budynków [radian]: ")
##k = raw_input ("Podaj minimalną ilość wierzcholkow odcinanych przez sieczna: ")
tol = 0.001
k = 4

#Algorytm generealizacji budynków z zastosowaniem siecznych

##Import danych oraz odczyt geometrii
def dataimport():
    data = arcpy.MakeFeatureLayer_management(r".\Dane.shp","data")
    
    buildings = [] 
    for row in arcpy.da.SearchCursor(data,["OID@","SHAPE@"]):
        parts=[]
        for part in row [1]:
            vertices =[]
            for i in part:
                vertices.append((i.X, i.Y))
            parts.append(vertices)
        buildings.append(parts)
    return buildings

##Obliczanie azymutu
def azymut (X1,X2,Y1,Y2):

    quadrant = m.atan2((Y2-Y1),(X2-X1))
    if quadrant <=0: A = quadrant + m.pi*2
    else: A = quadrant
    return A

##Obliczanie kąta między wierzchołkami
def angle(X1,X2,X3,Y1,Y2,Y3):
    ang = abs(azymut(X2,X3,Y2,Y3)-azymut(X1,X2,Y1,Y2))
    return ang

def distance(X1,X2,Y1,Y2):
    d = m.sqrt((X2-X1)**2+(Y2-Y1)**2)
    return d 
    
###Upraszczanie budynku poprzez pomęcie wierzchołków przy kątach 180+-tol
def uprosc(buildings):
    build_upro=[]
    for build in buildings:
        ver_upro = []
        for part in build:
            vertics = 0
            for pnt in part:
                if vertics ==0:
                    check = angle(part[-1][0],part[0][0],part[1][0],part[-1][1],part[0][1],part[1][1])
                elif vertics==len(part)-1:
                    check = angle(part[-2][0],part[-1][0],part[0][0],part[-2][1],part[-1][1],part[0][1])
                else: check = angle(part[vertics-1][0],part[vertics][0],part[vertics+1][0],part[vertics-1][1],part[vertics][1],part[vertics+1][1])
                if check <= m.pi-float(tol) or check >= m.pi+float(tol) :
                    ver_upro.append(pnt)
                vertics+=1
        build_upro.append(ver_upro)
    return build_upro
    
#Tworzenie pliku shp z uproszczonymi budynkami
def createSHP (data, f_name):
    arcpy.CreateFeatureclass_management(r".\\", str(f_name)+".shp","POLYGON")
    cursor = arcpy.da.InsertCursor(r".\\"+str(f_name)+".shp",["SHAPE@"])
    for build in data:
        cursor.insertRow([build])
    del cursor

###Tworzenie siecznych   
def sieczne(building):
    tworz_sieczne = []
    k = 2
    for pnt in building[2:-2]:
        dist = distance(building[0][0],pnt[0],building[0][1],pnt[1])
        ver_n = k+1
        dicto = {'id':(str(0)+str(k)),'lenght':dist,'vert_num':ver_n}
        tworz_sieczne.append(dicto)
        k+=1
    ver = 1
    for pnt in building[1:]:
        j=ver+2
        for oth in building[ver+2:-1]:
            dist = distance(pnt[0],oth[0],pnt[1],oth[1])
            ver_n = j-ver+1
            dicto = {'id':(str(ver)+str(j)),'lenght':dist,'vert_num':ver_n}
            tworz_sieczne.append(dicto)
            j+=1
        ver+=1
    return tworz_sieczne

def main ():
    data = dataimport()
    simp_build = uprosc(data)
    #createSHP(simp_build, "f_new")
    sieczne(simp_build[4])
main()




    
                            

# -*- coding: cp1250 -*-
import arcpy
import math as m

global tol
global k

arcpy.env.overwriteOutput = True

tol = raw_input("Podaj wartosc tolerancji dla upraszczania budynków [radian]: ")
k = raw_input ("Podaj minimalną ilość wierzcholkow odcinanych przez sieczna: ")

#Algorytm generealizacji z zastosowaniem siecznych

def dataimport():
    data = arcpy.MakeFeatureLayer_management(r".\Dane.shp","data")
    
    buildings = [] 
    for row in arcpy.da.SearchCursor(data,["OID@","SHAPE@"]):
        for part in row [1]:
            vertices =[]
            for i in part:
                vertices.append((i.X, i.Y))
        buildings.append(vertices)
    return buildings

def azymut (X1,X2,Y1,Y2):

    quadrant = m.atan2((Y2-Y1),(X2-X1))
##    print quadrant

    if quadrant <=0: A = quadrant + m.pi*2
    else: A = quadrant
    return A

def angle(X1,X2,X3,Y1,Y2,Y3):

    ang = abs(azymut(X2,X3,Y2,Y3)-azymut(X1,X2,Y1,Y2))
##    print ang
##print X1,Y1,X2,Y2
##    
##Az = azymut(X1,X2,Y1,Y2)
##print Az
##
##ang = angle(X1,X2,X3,Y1,Y2,Y3)
####print ang

def uprosc(buildings):

    build_upro=[]
    for build in buildings:
        vertics = 0
        ver_upro = []
        for pnt in build:
            if vertics ==0:
                check = angle(build[-1][0],build[0][0],build[1][0],build[-1][1],build[0][1],build[1][1])
            elif vertics==len(build)-1:
                check = angle(build[-2][0],build[-1][0],build[0][0],build[-2][1],build[-1][1],build[0][1])
            else: check = angle(build[vertics-1][0],build[vertics][0],build[vertics+1][0],build[vertics-1][1],build[vertics][1],build[vertics+1][1])
            if check <= m.pi-float(tol) or check >= m.pi+float(tol) :
                ver_upro.append(pnt)
            vertics+=1
        build_upro.append(ver_upro)
    return build_upro

def CreateSHP (data, f_name):
    arcpy.CreateFeatureclass_management(r".\\", str(f_name)+".shp","POLYGON")
    cursor = arcpy.da.InsertCursor(r".\\"+str(f_name)+".shp",["SHAPE@"])

    for build in data:
        cursor.insertRow([build])
    del cursor

def main ():
    data = dataimport()
    simp_build = uprosc(data)
    CreateSHP(simp_build, "f_new")

main()
    
                            

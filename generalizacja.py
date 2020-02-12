# -*- coding: cp1250 -*-
import arcpy
import math as m

global tol
global k

arcpy.env.overwriteOutput = True

##tol = raw_input("Podaj wartosc tolerancji dla upraszczania budynk�w [radian]: ")
##k = raw_input ("Podaj minimaln� ilo�� wierzcholkow odcinanych przez sieczna: ")
tol = 0.001
k = 4
#Algorytm generealizacji z zastosowaniem siecznych

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

def azymut (X1,X2,Y1,Y2):

    quadrant = m.atan2((Y2-Y1),(X2-X1))
##  print quadrant

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
    

def createSHP (data, f_name):
    arcpy.CreateFeatureclass_management(r".\\", str(f_name)+".shp","POLYGON")
    cursor = arcpy.da.InsertCursor(r".\\"+str(f_name)+".shp",["SHAPE@"])

    for build in data:
        cursor.insertRow([build])
    del cursor


def distance(X1,X2,Y1,Y2):

    d = m.sqrt((X2-X1)**2+(Y2-Y1)**2)

    return d 

    
def sieczne(building):

    tworz_sieczne = []
    k = 2
    for pnt in building[2:-2]:
        dist = distance(building[0][0],pnt[0],building[0][1],pnt[1])
        #tworz_sieczne.append(str(0)+str(k))
        dicto = {'id':(str(0)+str(k)),'lenght':dist,'vert_num':0}
        tworz_sieczne.append(dicto)
        k+=1
        
    ver = 1
    for pnt in building[1:]:
        j=ver+2
        for oth in building[ver+2:-1]:
            dist = distance(pnt[0],oth[0],pnt[1],oth[1])
            #tworz_sieczne.append(str(ver)+str(j))
            dicto = {'id':(str(ver)+str(j)),'lenght':dist,'vert_num':0}
            tworz_sieczne.append(dicto)
            j+=1
        ver+=1
    
    print tworz_sieczne

def main ():
    data = dataimport()
    simp_build = uprosc(data)
    #createSHP(simp_build, "f_new")
    sieczne(simp_build[4])

main()




    
                            

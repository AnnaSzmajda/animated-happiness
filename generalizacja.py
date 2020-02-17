# -*- coding: cp1250 -*-
## UWAGA: Algoytm obejmuje tylko podpunkty do tworzenia siecznych włącznie

import arcpy
import math as m
global tol
global k
global l_bud

arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False

tol = float(raw_input("Podaj wartosc tolerancji dla upraszczania budynków [stopnie]: "))*m.pi/180
k = int(raw_input ("Podaj minimalną ilość wierzcholkow odcinanych przez sieczne (>2): "))


if k<3: k = int(raw_input ("Podaj minimalną ilość wierzcholkow odcinanych przez sieczne (>2): "))

l_bud= 0

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
def createSHP (data, f_name, *fields):
    shp = arcpy.CreateFeatureclass_management(r".\\", str(f_name)+".shp","POLYGON")
    for field in fields:
        arcpy.AddField_management(shp, field, "Integer")

    column = ["SHAPE@"]+list(fields)
    cursor = arcpy.da.InsertCursor(shp,column)
    for build in data:
        cursor.insertRow(build)
    del cursor

###Tworzenie siecznych   
def sieczne(building):
    a = arcpy.Array([arcpy.Point(*coords) for coords in building])
    build = arcpy.Geometry("POLYGON", a)
    tworz_sieczne = []
    k = 2
    for pnt in building[2:-2]:
        dist = distance(building[0][0],pnt[0],building[0][1],pnt[1])
        ver_n = k+1
        dicto = {'id':(str(0)+str(k)),'lenght':dist,'vert_num':ver_n, 'id_from':0, 'id_to':k}
        geometry = arcpy.Geometry("POLYLINE", arcpy.Array([arcpy.Point(building[0][0],building[0][1]), arcpy.Point(pnt[0],pnt[1])]))
        if geometry.within(build): in_out = 1
        else: in_out = 0
        dicto = {'id':(str(0)+str(k)),'lenght':dist,'vert_num':ver_n, 'id_from':0, 'id_to':k, 'in_out':in_out}
        if not geometry.crosses(build):
            tworz_sieczne.append(dicto)
        k+=1
        
    ver = 1
    for pnt in building[1:]:
        j=ver+2
        for oth in building[ver+2:-1]:
            dist = distance(pnt[0],oth[0],pnt[1],oth[1])
            ver_n = j-ver+1
            geometry = arcpy.Geometry("POLYLINE", arcpy.Array([arcpy.Point(pnt[0],pnt[1]), arcpy.Point(oth[0],oth[1])]))
            if geometry.within(build): in_out = 1
            else: in_out = 0
            dicto = {'id':str(ver)+str(j), 'lenght':dist, 'vert_num':ver_n, 'id_from':ver, 'id_to':j, 'in_out':in_out}
            if not geometry.crosses(build):
                tworz_sieczne.append(dicto)
            j+=1
        ver+=1
    tworz_sieczne = sorted(tworz_sieczne, key=lambda k: k['lenght'])
    return tworz_sieczne

def generalizacja(tworz_sieczne, building):
    global l_bud
    global k
    dicto_xy = {i:building[i] for i in range(len(building))}
    rysuj = []
    xy_sprawdz = {}
    pozostale = []
    odrzuc = 0

    for tworz in tworz_sieczne:
        if tworz['vert_num'] >= k and tworz['id_from'] not in xy_sprawdz.keys() and tworz['id_to'] not in xy_sprawdz.keys():
            i=0
            xy_odrzuc = []
            for vert in range(tworz['id_from'], tworz['id_to']+1):
                if building[vert] not in xy_sprawdz.keys():
                    if i != 0 and  i != tworz['id_to']-tworz['id_from']:
                        if len(dicto_xy)-len(xy_sprawdz) <=5 : break
                        xy_sprawdz[vert] = building[vert]
                    xy_odrzuc.append(building[vert])
                    i+=1
            rysuj.append([xy_odrzuc, l_bud, odrzuc, tworz['in_out']])
            odrzuc += 1


    for pnt in dicto_xy:
        if pnt not in xy_sprawdz: pozostale.append(dicto_xy[pnt])

    l_bud += 1

    return (rysuj, [odrzuc])



def main ():
    data = dataimport()
    simp_build = uprosc(data)
    result = [generalizacja(sieczne(i),i) for i in simp_build]
    odrzucone = []
    pozostale = []
    for build in result:
        odrzucone += build[0]
        pozostale+= [build[1]]
        
    createSHP(odrzucone, "f_odrzucone","id","id_s","in_out")
    createSHP(pozostale, "f_pozostale")
main()

if __name__ == '__main__':
    main()



    
                            

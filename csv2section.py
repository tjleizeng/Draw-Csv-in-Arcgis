import arcpy
import types
import os
import math

def getdis(x1,y1,x2,y2):
    C = math.sin(y1/57.2958)*math.sin(y2/57.2958) + math.cos(y1/57.2958)*math.cos(y2/57.2958)*math.cos((x1-x2)/57.2958)
    return 6371004*math.acos(C)

def getXY(x1,y1,x2,y2):
    dist=0
    if(x1 != x2 or y1 != y2):
        dist=getdis(x1,y1,x2,y2)
    prop=0.2
    if(dist>1500):
        prop=300/dist
    newX1=(x2-x1)*prop+x1
    newY1=(y2-y1)*prop+y1
    newX2=(x2-x1)*(1-prop)+x1
    newY2=(y2-y1)*(1-prop)+y1
    return (newX1,newY1,newX2,newY2)

def csv2section():
    arcpy.env.overwriteOutput = True
    inPt       = arcpy.GetParameterAsText(0)
    outFeature = arcpy.GetParameterAsText(1)
    X1     = arcpy.GetParameterAsText(2)
    Y1     = arcpy.GetParameterAsText(3)
    X2     = arcpy.GetParameterAsText(4)
    Y2     = arcpy.GetParameterAsText(5)
    reserveField   = arcpy.GetParameterAsText(6)

    try:

        outPath, outFC = os.path.split(outFeature)

        #change C:\Users\leizengxiang\Desktop\drawCsvInArcgis to your directory, and change the wgs84.prj to your project information file
        arcpy.CreateFeatureclass_management(outPath, outFC, "POLYLINE", "", "DISABLED", "ENABLED",
            "C:\Users\leizengxiang\Desktop\drawCsvInArcgis\\wgs84.prj")

        if reserveField:
            field = arcpy.ListFields(inPt, reserveField)[0]
            arcpy.AddField_management(outFeature, field.name, field.type)

        oCur, iCur, sRow, feat = None, None, None, None

        shapeName = "Shape"
        idName = "id"

        oCur = arcpy.SearchCursor(inPt)
        iCur = arcpy.InsertCursor(outFeature)
        array = arcpy.Array()
        ID = -1
        PID = 0
        LID = 0
        if reserveField:
            RESERVE = 0
        TEMPX1 = 0
        TEMPX2 = 0 
        TEMPY1 = 0
        TEMPY2 = 0

        for sRow in oCur:
            TEMPX1 = sRow.getValue(X1)
            TEMPX2 = sRow.getValue(X2)
            TEMPY1 = sRow.getValue(Y1)
            TEMPY2 = sRow.getValue(Y2)
            (TEMPX1,TEMPY1,TEMPX2,TEMPY2)=getXY(TEMPX1,TEMPY1,TEMPX2,TEMPY2)
            pt1=arcpy.Point(TEMPX1,TEMPY1,None, None, PID)
            PID += 1
            pt2=arcpy.Point(TEMPX2,TEMPY2,None, None, PID)
            PID += 1
            array.add(pt1)
            array.add(pt2)
            if reserveField:
                RESERVE = sRow.getValue(reserveField)
            feat = iCur.newRow()
            feat.setValue(shapeName, array)
            LID += 1
            if reserveField:
                feat.setValue(reserveField, RESERVE)
            iCur.insertRow(feat)
            array.removeAll()  

    except Exception as err:
        arcpy.AddError(err[0])

    finally:
        if oCur:
            del oCur
        if iCur:
            del iCur
        if sRow:
            del sRow
        if feat:
            del feat
        try:
            # Update the spatial index(es)
            #
            r = arcpy.CalculateDefaultGridIndex_management(outFeature)
            arcpy.AddSpatialIndex_management(outFeature, r.getOutput(0), r.getOutput(1), r.getOutput(2))
        except:
            pass


if __name__ == '__main__':
    csv2section()

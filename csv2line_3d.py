import arcpy
import types
import os
import math


def getdis(x1,y1,x2,y2):
    C = math.sin(y1/57.2958)*math.sin(y2/57.2958) + math.cos(y1/57.2958)*math.cos(y2/57.2958)*math.cos((x1-x2)/57.2958)
    return 6371004*math.acos(C)

def getmax(x1, x2):
    if(x1 > x2):
        return x1
    else:
        return x2

def csv2line():
    arcpy.env.overwriteOutput = True
    inPt       = arcpy.GetParameterAsText(0)
    outFeature = arcpy.GetParameterAsText(1)
    X     = arcpy.GetParameterAsText(2)
    Y     = arcpy.GetParameterAsText(3)
    Z     = arcpy.GetParameterAsText(4)
    idField   = arcpy.GetParameterAsText(5)
    reserveField   = arcpy.GetParameterAsText(6)
    maxvField = "MAX_V"

    try:

        outPath, outFC = os.path.split(outFeature)

        #change C:\Users\leizengxiang\Desktop\drawCsvInArcgis to your directory, and change the wgs84.prj to your project information file
        arcpy.CreateFeatureclass_management(outPath, outFC, "POLYLINE", "", "DISABLED", "ENABLED",
            "C:\Users\leizengxiang\Desktop\drawCsvInArcgis\\wgs84.prj")

        field1 = arcpy.ListFields(inPt, idField)[0]
        arcpy.AddField_management(outFeature, field1.name, field1.type)
        if reserveField:
            field2 = arcpy.ListFields(inPt, reserveField)[0]
            arcpy.AddField_management(outFeature, field2.name, field2.type)
        # Add v
        arcpy.AddField_management(outFeature, maxvField, "double")

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
        MAXV = 0
        TEMPV = 0
        X1 = 0
        X2 = 0 
        Y1 = 0
        Y2 = 0
        Z1 = 0
        Z2 = 0

        for sRow in oCur:
            X2 = sRow.getValue(X)
            Y2 = sRow.getValue(Y)
            Z2 = sRow.getValue(Z)
            pt=arcpy.Point(X2,Y2,Z2, None, PID)
            PID += 1
            currentValue = sRow.getValue(idField)
            if ID == -1:
                ID = currentValue
                if reserveField:
                    RESERVE = sRow.getValue(reserveField)
                X1 = X2
                Y1 = Y2
                Z1 = Z2
            if ID <> currentValue:
                if array.count >= 2:
                    feat = iCur.newRow()
                    feat.setValue(idField, ID)
                    feat.setValue(shapeName, array)
                    feat.setValue(idName, LID)
                    LID += 1
                    if reserveField:
                        feat.setValue(reserveField, RESERVE)
                    feat.setValue(maxvField,MAXV)
                    iCur.insertRow(feat)

                else:
                    arcpy.AddIDMessage("WARNING", 1059, str(ID))

                X1 = X2
                Y1 = Y2
                Z1 = Z2
                MAXV = 0
                array.removeAll()
                if reserveField:
                    RESERVE = sRow.getValue(reserveField)

            if (Z1<Z2) and (X1 != X2 or Y1 != Y2):
                TEMPV = 0.36*getdis(X1,Y1,X2,Y2)/(Z2 - Z1) #KM/H
            else:
                TEMPV = 0
            MAXV = getmax(MAXV,TEMPV)
            array.add(pt)
            X1 = X2
            Y1 = Y2
            Z1 = Z2
            ID = currentValue

        if array.count > 1:
            feat = iCur.newRow()
            feat.setValue(idField, currentValue)
            feat.setValue(shapeName, array)
            feat.setValue(idName, LID)
            if reserveField:
                feat.setValue(reserveField, RESERVE)
            feat.setValue(maxvField,MAXV)
            iCur.insertRow(feat)
        else:
            arcpy.AddIDMessage("WARNING", 1059, str(ID))
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
    csv2line()

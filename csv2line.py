import arcpy
import types
import os
import math


def csv2line():
    arcpy.env.overwriteOutput = True
    inPt       = arcpy.GetParameterAsText(0)
    outFeature = arcpy.GetParameterAsText(1)
    X     = arcpy.GetParameterAsText(2)
    Y     = arcpy.GetParameterAsText(3)
    idField   = arcpy.GetParameterAsText(4)
    reserveField   = arcpy.GetParameterAsText(5)

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
        X1 = 0
        X2 = 0 
        Y1 = 0
        Y2 = 0

        for sRow in oCur:
            X2 = sRow.getValue(X)
            Y2 = sRow.getValue(Y)
            pt=arcpy.Point(X2,Y2,0, None, PID)
            PID += 1
            currentValue = sRow.getValue(idField)
            if ID == -1:
                ID = currentValue
                if reserveField:
                    RESERVE = sRow.getValue(reserveField)
                X1 = X2
                Y1 = Y2
            if ID <> currentValue:
                if array.count >= 2:
                    feat = iCur.newRow()
                    feat.setValue(idField, ID)
                    feat.setValue(shapeName, array)
                    feat.setValue(idName, LID)
                    LID += 1
                    if reserveField:
                        feat.setValue(reserveField, RESERVE)
                    iCur.insertRow(feat)

                else:
                    arcpy.AddIDMessage("WARNING", 1059, str(ID))

                X1 = X2
                Y1 = Y2
                array.removeAll()
                if reserveField:
                    RESERVE = sRow.getValue(reserveField)

            array.add(pt)
            X1 = X2
            Y1 = Y2
            ID = currentValue

        if array.count > 1:
            feat = iCur.newRow()
            feat.setValue(idField, currentValue)
            feat.setValue(shapeName, array)
            feat.setValue(idName, LID)
            if reserveField:
                feat.setValue(reserveField, RESERVE)
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

import requests
from xml.dom import minidom
import sqlite3

print("-----------Polymath Ventures Engineering Challenge------------")
conn = sqlite3.connect('categories.db')
c = conn.cursor()
while True:

    var = input("./categories ")

    if var == '--rebuild':

        xml = """<?xml version="1.0" encoding="utf-8"?>
                <GetCategoriesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                <RequesterCredentials>
                <eBayAuthToken>AgAAAA**AQAAAA**aAAAAA**PlLuWA**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GlDpaDpAudj6x9nY+seQ**LyoEAA**AAMAAA**wSd/jBCbxJHbYuIfP4ESyC0mHG2Tn4O3v6rO2zmnoVSF614aVDFfLSCkJ5b9wg9nD7rkDzQayiqvwdWeoJkqEpNQx6wjbVQ1pjiIaWdrYRq+dXxxGHlyVd+LqL1oPp/T9PxgaVAuxFXlVMh6wSyoAMRySI6QUzalepa82jSQ/qDaurz40/EIhu6+sizj0mCgjcdamKhp1Jk3Hqmv8FXFnXouQ9Vr0Qt+D1POIFbfEg9ykH1/I2CYkZBMIG+k6Pf00/UujbQdne6HUAu6CSj9wGsqQSAEPIXXvEnVmtU+6U991ZUhPuA/DMFEfVlibvNLBA7Shslp2oTy2T0wlpJN+f/Jle3gurHLIPc6EkEmckEpmSpFEyuBKz+ix4Cf4wYbcUk/Gr3kGdSi20XQGu/ZnJ7Clz4vVak9iJjN99j8lwA2zKW+CBRuHBjZdaUiDctSaADHwfz/x+09bIU9icgpzuOuKooMM5STbt+yJlJZdE3SRZHwilC4dToTQeVhAXA4tFZcDrZFzBmJsoRsJYrCdkJBPeGBub+fqomQYyKt1J0LAQ5Y0FQxLHBIp0cRZTPAuL/MNxQ/UXcxQTXjoCSdZd7B55f0UapU3EsqetEFvIMPxCPJ63YahVprODDva9Kz/Htm3piKyWzuCXfeu3siJvHuOVyx7Q4wyHrIyiJDNz5b9ABAKKauxDP32uqD7jqDzsVLH11/imKLLdl0U5PN+FP30XAQGBAFkHf+pAvOFLrdDTSjT3oQhFRzRPzLWkFg</eBayAuthToken>
                </RequesterCredentials>
                <CategorySiteID>0</CategorySiteID>
                <DetailLevel>ReturnAll</DetailLevel>
                </GetCategoriesRequest>"""

        headers = {"X-EBAY-API-CALL-NAME": "GetCategories",
                   "X-EBAY-API-APP-NAME":"EchoBay62-5538-466c-b43b-662768d6841",
                   "X-EBAY-API-CERT-NAME":"00dd08ab-2082-4e3c-9518-5f4298f296db",
                   "X-EBAY-API-DEV-NAME":"16a26b1b-26cf-442d-906d-597b60c41c19",
                   "X-EBAY-API-SITEID":"0",
                   "X-EBAY-API-COMPATIBILITY-LEVEL":"861"}

        response = requests.post("https://api.sandbox.ebay.com/ws/api.dll", data=xml, headers=headers)


        file = open("kml.kml", "w")
        file.write(response.text)
        file.close()

        xmldoc = minidom.parse("kml.kml")
        GeteBayOfficialTimeResponse = xmldoc.getElementsByTagName("GetCategoriesResponse")[0]
        CategoryArray = GeteBayOfficialTimeResponse.getElementsByTagName("CategoryArray")[0]
        Categories = GeteBayOfficialTimeResponse.getElementsByTagName("Category")


        c.execute("DROP TABLE IF EXISTS categoriesParams")
        c.execute('CREATE TABLE IF NOT EXISTS categoriesParams (id INTEGER, CategoryName TEXT, CategoryLevel INTEGER, BestOfferEnabled TEXT, CategoryParentID INTEGER)')

        for category in Categories:
            id = category.getElementsByTagName("CategoryID")[0].childNodes[0].data
            CategoryName = category.getElementsByTagName("CategoryName")[0].childNodes[0].data
            CategoryLevel = category.getElementsByTagName("CategoryLevel")[0].childNodes[0].data
            BestOfferEnabled = ((category.getElementsByTagName("BestOfferEnabled")[0].childNodes[0].data) if len(category.getElementsByTagName("BestOfferEnabled"))>0 else "")
            CategoryParentID = category.getElementsByTagName("CategoryParentID")[0].childNodes[0].data
            print(id + ' ' + CategoryName + ' ' + CategoryLevel + ' ' + BestOfferEnabled + ' ' + CategoryParentID)

            c.execute("INSERT INTO categoriesParams (id , CategoryName , CategoryLevel , BestOfferEnabled , CategoryParentID ) VALUES (? , ? , ? , ? , ? )",
                        (id, CategoryName, CategoryLevel, BestOfferEnabled, CategoryParentID))
            conn.commit()


    elif (var.split(" ")[0] == '--render')&(len(var.split(" "))>1):
        print("Searching id: "+var.split(" ")[1])
        idParam = var.split(" ")[1]

        c.execute('SELECT * FROM categoriesParams WHERE id=?', (idParam,))
        father = c.fetchall()

        if len(father)>0:
            data={}
            data['father'] = father

            c.execute('SELECT * FROM categoriesParams WHERE  CategoryLevel>? AND CategoryParentID=?', (1,idParam))
            data['children'] = c.fetchall()
            grandchildren = []
            for row in data['children']:
                c.execute('SELECT * FROM categoriesParams WHERE id!=? AND CategoryParentID=?', (row[0],row[0]))
                grandchildren = grandchildren + c.fetchall()
                print(grandchildren)
                print("------------------------------------------------")

            data['grandchildren'] = grandchildren

            greatgrandchild = []
            for row in data['grandchildren']:
                c.execute('SELECT * FROM categoriesParams WHERE id!=? AND CategoryParentID=?', (row[0],row[0]))
                greatgrandchild = greatgrandchild + c.fetchall()
                print(greatgrandchild)
                print("------------------------------------------------")

            data['greatgrandchild'] = greatgrandchild

            print(data)


            htmlName = idParam+'.html'
            f = open(htmlName,'w')

            childrenRows = """"""
            for element in data['children']:
                childrenRows = childrenRows+"""
                <tr>
                  <th scope="row">"""+str(element[0])+"""</th>
                  <td>"""+element[1]+"""</td>
                  <td>"""+str(element[2])+"""</td>
                  <td>"""+str(element[4])+"""</td>
                </tr>"""

            grandchildrenRows = """"""
            for element in data['grandchildren']:
                grandchildrenRows = grandchildrenRows+"""
                <tr>
                  <th scope="row">"""+str(element[0])+"""</th>
                  <td>"""+element[1]+"""</td>
                  <td>"""+str(element[2])+"""</td>
                  <td>"""+str(element[4])+"""</td>
                </tr>"""

            greatgrandchildRows = """"""
            for element in data['greatgrandchild']:
                greatgrandchildRows = greatgrandchildRows+"""
                <tr>
                  <th scope="row">"""+str(element[0])+"""</th>
                  <td>"""+element[1]+"""</td>
                  <td>"""+str(element[2])+"""</td>
                  <td>"""+str(element[4])+"""</td>
                </tr>"""

            message = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Polymath Ventures Engineering Challenge</title>
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css" integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4" crossorigin="anonymous">
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            </head>
            <body>

                <h1>Category """ + idParam + """: """ + data['father'][0][1]+ """</h1>
                <table class="table">
                  <thead class="thead-dark">
                    <tr>
                      <th scope="col">Id</th>
                      <th scope="col">Category Name</th>
                      <th scope="col">Category Level</th>
                      <th scope="col">Category Parent Id</th>
                    </tr>
                  </thead>
                  <tbody>

                    <tr>
                      <th scope="row">"""+str(data['father'][0][0])+"""</th>
                      <td>"""+data['father'][0][1]+"""</td>
                      <td>"""+str(data['father'][0][2])+"""</td>
                      <td>"""+str(data['father'][0][4])+"""</td>
                    </tr>
                  </tbody>

                </table>

                <h1>Childrens</h1>
                <table class="table">
                  <thead class="thead-dark">
                    <tr>
                      <th scope="col">Id</th>
                      <th scope="col">Category Name</th>
                      <th scope="col">Category Level</th>
                      <th scope="col">Category Parent Id</th>
                    </tr>
                  </thead>
                  <tbody>

                  """+childrenRows+"""

                  </tbody>

                </table>

                <h1>Grandchildrens</h1>

                <table class="table">
                  <thead class="thead-dark">
                    <tr>
                      <th scope="col">Id</th>
                      <th scope="col">Category Name</th>
                      <th scope="col">Category Level</th>
                      <th scope="col">Category Parent Id</th>
                    </tr>
                  </thead>
                  <tbody>

                  """+grandchildrenRows+"""

                  </tbody>

                </table>

                <h1>Great Grandchild</h1>

                <table class="table">
                  <thead class="thead-dark">
                    <tr>
                      <th scope="col">Id</th>
                      <th scope="col">Category Name</th>
                      <th scope="col">Category Level</th>
                      <th scope="col">Category Parent Id</th>
                    </tr>
                  </thead>
                  <tbody>

                  """+greatgrandchildRows+"""

                  </tbody>

                </table>


                <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.0/umd/popper.min.js" integrity="sha384-cs/chFZiN24E4KMATLdqdvsezGxaGsi4hLGOzlXwp5UZB1LY//20VyM2taTB4QvJ" crossorigin="anonymous"></script>
                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js" integrity="sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm" crossorigin="anonymous"></script>
            </body>
            </html>
            """

            f.write(message)
            f.close()
        else:
            print("No category with ID: "+var.split(" ")[1])

c.close()
conn.close()

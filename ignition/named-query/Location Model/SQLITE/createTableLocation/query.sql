CREATE TABLE "Location" (
	"LocationID"	INTEGER NOT NULL,
	"ParentLocationID" INTEGER,
	"LocationTypeID" INTEGER,
	"Name"	TEXT NOT NULL DEFAULT 'New Name',
	"Description" TEXT,
	"isActive"	INTEGER DEFAULT 1,
	"LastModifiedBy" TEXT,
	"LastModifiedOn" TEXT,
	"ZoomLevel" INTEGER,
	"Latitude" TEXT,
	"Longitude" TEXT,
	"MQTTPath" TEXT,
	"LocationTypeDefinitionID" INT,
	"MapCallID" INTEGER,
	"HmiUrl" TEXT,
	"orderNumber" INTEGER,
	"SCADAView" INTEGER,
	"shortName" TEXT,
	PRIMARY KEY("LocationID" AUTOINCREMENT),
	CONSTRAINT "FK_Location_LocationType" FOREIGN KEY("LocationTypeID") REFERENCES "LocationType"
)
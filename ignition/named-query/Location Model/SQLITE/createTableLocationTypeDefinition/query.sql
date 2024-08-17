CREATE TABLE "LocationTypeDefinition" (
	"LocationTypeDefinitionID"	INTEGER NOT NULL,
	"LocationTypeID" INTEGER NOT NULL DEFAULT 1,
	"Name"	TEXT NOT NULL DEFAULT 'New Name',
	"Description" TEXT,
	"isActive"	INTEGER DEFAULT 1,
	"LastModifiedBy" TEXT,
	"LastModifiedOn" TEXT,
	"UDTPath" TEXT,
	"IgnitionTemplatePath" TEXT,
	"IgnitionPIDTemplatePath" TEXT,
	PRIMARY KEY("LocationTypeDefinitionID" AUTOINCREMENT),
	CONSTRAINT "FK_LocationTypeDefinition_LocationType" FOREIGN KEY("LocationTypeID") REFERENCES "LocationType"
)
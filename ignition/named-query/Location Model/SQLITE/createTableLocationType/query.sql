CREATE TABLE "LocationType" (
	"LocationTypeID"	INTEGER NOT NULL,
	"Name"	TEXT NOT NULL DEFAULT 'New Name',
	"Description" TEXT,
	"Icon" TEXT,
	"isActive"	INTEGER DEFAULT 1,
	"LastModifiedBy" TEXT,
	"LastModifiedOn" TEXT,
	PRIMARY KEY("LocationTypeID" AUTOINCREMENT)
)
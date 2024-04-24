CREATE TABLE "Launch" (
    "ID" int   NOT NULL,
    "Name" string   NOT NULL,
    "Date" string   NULL,
    "Location" string   NULL,
    "Pad" string   NULL,
    CONSTRAINT "pk_Launch" PRIMARY KEY (
        "ID"
     )
);

CREATE TABLE "User" (
    "ID" int   NOT NULL,
    "Username" string   NOT NULL,
    "Email" email   NOT NULL,
    "Password" password   NOT NULL,
    "Bio" string(300)   NULL,
    "Location" string   NULL,
    "Img_URL" url   NULL,
    "Header_Img_URL" url   NULL,
    CONSTRAINT "pk_User" PRIMARY KEY (
        "ID"
     ),
    CONSTRAINT "uc_User_Username" UNIQUE (
        "Username"
    ),
    CONSTRAINT "uc_User_Email" UNIQUE (
        "Email"
    )
);

CREATE TABLE "Collection" (
    "ID" int   NOT NULL,
    "Name" string(50)   NOT NULL,
    "Description" string(150)   NULL,
    "CreatedDate" dateTime  DEFAULT getutcdate() NOT NULL,
    "CreatedBy" int   NOT NULL,
    CONSTRAINT "pk_Collection" PRIMARY KEY (
        "ID"
     )
);

CREATE TABLE "Launch_Collections" (
    "CollectionsID" int   NOT NULL,
    "LaunchID" int   NOT NULL
);

ALTER TABLE "Collection" ADD CONSTRAINT "fk_Collection_CreatedBy" FOREIGN KEY("CreatedBy")
REFERENCES "User" ("ID");

ALTER TABLE "Launch_Collections" ADD CONSTRAINT "fk_Launch_Collections_CollectionsID" FOREIGN KEY("CollectionsID")
REFERENCES "Collection" ("ID");

ALTER TABLE "Launch_Collections" ADD CONSTRAINT "fk_Launch_Collections_LaunchID" FOREIGN KEY("LaunchID")
REFERENCES "Launch" ("ID");

CREATE INDEX "idx_Launch_Name"
ON "Launch" ("Name");

CREATE INDEX "idx_Collection_Name"
ON "Collection" ("Name");


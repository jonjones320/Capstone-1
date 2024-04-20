-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.

-- Modify this code to update the DB schema diagram.
-- To reset the sample schema, replace everything with
-- two dots ('..' - without quotes).

CREATE TABLE "Launch" (
    "LaunchID" int   NOT NULL,
    "Name" string   NOT NULL,
    "Date" string   NULL,
    "Location" string   NULL,
    "Pad" string   NULL,
    CONSTRAINT "pk_Launch" PRIMARY KEY (
        "LaunchID"
     )
);

CREATE TABLE "List" (
    "ListID" int   NOT NULL,
    "LaunchID" int   NOT NULL,
    "CreatedBy" string   NOT NULL,
    "CreatedDate" dateTime  DEFAULT getutcdate() NOT NULL,
    CONSTRAINT "pk_List" PRIMARY KEY (
        "ListID"
     )
);

CREATE TABLE "User" (
    "UserID" int   NOT NULL,
    "Username" string   NOT NULL,
    "Password" string   NOT NULL,
    CONSTRAINT "pk_User" PRIMARY KEY (
        "UserID"
     ),
    CONSTRAINT "uc_User_Username" UNIQUE (
        "Username"
    )
);

CREATE TABLE "Favorite" (
    "UserID" int   NOT NULL,
    "ListID" int   NOT NULL
);

ALTER TABLE "List" ADD CONSTRAINT "fk_List_LaunchID" FOREIGN KEY("LaunchID")
REFERENCES "Launch" ("LaunchID");

ALTER TABLE "List" ADD CONSTRAINT "fk_List_CreatedBy" FOREIGN KEY("CreatedBy")
REFERENCES "User" ("UserID");

ALTER TABLE "Favorite" ADD CONSTRAINT "fk_Favorite_UserID" FOREIGN KEY("UserID")
REFERENCES "User" ("UserID");

ALTER TABLE "Favorite" ADD CONSTRAINT "fk_Favorite_ListID" FOREIGN KEY("ListID")
REFERENCES "List" ("ListID");

CREATE INDEX "idx_Launch_Name"
ON "Launch" ("Name");


# Script used to create database

CREATE TABLE guestlist (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    party_size INTEGER NOT NULL DEFAULT 1,
    over_21 INTEGER NOT NULL DEFAULT 0,
    rsvp INTEGER NOT NULL DEFAULT 0,
    responded_rsvp TEXT DEFAULT "No",
    email TEXT,
    phone_number TEXT,
    events_invited TEXT DEFAULT "",
    Shreya_Haldi TEXT DEFAULT "",
    Aman_Haldi TEXT DEFAULT "",
    Sangeet TEXT DEFAULT "",
    Wedding TEXT DEFAULT "",
    Reception TEXT DEFAULT "",
    guest_names TEXT DEFAULT ""
);

# AKIA4M3WREY6CPSFWKGY
# GYLDrwPJomQphuoxY1BsRDlpBP/uwU9qk+PzNm3S
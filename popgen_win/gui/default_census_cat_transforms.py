# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand 
# Copyright (C) 2009, Arizona State University
# See PopGen/License

DEFAULT_PERSON_PUMS2000_QUERIES = [ "alter table person_pums add column page bigint",
                                "alter table person_pums add column pgender bigint",
                                "alter table person_pums add column prace bigint",
                                "alter table person_pums add column employment bigint",

                                "alter table person_pums add column pclwkr bigint",
                                "alter table person_pums add column pearns bigint",
                                "alter table person_pums add column peduc bigint",
                                "alter table person_pums add column penroll bigint",
                                "alter table person_pums add column phours bigint",
                                "alter table person_pums add column pndnaics bigint",                                   
                                "alter table person_pums add column pocccen bigint",                                   
                                "alter table person_pums add column ptrvmns bigint",                                   

                                "update person_pums set pearns = earns",
                                "update person_pums set peduc = educ",
                                "update person_pums set penroll = enroll",
                                "update person_pums set pndnaics = indnaics",
                                "update person_pums set pocccen = occcen5",
                                "update person_pums set ptrvmns = trvmns",
 
                                #original recodes
                                "update person_pums set page = 1 where age < 5",
                                "update person_pums set page = 2 where age >= 5 and age < 15",
                                "update person_pums set page = 3 where age >= 15 and age < 25",
                                "update person_pums set page = 4 where age >= 25 and age < 35",
                                "update person_pums set page = 5 where age >= 35 and age < 45",
                                "update person_pums set page = 6 where age >= 45 and age < 55",
                                "update person_pums set page = 7 where age >= 55 and age < 65",
                                "update person_pums set page = 8 where age >= 65 and age < 75",
                                "update person_pums set page = 9 where age >= 75 and age < 85",
                                "update person_pums set page = 10 where age >= 85",

                                # Recodes for UrbanSim for SF, Lane County, Hawaii
                                #"update person_pums set page = 1 where age < 15",
                                #"update person_pums set page = 2 where age >= 15 and age < 35",
                                #"update person_pums set page = 3 where age >= 35 and age < 55",
                                #"update person_pums set page = 4 where age >= 55 and age < 75",
                                #"update person_pums set page = 5 where age >= 75",

                                "update person_pums set pgender = sex",
                                "update person_pums set prace = 1 where race1 = 1",
                                "update person_pums set prace = 2 where race1 = 2",
                                "update person_pums set prace = 3 where race1 >=3 and race1 <= 5",
                                "update person_pums set prace = 4 where race1 = 6",
                                "update person_pums set prace = 5 where race1 = 7",
                                "update person_pums set prace = 6 where race1 = 8",
                                "update person_pums set prace = 7 where race1 = 9",
                                "update person_pums set employment = 1 where esr = 0",
                                "update person_pums set employment = 2 where esr = 1 or esr = 2 or esr = 4 or esr = 5",
                                "update person_pums set employment = 3 where esr = 3",
                                "update person_pums set employment = 4 where esr = 6",

                                # employed civilians
                                "update person_pums set pclwkr = 1 where clwkr = 1",
                                "update person_pums set pclwkr = 2 where clwkr = 2",
                                "update person_pums set pclwkr = 3 where clwkr = 3",
                                "update person_pums set pclwkr = 4 where clwkr = 4",
                                "update person_pums set pclwkr = 5 where clwkr = 5",
                                "update person_pums set pclwkr = 6 where clwkr = 6",
                                "update person_pums set pclwkr = 7 where clwkr = 7",
                                "update person_pums set pclwkr = 8 where clwkr = 8",
                                "update person_pums set pclwkr = 9 where esr = 0", #15 and younger
                                "update person_pums set pclwkr = 10 where esr = 4 or esr = 5", #In armed forces
                                "update person_pums set pclwkr = 11 where esr = 3",# Unemployed 
                                "update person_pums set pclwkr = 12 where esr = 6", #Not in labor force


                                "update person_pums set phours = 1 where wrklyr = 2", #did not work in 1999
                                "update person_pums set phours = 2 where hours >= 1 and hours < 15", 
                                "update person_pums set phours = 3 where hours >= 15 and hours < 35", 
                                "update person_pums set phours = 4 where hours >= 35", 
                                "update person_pums set phours = 5 where esr = 0", #15 and younger


                                "drop table person_sample",
                                """create table person_sample select state, pumano, hhid, serialno, """\
                                        """pnum, age, page, pgender, prace, employment, relate, pclwkr, pearns, """\
                                        """peduc, penroll, phours, pndnaics, pocccen, ptrvmns """\
                                        """from person_pums""",
                                "alter table person_sample add index(serialno, pnum)",
                                "drop table hhld_sample_temp",
                                "alter table hhld_sample drop column hhldrage",
                                "alter table hhld_sample rename to hhld_sample_temp",
                                "drop table hhld_sample",

                                #original recodes    
                                #"""create table hhld_sample select hhld_sample_temp.*, """\
                                #        """p1age as hhldrage from hhld_sample_temp left """\
                                #        """join person_sample using(serialno) where relate = 1""",
                                    
                                #"alter table hhld_sample add index(serialno)",
                                #"update hhld_sample set hhldrage = 1 where hhldrage <=7 ",
                                #"update hhld_sample set hhldrage = 2 where hhldrage >7"]

                                # Recodes for UrbanSim SF, Lane County, Hawaii
                                """create table hhld_sample select hhld_sample_temp.*, """\
                                        """page as hhldrage, prace as hhldrrace from hhld_sample_temp left """\
                                        """join person_sample using(serialno) where relate = 1""",
                                """alter table person_sample drop column age""",    
                                "alter table hhld_sample add index(serialno)",
                                "update hhld_sample set hhldrage = 1 where hhldrage <=7 ",
                                "update hhld_sample set hhldrage = 2 where hhldrage >7"]

DEFAULT_PERSON_PUMSACS_QUERIES = ["alter table person_pums change agep age bigint",
                                  "alter table person_pums change puma pumano bigint",
                                  "alter table person_pums change rac1p race1 bigint",
                                  "alter table person_pums change st state bigint",
                                  "alter table person_pums change sporder pnum bigint",
                                  "alter table person_pums change rel relate bigint",

                                  "alter table person_pums add column agep bigint",
                                  "alter table person_pums add column gender bigint",
                                  "alter table person_pums add column race bigint",
                                  "alter table person_pums add column employment bigint",
                                  "update person_pums set agep = 1 where age < 5",
                                  "update person_pums set agep = 2 where age >= 5 and age < 15",
                                  "update person_pums set agep = 3 where age >= 15 and age < 25",
                                  "update person_pums set agep = 4 where age >= 25 and age < 35",
                                  "update person_pums set agep = 5 where age >= 35 and age < 45",
                                  "update person_pums set agep = 6 where age >= 45 and age < 55",
                                  "update person_pums set agep = 7 where age >= 55 and age < 65",
                                  "update person_pums set agep = 8 where age >= 65 and age < 75",
                                  "update person_pums set agep = 9 where age >= 75 and age < 85",
                                  "update person_pums set agep = 10 where age >= 85",
                                  "update person_pums set gender = sex",
                                  "update person_pums set race = 1 where race1 = 1",
                                  "update person_pums set race = 2 where race1 = 2",
                                  "update person_pums set race = 3 where race1 >=3 and race1 <= 5",
                                  "update person_pums set race = 4 where race1 = 6",
                                  "update person_pums set race = 5 where race1 = 7",
                                  "update person_pums set race = 6 where race1 = 8",
                                  "update person_pums set race = 7 where race1 = 9",
                                  "update person_pums set employment = 1 where esr = 0",
                                  "update person_pums set employment = 2 where esr = 1 or esr = 2 or esr = 4 or esr = 5",
                                  "update person_pums set employment = 3 where esr = 3",
                                  "update person_pums set employment = 4 where esr = 6",


                                  "alter table person_pums add index(serialno)",

                                   "create table person_pums1 select person_pums.*, hhid from person_pums left join serialcorr using(serialno)",
                                  "update person_pums1 set serialno = hhid",

                                  "drop table person_sample",

                                  "create table person_sample select state, pumano, hhid, serialno, pnum, agep, gender, race, employment, relate from person_pums1",
                                  "alter table person_sample add index(serialno, pnum)",

                                  "drop table hhld_sample_temp",
                                  "alter table hhld_sample drop column hhldrage",
                                  "alter table hhld_sample rename to hhld_sample_temp",
                                  "drop table hhld_sample",
                                  "create table hhld_sample select hhld_sample_temp.*, agep as hhldrage from hhld_sample_temp left join person_sample using(serialno) where relate = 0",
                                  "alter table hhld_sample add index(serialno)",
                                  "update hhld_sample set hhldrage = 1 where hhldrage <=7 ",
                                  "update hhld_sample set hhldrage = 2 where hhldrage >7",
                                  "drop table hhld_sample_temp",
                                  "drop table person_pums1"]


DEFAULT_HOUSING_PUMS2000_QUERIES = ["alter table housing_pums add index(serialno)",
                                "alter table housing_pums add column hhtype bigint",
                                "alter table housing_pums add column hhldtype bigint",
                                "alter table housing_pums add column hhldinc bigint",
                                "alter table housing_pums add column hhldtenure bigint",
                                "alter table housing_pums add column hhldsize bigint",
                                "alter table housing_pums add column hhchildpresence bigint",
                                "alter table housing_pums add column groupquarter bigint",
                                "alter table housing_pums add column hhldfam bigint",

                                "alter table housing_pums add column htenure bigint",
                                "alter table housing_pums add column hbldgsz bigint",
                                "alter table housing_pums add column hvehicl bigint",
                                "alter table housing_pums add column hgrent bigint",
                                "alter table housing_pums add column hvalue bigint",
                                "alter table housing_pums add column hyrbuilt bigint",
                                "alter table housing_pums add column hyrmoved bigint",
                        

                                "update housing_pums set hvehicl = vehicl",
                                "update housing_pums set hgrent = grent",
                                "update housing_pums set hvalue = value",
                                "update housing_pums set hyrbuilt = yrbuilt",

                                "update housing_pums set htenure = 1 where tenure = 1 or tenure = 2",
                                "update housing_pums set htenure = 2 where tenure = 3 or tenure = 4",

                                # Original recodes
                                "update housing_pums set hbldgsz = 1 where bldgsz = 1",
                                "update housing_pums set hbldgsz = 2 where bldgsz = 2",
                                "update housing_pums set hbldgsz = 3 where bldgsz = 3",
                                "update housing_pums set hbldgsz = 4 where bldgsz = 4",
                                "update housing_pums set hbldgsz = 5 where bldgsz = 5",
                                "update housing_pums set hbldgsz = 6 where bldgsz = 6",
                                "update housing_pums set hbldgsz = 7 where bldgsz = 7",
                                "update housing_pums set hbldgsz = 8 where bldgsz = 8",
                                "update housing_pums set hbldgsz = 9 where bldgsz = 9",
                                "update housing_pums set hbldgsz = 10 where bldgsz = 10",

                                "update housing_pums set hyrmoved = 1 where yrmoved = 1", 
                                "update housing_pums set hyrmoved = 2 where yrmoved = 2", 
                                "update housing_pums set hyrmoved = 3 where yrmoved = 3", 
                                "update housing_pums set hyrmoved = 4 where yrmoved = 4", 
                                "update housing_pums set hyrmoved = 5 where yrmoved = 5", 
                                "update housing_pums set hyrmoved = 6 where yrmoved = 6", 


                                # Recodes for UrbanSim SF, Lane County, Hawaii
                                "update housing_pums set hbldgsz = 1 where bldgsz = 1",
                                "update housing_pums set hbldgsz = 2 where bldgsz = 2",
                                "update housing_pums set hbldgsz = 3 where bldgsz = 3",
                                "update housing_pums set hbldgsz = 4 where bldgsz = 4 or bldgsz = 5 or bldgsz = 6",
                                "update housing_pums set hbldgsz = 5 where bldgsz = 7",
                                "update housing_pums set hbldgsz = 6 where bldgsz = 8 or bldgsz = 9",
                                "update housing_pums set hbldgsz = 7 where bldgsz = 10",                                    

                                "update housing_pums set hyrmoved = 1 where yrmoved = 1 or yrmoved = 2", #1995-2000
                                "update housing_pums set hyrmoved = 2 where yrmoved = 3", 
                                "update housing_pums set hyrmoved = 3 where yrmoved = 4", 
                                "update housing_pums set hyrmoved = 4 where yrmoved = 5", 
                                "update housing_pums set hyrmoved = 5 where yrmoved = 6", 
                                    


                                "update housing_pums set hhtype = 1 where unittype = 0",
                                "update housing_pums set hhtype = 2 where unittype = 1 or unittype = 2",
                                "update housing_pums set hhldtype = 1 where hht = 1",
                                "update housing_pums set hhldtype = 2 where hht = 2",
                                "update housing_pums set hhldtype = 3 where hht = 3",
                                "update housing_pums set hhldtype = 4 where hht = 4 or hht = 5",
                                "update housing_pums set hhldtype = 5 where hht = 6 or hht = 7",
                                "update housing_pums set hhldtype = -99 where hht = 0",

                                # Original recodes
                                "update housing_pums set hhldinc = 1 where hinc <15000",
                                "update housing_pums set hhldinc = 2 where hinc >= 15000 and hinc < 25000",
                                "update housing_pums set hhldinc = 3 where hinc >= 25000 and hinc < 35000",
                                "update housing_pums set hhldinc = 4 where hinc >= 35000 and hinc < 45000",
                                "update housing_pums set hhldinc = 5 where hinc >= 45000 and hinc < 60000",
                                "update housing_pums set hhldinc = 6 where hinc >= 60000 and hinc < 100000",
                                "update housing_pums set hhldinc = 7 where hinc >= 100000 and hinc < 150000",
                                "update housing_pums set hhldinc = 8 where hinc >= 150000",
                                "update housing_pums set hhldinc = -99 where hht = 0",                          

                                "update housing_pums set hhldsize = persons where persons < 7",
                                "update housing_pums set hhldsize = 7 where persons >= 7",
                                "update housing_pums set hhldsize = -99 where hht = 0",                          

                                # Recodes for UrbanSim SF, Lane County, Hawaii
                                #"update housing_pums set hhldsize = persons where persons < 4",
                                #"update housing_pums set hhldsize = 4 where persons >= 4",
                                #"update housing_pums set hhldsize = -99 where hht = 0",                          

                                #"update housing_pums set hhldinc = 1 where hinc <25000",
                                #"update housing_pums set hhldinc = 2 where hinc >= 25000 and hinc < 45000",
                                #"update housing_pums set hhldinc = 3 where hinc >= 45000 and hinc < 100000",
                                #"update housing_pums set hhldinc = 4 where hinc >= 100000",
                                #"update housing_pums set hhldinc = -99 where hht = 0",                          

                                "update housing_pums set hhchildpresence = 1 where noc > 0",
                                "update housing_pums set hhchildpresence = 2 where noc = 0",
                                "update housing_pums set hhchildpresence = -99 where hht = 0",                          
                                "update housing_pums set groupquarter = unittype where unittype >0",
                                "update housing_pums set groupquarter = -99 where unittype =0",
                                
                                "update housing_pums set hhldfam = 1 where hhldtype <=3",
                                "update housing_pums set hhldfam = 2 where hhldtype > 3",

                                "delete from housing_pums where persons = 0",
                                "drop table hhld_sample",
                                "drop table gq_sample",
                                """create table hhld_sample select state, pumano, hhid, serialno, """\
                                        """hhtype, hhldtype, hhldinc, hhldsize, hhchildpresence, """\
                                        """hhldfam, htenure, hbldgsz, hvehicl, hgrent, hvalue, """\
                                        """hyrbuilt, hyrmoved from housing_pums where hhtype = 1""",
                                """create table gq_sample select state, pumano, hhid, serialno, """\
                                        """hhtype, groupquarter from housing_pums where hhtype = 2""",
                                "alter table hhld_sample add index(serialno)",
                                "alter table gq_sample add index(serialno)"]


DEFAULT_HOUSING_PUMSACS_QUERIES = ["alter table housing_pums add index(serialno)",
                                   "alter table housing_pums change hincp hinc bigint",
                                   "alter table housing_pums change np persons bigint",
                                   "alter table housing_pums change hupaoc noc bigint",
                                   "alter table housing_pums change type unittype bigint",
                                   "alter table housing_pums change st state bigint",
                                   "alter table housing_pums change puma pumano bigint",
                                   
                                   "alter table housing_pums add column hhtype bigint",
                                   "alter table housing_pums add column hhldtype bigint",
                                   "alter table housing_pums add column hhldinc bigint",
                                   "alter table housing_pums add column hhldtenure bigint",
                                   "alter table housing_pums add column hhldsize bigint",
                                   "alter table housing_pums add column childpresence bigint",
                                   "alter table housing_pums add column groupquarter bigint",
                                   "alter table housing_pums add column hhldfam bigint",
                                   
                                   "update housing_pums set hhtype = 1 where unittype = 1",
                                   "update housing_pums set hhtype = 2 where unittype = 2 or unittype = 3",
                                   "update housing_pums set hhldtype = 1 where hht = 1",
                                   "update housing_pums set hhldtype = 2 where hht = 2",
                                   "update housing_pums set hhldtype = 3 where hht = 3",
                                   "update housing_pums set hhldtype = 4 where hht = 4 or hht = 6",
                                   "update housing_pums set hhldtype = 5 where hht = 5 or hht = 7",
                                   "update housing_pums set hhldtype = -99 where hht = 0",
                                   "update housing_pums set hhldinc = 1 where hinc <15000",
                                   "update housing_pums set hhldinc = 2 where hinc >= 15000 and hinc < 25000",
                                   "update housing_pums set hhldinc = 3 where hinc >= 25000 and hinc < 35000",
                                   "update housing_pums set hhldinc = 4 where hinc >= 35000 and hinc < 45000",
                                   "update housing_pums set hhldinc = 5 where hinc >= 45000 and hinc < 60000",
                                   "update housing_pums set hhldinc = 6 where hinc >= 60000 and hinc < 100000",
                                   "update housing_pums set hhldinc = 7 where hinc >= 100000 and hinc < 150000",
                                   "update housing_pums set hhldinc = 8 where hinc >= 150000",
                                   "update housing_pums set hhldinc = -99 where hht = 0",                          
                                   #"update housing_pums set hhldtenure = 1 where tenure = 1 or tenure = 2",
                                   #"update housing_pums set hhldtenure = 2 where tenure = 3 or tenure = 4",
                                   #"update housing_pums set hhldtenure = -99 where tenure = 0",                          
                                   "update housing_pums set hhldsize = persons where persons < 7",
                                   "update housing_pums set hhldsize = 7 where persons >= 7",
                                   "update housing_pums set hhldsize = -99 where hht = 0",                          
                                   "update housing_pums set childpresence = 1 where noc =1 or noc = 2 or noc = 3",
                                   "update housing_pums set childpresence = 2 where noc = 4",
                                   "update housing_pums set childpresence = -99 where hht = 0",                          
                                   "update housing_pums set groupquarter = 1 where unittype >1",
                                   "update housing_pums set groupquarter = -99 where unittype =1",
                                   
                                   "update housing_pums set hhldfam = 1 where hhldtype <=3",
                                   "update housing_pums set hhldfam = 2 where hhldtype > 3",

                                   "delete from housing_pums where persons = 0",
                                   "drop table serialcorr",
                                   "create table serialcorr select state, pumano, serialno from housing_pums group by serialno",
                                   "alter table serialcorr add column hhid bigint primary key auto_increment not null",
                                   "alter table serialcorr add index(serialno)",
                                   
                                   
                                   "drop table hhld_sample",
                                   "drop table gq_sample",

                                   "alter table housing_pums add index(serialno)",

                                   "create table housing_pums1 select housing_pums.*, hhid from housing_pums left join serialcorr using(serialno)",
                                   "update housing_pums1 set serialno = hhid",

                                   "create table hhld_sample select state, pumano, hhid, serialno, hhldtype, hhldinc, hhldsize, childpresence, hhldfam from housing_pums1 where hhtype = 1",
                                   "create table gq_sample select state, pumano, hhid, serialno, groupquarter from housing_pums1 where hhtype = 2",


                                   "alter table hhld_sample add index(serialno)",
                                   "alter table gq_sample add index(serialno)",
                                   "drop table housing_pums1"]

DEFAULT_SF2000_QUERIES = ["alter table %s add column agep1 bigint",
                          "alter table %s add column agep2 bigint",
                          "alter table %s add column agep3 bigint",
                          "alter table %s add column agep4 bigint",
                          "alter table %s add column agep5 bigint",
                          "alter table %s add column agep6 bigint",
                          "alter table %s add column agep7 bigint",
                          "alter table %s add column agep8 bigint",
                          "alter table %s add column agep9 bigint",
                          "alter table %s add column agep10 bigint",
                          "alter table %s add column gender1 bigint",
                          "alter table %s add column gender2 bigint",
                          "alter table %s add column race1 bigint",
                          "alter table %s add column race2 bigint",
                          "alter table %s add column race3 bigint",
                          "alter table %s add column race4 bigint",
                          "alter table %s add column race5 bigint",
                          "alter table %s add column race6 bigint",
                          "alter table %s add column race7 bigint",
                          "alter table %s add column employment1 bigint",
                          "alter table %s add column employment2 bigint",
                          "alter table %s add column employment3 bigint",
                          "alter table %s add column employment4 bigint",
                          "alter table %s add column childpresence1 bigint",
                          "alter table %s add column childpresence2 bigint",
                          "alter table %s add column groupquarter1 bigint",
                          "alter table %s add column groupquarter2 bigint",
                          "alter table %s add column hhldinc1 bigint",
                          "alter table %s add column hhldinc2 bigint",
                          "alter table %s add column hhldinc3 bigint",
                          "alter table %s add column hhldinc4 bigint",
                          "alter table %s add column hhldinc5 bigint",
                          "alter table %s add column hhldinc6 bigint",
                          "alter table %s add column hhldinc7 bigint",
                          "alter table %s add column hhldinc8 bigint",
                          "alter table %s add column hhldsize1 bigint",
                          "alter table %s add column hhldsize2 bigint",
                          "alter table %s add column hhldsize3 bigint",
                          "alter table %s add column hhldsize4 bigint",
                          "alter table %s add column hhldsize5 bigint",
                          "alter table %s add column hhldsize6 bigint",
                          "alter table %s add column hhldsize7 bigint",
                          "alter table %s add column hhldtype1 bigint",
                          "alter table %s add column hhldtype2 bigint",
                          "alter table %s add column hhldtype3 bigint",
                          "alter table %s add column hhldtype4 bigint",
                          "alter table %s add column hhldtype5 bigint",
                          "alter table %s add column hhldrage1 bigint",
                          "alter table %s add column hhldrage2 bigint",
                          "alter table %s add column hhldfam1 bigint",
                          "alter table %s add column hhldfam2 bigint",



                          
                          # Original recodes
                          """update %s set agep1 = (P008003+P008004+P008005+P008006+P008007) """\
                              """+ (P008042+P008043+P008044+P008045+P008046)""",
                          """update %s set agep2 = (P008008+P008009+P008010+P008011+P008012+"""\
                              """P008013+P008014+P008015+P008016+P008017 ) + """\
                              """(P008047+P008048+P008049+P008050+P008051+P008052+P008053+"""\
                              """P008054+P008055+P008056)""",
                          """update %s set agep3 = (P008018+P008019+P008020+P008021+P008022"""\
                              """+P008023+P008024+P008025 ) + (P008057+P008058+P008059+P008060"""\
                              """+P008061+P008062+P008063+P008064)""",
                          "update %s set agep4 = (P008026+P008027) + (P008065+P008066)",
                          "update %s set agep5 = (P008028+P008029) + (P008067+P008068)",
                          "update %s set agep6 = (P008030+P008031) + (P008069+P008070)",
                          "update %s set agep7 = (P008032+P008033+P008034) + (P008071+P008072+P008073)",
                          "update %s set agep8 = (P008035+P008036+P008037) + (P008074+P008075+P008076)",
                          "update %s set agep9 = (P008038+P008039) + (P008077+P008078)",
                          "update %s set agep10 = (P008040) + (P008079)",

                          
                          # Recodes for Urbansim SF, Lane County, Hawaii
                          #"""update %s set agep1 = (P008003+P008004+P008005+P008006+P008007) """\
                          #   """+ (P008042+P008043+P008044+P008045+P008046) + """\
                          #   """(P008008+P008009+P008010+P008011+P008012+"""\
                          #   """P008013+P008014+P008015+P008016+P008017 ) + """\
                          #   """(P008047+P008048+P008049+P008050+P008051+P008052+P008053+"""\
                          #   """P008054+P008055+P008056)""",
                          #"""update %s set agep2 = (P008018+P008019+P008020+P008021+P008022"""\
                          #   """+P008023+P008024+P008025 ) + (P008057+P008058+P008059+P008060"""\
                          #   """+P008061+P008062+P008063+P008064) + """\
                          #   """(P008026+P008027) + (P008065+P008066)""",
                          #""update %s set agep3 = (P008028+P008029) + (P008067+P008068) + """\
                          #    """ (P008030+P008031) + (P008069+P008070)""",
                          #"""update %s set agep4 = (P008032+P008033+P008034) + (P008071+P008072+P008073) + """\
                          #    """ (P008035+P008036+P008037) + (P008074+P008075+P008076)""",
                          #"update %s set agep5 = (P008038+P008039) + (P008077+P008078) + (P008040) + (P008079)",


                          "update %s set gender1 = P008002", 
                          "update %s set gender2 = P008041", 

                          "update %s set race1 = P006002",
                          "update %s set race2 = P006003",
                          "update %s set race3 = P006004",
                          "update %s set race4 = P006005",
                          "update %s set race5 = P006006",
                          "update %s set race6 = P006007",
                          "update %s set race7 = P006008",

                          # Original recodes
                          #"update %s set employment1 = agep1+agep2+P008018+P008057",

                          # Recodes for UrbanSim SF, Lane County, Hawaii
                          "update %s set employment1 = agep1+P008018+P008057",
                          "update %s set employment2 = P043004+P043006+P043011+P043013",
                          "update %s set employment3 = P043007+P043014",
                          "update %s set employment4 = P043008+P043015",

                          "update %s set childpresence1 = P010008 + P010012 + P010015",
                          "update %s set childpresence2 = P010009 + P010013 + P010016 + P010017 + P010002",

                          "update %s set groupquarter1 = P009026",
                          "update %s set groupquarter2 = P009027",

                          # Original recodes
                          "update %s set hhldinc1 = P052002 + P052003",
                          "update %s set hhldinc2 = P052004 + P052005",
                          "update %s set hhldinc3 = P052006 + P052007",
                          "update %s set hhldinc4 = P052008 + P052009",
                          "update %s set hhldinc5 = P052010 + P052011",
                          "update %s set hhldinc6 = P052012 + P052013",
                          "update %s set hhldinc7 = P052014 + P052015",
                          "update %s set hhldinc8 = P052016 + P052017",

                          "update %s set hhldsize1 = P014010 ",
                          "update %s set hhldsize2 = P014003+P014011 ",
                          "update %s set hhldsize3 = P014004+P014012 ",
                          "update %s set hhldsize4 = P014005+P014013 ",
                          "update %s set hhldsize5 = P014006+P014014 ",
                          "update %s set hhldsize6 = P014007+P014015 ",
                          "update %s set hhldsize7 = P014008+P014016 ",

                          # Recodes for UrbanSim for SF, Lane County, Hawaii
                          #"update %s set hhldinc1 = P052002 + P052003 + P052004 + P052005",
                          #"update %s set hhldinc2 = P052006 + P052007 + P052008 + P052009",
                          #"update %s set hhldinc3 = P052010 + P052011 + P052012 + P052013",
                          #"update %s set hhldinc4 = P052014 + P052015 + P052016 + P052017",

                          #"update %s set hhldsize1 = P014010 ",
                          #"update %s set hhldsize2 = P014003+P014011 ",
                          #"update %s set hhldsize3 = P014004+P014012 ",
                          #"update %s set hhldsize4 = P014005+P014013 + P014006+P014014 + P014007+P014015 + P014008+P014016 ",

                          "update %s set hhldtype1 = P010007",
                          "update %s set hhldtype2 = P010011 ",
                          "update %s set hhldtype3 = P010014",
                          "update %s set hhldtype4 = P010002",
                          "update %s set hhldtype5 = P010017",

                          "update %s set hhldrage1 = P012002",
                          "update %s set hhldrage2 = P012017",

                          "update %s set hhldfam1 = hhldtype1 + hhldtype2 + hhldtype3",
                          "update %s set hhldfam2 = hhldtype4 + hhldtype5",
                          

                          "alter table %s add column htenure1 bigint",
                          "alter table %s add column htenure2 bigint",

                          "alter table %s add column hbldgsz1 bigint",
                          "alter table %s add column hbldgsz2 bigint",
                          "alter table %s add column hbldgsz3 bigint",
                          "alter table %s add column hbldgsz4 bigint",
                          "alter table %s add column hbldgsz5 bigint",
                          "alter table %s add column hbldgsz6 bigint",
                          "alter table %s add column hbldgsz7 bigint",
                          "alter table %s add column hbldgsz8 bigint",
                          "alter table %s add column hbldgsz9 bigint",
                          "alter table %s add column hbldgsz10 bigint",

                          "alter table %s add column phours1 bigint",
                          "alter table %s add column phours2 bigint",
                          "alter table %s add column phours3 bigint",
                          "alter table %s add column phours4 bigint",
                          "alter table %s add column phours5 bigint",

                          "alter table %s add column pclwkr1 bigint",
                          "alter table %s add column pclwkr2 bigint",
                          "alter table %s add column pclwkr3 bigint",
                          "alter table %s add column pclwkr4 bigint",
                          "alter table %s add column pclwkr5 bigint",
                          "alter table %s add column pclwkr6 bigint",
                          "alter table %s add column pclwkr7 bigint",
                          "alter table %s add column pclwkr8 bigint",
                          "alter table %s add column pclwkr9 bigint",
                          "alter table %s add column pclwkr10 bigint",
                          "alter table %s add column pclwkr11 bigint",
                          "alter table %s add column pclwkr12 bigint",

                          "alter table %s add column hyrmoved1 bigint",
                          "alter table %s add column hyrmoved2 bigint",
                          "alter table %s add column hyrmoved3 bigint",
                          "alter table %s add column hyrmoved4 bigint",
                          "alter table %s add column hyrmoved5 bigint",

                          
                          "alter table %s add column hhldrrace1 bigint",
                          "alter table %s add column hhldrrace2 bigint",
                          "alter table %s add column hhldrrace3 bigint",
                          "alter table %s add column hhldrrace4 bigint",
                          "alter table %s add column hhldrrace5 bigint",
                          "alter table %s add column hhldrrace6 bigint",
                          "alter table %s add column hhldrrace7 bigint",
                          # Household variables from P Series of Tables
                          "alter table %s add column hhldsize_check bigint",
                          "alter table %s add column hhldinc_check bigint",
                          "alter table %s add column hchild_check bigint",
                          # Household variables from H Series of Tables, 
                          # they correspond to occupied housing units
                          "alter table %s add column hhldrrace_check bigint",
                          "alter table %s add column hyrmoved_check bigint",
                          "alter table %s add column htenure_check bigint",
                          "alter table %s add column hbldgsz_check bigint",
                          # All person variables are from P series of tables,
                          "alter table %s add column phours_check bigint",
                          "alter table %s add column pclwkr_check bigint",
                          "alter table %s add column pgender_check bigint",
                          "alter table %s add column phousing_check bigint",
                          "alter table %s add column pemp_check bigint",
                          


                          "update %s set htenure1 = H007002",
                          "update %s set htenure2 = H007003",

                          "update %s set hhldrrace1 = H009002",
                          "update %s set hhldrrace2 = H009003",
                          "update %s set hhldrrace3 = H009004",
                          "update %s set hhldrrace4 = H009005",
                          "update %s set hhldrrace5 = H009006",
                          "update %s set hhldrrace6 = H009007",
                          "update %s set hhldrrace7 = H009008",
                          
                          # Original recodes
                          #"update %s set hyrmoved1 = H038003 + H038010",
                          #"update %s set hyrmoved2 = H038004 + H038011",
                          #"update %s set hyrmoved3 = H038005 + H038012",
                          #"update %s set hyrmoved4 = H038006 + H038013",
                          #"update %s set hyrmoved5 = H038007 + H038014",
                          #"update %s set hyrmoved6 = H038008 + H038015",

                          #"update %s set hbldgsz1 = H030010",
                          #"update %s set hbldgsz2 = H030002",
                          #"update %s set hbldgsz3 = H030003",
                          #"update %s set hbldgsz4 = H030004",
                          #"update %s set hbldgsz5 = H030005",
                          #"update %s set hbldgsz6 = H030006",
                          #"update %s set hbldgsz7 = H030007",
                          #"update %s set hbldgsz8 = H030008",
                          #"update %s set hbldgsz9 = H030009",
                          #"update %s set hbldgsz10 = H030011",

                          # Recodes for UrbanSim SF, Lane County, Hawaii
                          "update %s set hyrmoved1 = H038003 + H038010 + H038004 + H038011",
                          "update %s set hyrmoved2 = H038005 + H038012",
                          "update %s set hyrmoved3 = H038006 + H038013",
                          "update %s set hyrmoved4 = H038007 + H038014",
                          "update %s set hyrmoved5 = H038008 + H038015",

                          "update %s set hbldgsz1 = H030010",
                          "update %s set hbldgsz2 = H030002",
                          "update %s set hbldgsz3 = H030003",
                          "update %s set hbldgsz4 = H030004 + H030005 + H030006",
                          "update %s set hbldgsz5 = H030007",
                          "update %s set hbldgsz6 = H030008 + H030009",
                          "update %s set hbldgsz7 = H030011",
                          

                          "update %s set phours1 = P047025 + P047049", # did not work
                          "update %s set phours2 = P047018 + P047042", # 1 - 14 hours/week
                          "update %s set phours3 = P047011 + P047035", # 15 - 34 hours/week
                          "update %s set phours4 = P047004 + P047028", # 35 + hours/week

                          # Original recodes
                          #"update %s set phours5 = agep1+agep2+P008018+P008057""", # Not in universe 15 and younger
                          
                          # Recodes for UrbanSim for SF, Lane County, Hawaii
                          "update %s set phours5 = agep1+P008018+P008057""", # Not in universe 15 and younger

                          """update %s set pclwkr1 = P051005 + P051016 + P051026 + P051037 + """\
                              """P051048 + P051058""",
                          """update %s set pclwkr2 = P051039 + P051050 + P051060 + """\
                              """P051007 + P051018 + P051028""",
                          """update %s set pclwkr3 = P051040 + P051051 + P051061 + """\
                              """P051008 + P051019 + P051029""",
                          """update %s set pclwkr4 = P051041 + P051052 + P051062 + """\
                              """P051009 + P051020 + P051030""",
                          """update %s set pclwkr5 = P051042 + P051053 + P051063 + """\
                              """P051010 + P051021 + P051031""",
                          """update %s set pclwkr6 = P051043 + P051054 + P051064 + """\
                              """P051011 + P051022 + P051032""",
                          """update %s set pclwkr7 = P051038 + P051049 + P051059 + """\
                              """P051006 + P051017 + P051027""",
                          """update %s set pclwkr8 = P051044 + P051055 + P051065 + """\
                              """P051012 + P051023 + P051033""",
                          # Original Recodes
                          #"""update %s set pclwkr9 = agep1+agep2+P008018+P008057""", # 15 and younger

                          # Recodes for UrbanSim for SF, Lane County, Hawaii
                          """update %s set pclwkr9 = agep1+P008018+P008057""", # 15 and younger

                          """update %s set pclwkr10 = P043004 + P043011""", # In Armed Forces
                          """update %s set pclwkr11 = P043007 + P043014""", # Unemployed Civilian
                          """update %s set pclwkr12 = P043008 + P043015""", # Not in labor force

                          """update %s set hchild_check = childpresence1 + childpresence2""",
                          """update %s set hhldrrace_check = hhldrrace1 + hhldrrace2 + hhldrrace3 + """\
                              """hhldrrace4 + hhldrrace5 + hhldrrace6 + hhldrrace7""",

                          """update %s set hhldsize_check = hhldsize1 + hhldsize2 + hhldsize3 + """\
                              """hhldsize4 + hhldsize5 + hhldsize6 + hhldsize7""",

                          """update %s set hhldinc_check = hhldinc1 + hhldinc2 + hhldinc3 + """\
                              """hhldinc4 + hhldinc5 + hhldinc6 + hhldinc7 + hhldinc8""",

                          """update %s set phousing_check = hchild_check + groupquarter1 + groupquarter2""",

                          """update %s set hyrmoved_check = hyrmoved1 + hyrmoved2 + hyrmoved3 + """\
                              """hyrmoved4 + hyrmoved5""",
                          """update %s set htenure_check = htenure1 + htenure2""",
                          """update %s set hbldgsz_check = hbldgsz1 + hbldgsz2 + hbldgsz3 + hbldgsz4 + """\
                              """hbldgsz5 + hbldgsz6 + hbldgsz7 + hbldgsz8 + hbldgsz9 + hbldgsz10 """,

                          """update %s set phours_check = phours1 + phours2 + phours3 + phours4 + phours5""",
                          """update %s set pclwkr_check = pclwkr1 + pclwkr2 + pclwkr3 + pclwkr4 + """\
                              """pclwkr5 + pclwkr6 + pclwkr7 + pclwkr8 + pclwkr9 + pclwkr10 + pclwkr11 + pclwkr12""",
                          """update %s set pgender_check = gender1 + gender2""",
                          "update %s set pemp_check = employment1 + employment2 + employment3 + employment4",

                          "drop table hhld_marginals",
                          "drop table gq_marginals",
                          "drop table person_marginals",
                          #"""create table hhld_marginals select state, county, tract, bg, hhldinc1, hhldinc2, hhldinc3, hhldinc4, hhldinc5, hhldinc6, hhldinc7, hhldinc8,"""
                          #"""hhldsize1, hhldsize2, hhldsize3, hhldsize4, hhldsize5, hhldsize6, hhldsize7, hhldtype1, hhldtype2, hhldtype3, hhldtype4, hhldtype5,"""
                          #"""childpresence1, childpresence2, hhldrage1, hhldrage2, hhldfam1, hhldfam2 from %s""",
                          #"create table gq_marginals select state, county, tract, bg, groupquarter1, groupquarter2 from %s",
                          #"""create table person_marginals select state, county, tract, bg, agep1, agep2, agep3, agep4, agep5, agep6, agep7, agep8, agep9, agep10,"""
                          #"""gender1, gender2, race1, race2, race3, race4, race5, race6, race7, employment1, employment2, employment3, employment4 from"""
                          #""" %s"""]

                          # Original Recodes
                          #"""create table hhld_marginals select state, county, tract, bg, """\
                          #    """hhldinc1, hhldinc2, hhldinc3, hhldinc4, hhldinc5, hhldinc6, """\
                          #    """hhldinc7, hhldinc8, hhldsize1, hhldsize2, hhldsize3, hhldsize4, """\
                          #    """hhldsize5, hhldsize6, hhldsize7, hhldtype1, hhldtype2, """\
                          #    """hhldtype3, hhldtype4, hhldtype5, childpresence1, childpresence2, """\
                          #    """hhldrage1, hhldrage2, hhldfam1, hhldfam2, """\
                          #    """hyrmoved1, hyrmoved2, hyrmoved3, hyrmoved4, hyrmoved5, hyrmoved6, """\
                          #    """htenure1, htenure2, """\
                          #    """hbldgsz1, hbldgsz2, hbldgsz3, hbldgsz4, hbldgsz5, hbldgsz6, hbldgsz7, """\
                          #    """hbldgsz8, hbldgsz9, hbldgsz10 """\
                          #    """from %s""",

                          #"""create table gq_marginals select state, county, tract, bg, """\
                          #    """groupquarter1, groupquarter2 from %s""",

                          #"""create table person_marginals select state, county, tract, bg, """\
                          #    """agep1, agep2, agep3, agep4, agep5, agep6, agep7, agep8, agep9, """\
                          #    """agep10, gender1, gender2, race1, race2, race3, race4, """\
                          #    """race5, race6, race7, employment1, employment2, employment3, """\
                          #    """employment4, """\
                          #    """phours1, phours2, phours3, phours4, phours5, """\
                          #    """pclwkr1, pclwkr2, pclwkr3, pclwkr4, pclwkr5, pclwkr6, pclwkr7, """\
                          #    """pclwkr8, pclwkr9, pclwkr10, pclwkr11, pclwkr12 """
                          #    """from %s"""

                          # Recodes for UrbanSim for SF, Lane County, Hawaii
                          """create table hhld_marginals select state, county, tract, bg, """\
                              """hhldinc1, hhldinc2, hhldinc3, hhldinc4, """\
                              """ hhldinc5, hhldinc6, hhldinc7, hhldinc8,"""\
                              """hhldsize1, hhldsize2, hhldsize3, hhldsize4, """\
                              """hhldsize5, hhldsize6, hhldsize7, """\
                              """hhldtype1, hhldtype2, """\
                              """hhldtype3, hhldtype4, hhldtype5, childpresence1, childpresence2, """\
                              """hhldrage1, hhldrage2, hhldfam1, hhldfam2, """\
                              """htenure1, htenure2, """\
                              """hbldgsz1, hbldgsz2, hbldgsz3, hbldgsz4, hbldgsz5, hbldgsz6, hbldgsz7, """\
                              """hyrmoved1, hyrmoved2, hyrmoved3, hyrmoved4, hyrmoved5, """\
                              """hhldrrace1, hhldrrace2, hhldrrace3, hhldrrace4, hhldrrace5, """\
                              """hhldrrace6, hhldrrace7 """\
                              """from %s""",

                          """create table gq_marginals select state, county, tract, bg, """\
                              """groupquarter1, groupquarter2 from %s""",

                          """create table person_marginals select state, county, tract, bg, """\
                              """agep1, agep2, agep3, agep4, agep5, """\
                              """agep6, agep7, agep8, agep9, agep10, """\
                              """gender1, gender2, race1, race2, race3, race4, """\
                              """race5, race6, race7, employment1, employment2, employment3, """\
                              """employment4, """\
                              """phours1, phours2, phours3, phours4, phours5, """\
                              """pclwkr1, pclwkr2, pclwkr3, pclwkr4, pclwkr5, pclwkr6, pclwkr7, """\
                              """pclwkr8, pclwkr9, pclwkr10, pclwkr11, pclwkr12 """
                              """from %s"""]


DEFAULT_SFACS_QUERIES = ["alter table %s add column agep1 bigint",
                         "alter table %s add column agep2 bigint",
                         "alter table %s add column agep3 bigint",
                         "alter table %s add column agep4 bigint",
                         "alter table %s add column agep5 bigint",
                         "alter table %s add column agep6 bigint",
                         "alter table %s add column agep7 bigint",
                         "alter table %s add column agep8 bigint",
                         "alter table %s add column agep9 bigint",
                         "alter table %s add column agep10 bigint",
                         "alter table %s add column gender1 bigint",
                         "alter table %s add column gender2 bigint",
                         "alter table %s add column race1 bigint",
                         "alter table %s add column race2 bigint",
                         "alter table %s add column race3 bigint",
                         "alter table %s add column race4 bigint",
                         "alter table %s add column race5 bigint",
                         "alter table %s add column race6 bigint",
                         "alter table %s add column race7 bigint",
                         "alter table %s add column race11 bigint",
                         "alter table %s add column race12 bigint",
                         "alter table %s add column race13 bigint",
                         "alter table %s add column race14 bigint",
                         "alter table %s add column race15 bigint",
                         "alter table %s add column race16 bigint",
                         "alter table %s add column race17 bigint",
                         "alter table %s add column race21 bigint",
                         "alter table %s add column race22 bigint",
                         "alter table %s add column race23 bigint",
                         "alter table %s add column race24 bigint",
                         "alter table %s add column race25 bigint",
                         "alter table %s add column race26 bigint",
                         "alter table %s add column race27 bigint",
                         "alter table %s add column employment1 bigint",
                         "alter table %s add column employment2 bigint",
                         "alter table %s add column employment3 bigint",
                         "alter table %s add column employment4 bigint",
                         "alter table %s add column childpresence1 bigint",
                         "alter table %s add column childpresence2 bigint",
                         "alter table %s add column groupquarter1 bigint",
                         "alter table %s add column hhldinc1 bigint",
                         "alter table %s add column hhldinc2 bigint",
                         "alter table %s add column hhldinc3 bigint",
                         "alter table %s add column hhldinc4 bigint",
                         "alter table %s add column hhldinc5 bigint",
                         "alter table %s add column hhldinc6 bigint",
                         "alter table %s add column hhldinc7 bigint",
                         "alter table %s add column hhldinc8 bigint",
                         "alter table %s add column hhldsize1 bigint",
                         "alter table %s add column hhldsize2 bigint",
                         "alter table %s add column hhldsize3 bigint",
                         "alter table %s add column hhldsize4 bigint",
                         "alter table %s add column hhldsize5 bigint",
                         "alter table %s add column hhldsize6 bigint",
                         "alter table %s add column hhldsize7 bigint",
                         "alter table %s add column hhldtype1 bigint",
                         "alter table %s add column hhldtype2 bigint",
                         "alter table %s add column hhldtype3 bigint",
                         "alter table %s add column hhldtype4 bigint",
                         "alter table %s add column hhldtype5 bigint",
                         "alter table %s add column hhldrage1 bigint",
                         "alter table %s add column hhldrage2 bigint",
                         "alter table %s add column hhldfam1 bigint",
                         "alter table %s add column hhldfam2 bigint",

                         "alter table %s add column check_gender bigint",
                         "alter table %s add column check_age bigint",
                         "alter table %s add column check_race bigint",
                         "alter table %s add column check_race1 bigint",
                         "alter table %s add column check_race2 bigint",
                         "alter table %s add column check_employment bigint",
                         
                         "alter table %s add column check_type bigint",
                         "alter table %s add column check_size bigint",
                         "alter table %s add column check_fam bigint",
                         "alter table %s add column check_hhldrage bigint",
                         "alter table %s add column check_inc bigint",
                         "alter table %s add column check_child bigint",
                         


                         "update %s set agep1 = (B01001000003)+(B01001000027)",
                         "update %s set agep2 = (B01001000004+B01001000005) + (B01001000028+B01001000029)",
                         "update %s set agep3 = (B01001000006+B01001000007+B01001000008+B01001000009+B01001000010) + (B01001000030+B01001000031+B01001000032+B01001000033+B01001000034)",
                         "update %s set agep4 = (B01001000011+B01001000012) + (B01001000035+B01001000036)",
                         "update %s set agep5 = (B01001000013+B01001000014) + (B01001000037+B01001000038)",
                         "update %s set agep6 = (B01001000015+B01001000016) + (B01001000039+B01001000040)",
                         "update %s set agep7 = (B01001000017+B01001000018+B01001000019) + (B01001000041+B01001000042+B01001000043)",
                         "update %s set agep8 = (B01001000020+B01001000021+B01001000022) + (B01001000044+B01001000045+B01001000046)",
                         "update %s set agep9 = (B01001000023+B01001000024) + (B01001000047+B01001000048)",
                         "update %s set agep10 = (B01001000025) + (B01001000049)",
                         "update %s set gender1 = B01001000002",
                         "update %s set gender2 = B01001000026",  
                         "update %s set race1 = B02001000002",
                         "update %s set race2 = B02001000003",
                         "update %s set race3 = B02001000004",
                         "update %s set race4 = B02001000005",
                         "update %s set race5 = B02001000006",
                         "update %s set race6 = B02001000007",
                         "update %s set race7 = B02001000009+B02001000010",

                         "update %s set race11 = C01001A00001",
                         "update %s set race12 = C01001B00001",
                         "update %s set race13 = C01001C00001",
                         "update %s set race14 = C01001D00001",
                         "update %s set race15 = C01001E00001",
                         "update %s set race16 = C01001F00001",
                         "update %s set race17 = C01001G00001",

                         "update %s set race21 = B01001A00001",
                         "update %s set race22 = B01001B00001",
                         "update %s set race23 = B01001C00001",
                         "update %s set race24 = B01001D00001",
                         "update %s set race25 = B01001E00001",
                         "update %s set race26 = B01001F00001",
                         "update %s set race27 = B01001G00001",

                         """update %s set employment2 = (B23001000005 + B23001000007) + (B23001000012 + B23001000014) + """
                         """(B23001000019 + B23001000021) + (B23001000026 + B23001000028) + (B23001000033 + B23001000035) + """
                         """(B23001000040 + B23001000042) + (B23001000047 + B23001000049) + (B23001000054 + B23001000056) + """
                         """(B23001000061 + B23001000063) + (B23001000068 + B23001000070) + (B23001000075 + B23001000080 + B23001000085) + """
                         """(B23001000091 + B23001000093) + (B23001000098 + B23001000100) + """
                         """(B23001000105 + B23001000107) + (B23001000112 + B23001000114) + (B23001000119 + B23001000121) + """
                         """(B23001000126 + B23001000128) + (B23001000133 + B23001000135) + (B23001000140 + B23001000142) + """
                         """(B23001000147 + B23001000149) + (B23001000154 + B23001000156) + (B23001000161 + B23001000166 + B23001000171)""",

                         """update %s set employment3 = (B23001000008 + B23001000015 + B23001000022 + """
                         """B23001000029 + B23001000036 + B23001000043 + B23001000050 + B23001000057 + B23001000064 +"""
                         """B23001000071 + B23001000076 + B23001000081 + B23001000086 + B23001000094 + B23001000101 +"""
                         """B23001000108 + B23001000115 + B23001000122 + B23001000129 + B23001000136 + B23001000143 +"""
                         """B23001000150 + B23001000157 + B23001000162 + B23001000167 + B23001000172) """,

                         """update %s set employment4 = (B23001000009 + B23001000016 + B23001000023 + """
                         """B23001000030 + B23001000037 + B23001000044 + B23001000051 + B23001000058 + B23001000065 +"""
                         """B23001000072 + B23001000077 + B23001000082 + B23001000087 + B23001000095 + B23001000102 +"""
                         """B23001000109 + B23001000116 + B23001000123 + B23001000130 + B23001000137 + B23001000144 +"""
                         """B23001000151 + B23001000158 + B23001000163 + B23001000168 + B23001000173) """,

                         "update %s set employment1 = gender1 + gender2 - employment2 - employment3 - employment4",

                         "update %s set groupquarter1 = B26001000001",
                         "update %s set hhldinc1 = B19001000002 + B19001000003",
                         "update %s set hhldinc2 = B19001000004 + B19001000005",
                         "update %s set hhldinc3 = B19001000006 + B19001000007",
                         "update %s set hhldinc4 = B19001000008 + B19001000009",
                         "update %s set hhldinc5 = B19001000010 + B19001000011",
                         "update %s set hhldinc6 = B19001000012 + B19001000013",
                         "update %s set hhldinc7 = B19001000014 + B19001000015",
                         "update %s set hhldinc8 = B19001000016 + B19001000017",
                         "update %s set hhldsize1 = B25009000003+B25009000011",
                         "update %s set hhldsize2 = B25009000004+B25009000012",
                         "update %s set hhldsize3 = B25009000005+B25009000013",
                         "update %s set hhldsize4 = B25009000006+B25009000014",
                         "update %s set hhldsize5 = B25009000007+B25009000015",
                         "update %s set hhldsize6 = B25009000008+B25009000016",
                         "update %s set hhldsize7 = B25009000009+B25009000017",
                         "update %s set hhldtype1 = B11001000003",
                         "update %s set hhldtype2 = B11001000005",
                         "update %s set hhldtype3 = B11001000006",
                         "update %s set hhldtype4 = B11001000008",
                         "update %s set hhldtype5 = B11001000009",
                         """update %s set hhldrage1 = (B25007000003+B25007000004+B25007000005+B25007000006+B25007000007+B25007000008)+"""
                         """(B25007000013+B25007000014+B25007000015+B25007000016+B25007000017+B25007000018)""", 
                         "update %s set hhldrage2 = (B25007000009+ B25007000010+B25007000011)+(B25007000019+ B25007000020+B25007000021)",
                         "update %s set hhldfam1 = hhldtype1 + hhldtype2 + hhldtype3",
                         "update %s set hhldfam2 = hhldtype4 + hhldtype5",
                         "update %s set childpresence1 = C23007000002",
                         "update %s set childpresence2 = C23007000017 + hhldtype4 + hhldtype5",

                         "update %s set check_gender = gender1 + gender2",
                         "update %s set check_age = agep1+agep2+agep3+agep4+agep5+agep6+agep7+agep8+agep9+agep10",
                         "update %s set check_race = race1+race2+race3+race4+race5+race6+race7",
                         "update %s set check_race1 = race11+race12+race13+race14+race15+race16+race17",
                         "update %s set check_race2 = race21+race22+race23+race24+race25+race26+race27",
                         "update %s set check_employment = employment1 + employment2 + employment3 + employment4",

                         "update %s set check_type = hhldtype1+hhldtype2+hhldtype3+hhldtype4+hhldtype5",
                         "update %s set check_size = hhldsize1+hhldsize2+hhldsize3+hhldsize4+hhldsize5+hhldsize6+hhldsize7",
                         "update %s set check_hhldrage = hhldrage1+hhldrage2",
                         "update %s set check_inc = hhldinc1+hhldinc2+hhldinc3+hhldinc4+hhldinc5+hhldinc6+hhldinc7+hhldinc8",
                         "update %s set check_fam = hhldfam1+hhldfam2",
                         "update %s set check_child = childpresence1+childpresence2",


                  

                         "drop table hhld_marginals",
                         "drop table gq_marginals",
                         "drop table person_marginals",
                         """create table hhld_marginals select state, county, tract, bg, hhldinc1, hhldinc2, hhldinc3, hhldinc4, hhldinc5, hhldinc6, hhldinc7, hhldinc8,"""
                         """hhldsize1, hhldsize2, hhldsize3, hhldsize4, hhldsize5, hhldsize6, hhldsize7, hhldtype1, hhldtype2, hhldtype3, hhldtype4, hhldtype5,"""
                         """childpresence1, childpresence2, hhldrage1, hhldrage2, hhldfam1, hhldfam2 from %s""",
                         "create table gq_marginals select state, county, tract, bg, groupquarter1 from %s",
                         """create table person_marginals select state, county, tract, bg, agep1, agep2, agep3, agep4, agep5, agep6, agep7, agep8, agep9, agep10,"""
                         """gender1, gender2, race1, race2, race3, race4, race5, race6, race7 from %s"""]


                   

                   
 



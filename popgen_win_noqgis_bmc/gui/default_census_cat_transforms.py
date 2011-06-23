# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand 
# Copyright (C) 2009, Arizona State University
# See PopGen/License

DEFAULT_PERSON_PUMS2000_QUERIES = ["alter table person_pums add column person_tot_bmc bigint",
                                "alter table person_pums add column age_bmc bigint",
                                "alter table person_pums add column sex_bmc bigint",                                    
                                "alter table person_pums add column esr_bmc bigint",
                                "alter table person_pums add column occcen5_bmc bigint",                                    

                                "update person_pums set person_tot_bmc = 1",
                                   
                                "update person_pums set age_bmc = 1 where age < 5",
                                "update person_pums set age_bmc = 2 where age >= 5 and age < 15",
                                "update person_pums set age_bmc = 3 where age >= 15 and age < 25",
                                "update person_pums set age_bmc = 4 where age >= 25 and age < 35",
                                "update person_pums set age_bmc = 5 where age >= 35 and age < 45",
                                "update person_pums set age_bmc = 6 where age >= 45 and age < 55",
                                "update person_pums set age_bmc = 7 where age >= 55 and age < 65",
                                "update person_pums set age_bmc = 8 where age >= 65 and age < 75",
                                "update person_pums set age_bmc = 9 where age >= 75 and age < 85",
                                "update person_pums set age_bmc = 10 where age >= 85",

                                "update person_pums set sex_bmc = sex",

                                "update person_pums set esr_bmc = 1 where esr = 0",
                                "update person_pums set esr_bmc = 2 where esr = 1 or esr = 2 or esr = 4 or esr = 5",
                                "update person_pums set esr_bmc = 3 where esr = 3",
                                "update person_pums set esr_bmc = 4 where esr = 6",

                                "update person_pums set occcen5_bmc = 1 where occcen5 >= 1 and occcen5 <= 99",
                                "update person_pums set occcen5_bmc = 2 where occcen5 >= 100 and occcen5 <= 359", 
                                "update person_pums set occcen5_bmc = 3 where occcen5 >= 360 and occcen5 <= 469", 
                                "update person_pums set occcen5_bmc = 4 where occcen5 >= 470 and occcen5 <= 599", 
                                "update person_pums set occcen5_bmc = 5 where occcen5 >= 600 and occcen5 <= 619", 
                                "update person_pums set occcen5_bmc = 6 where occcen5 >= 620 and occcen5 <= 769", 
                                "update person_pums set occcen5_bmc = 7 where occcen5 >= 770 and occcen5 <= 979", 
                                "update person_pums set occcen5_bmc = 8 where occcen5 >= 980 and occcen5 <= 983",
                                "update person_pums set occcen5_bmc = 8 where occcen5 = 992",
                                "update person_pums set occcen5_bmc = 8 where occcen5 = 0",    

                                "drop table person_sample",

                                """create table person_sample select state, pumano, hhid, serialno, """\
                                        """pnum, person_tot_bmc, age_bmc, sex_bmc, esr_bmc, occcen5_bmc, """\
                                        """relate, earns, trvmns, age, race1, esr, sex, occcen5, clwkr, """\
                                        """indnaics, enroll, educ """
                                        """from person_pums""",
                                "alter table person_sample add index(serialno, pnum)",
                                   
                                "alter table hhld_sample drop column hhldrage_bmc",
                                "alter table hhld_sample drop column hhldrrace_bmc",
                                "alter table hhld_sample drop column hhldrage_raw",
                                "alter table hhld_sample drop column hhldrrace_raw",
                                "alter table hhld_sample drop column esr_sum_bmc",
                                "alter table hhld_sample drop column esr_sum_r_bmc",
                                   
                                "drop table hhld_sample_temp",
                                "alter table hhld_sample rename to hhld_sample_temp",

                                "drop table hhld_sample",
                                "drop table hhld_sample1",
                                "drop table hhld_esr_2_sum",


                                """create table hhld_esr_2_sum select serialno, count(*) as esr_sum_bmc from person_sample where esr_bmc = 2 """\
                                        """group by serialno""",
                                "alter table hhld_esr_2_sum add index(serialno)",



                                """create table hhld_sample1 select hhld_sample_temp.*, """\
                                        """age_bmc as hhldrage_bmc, age as hhldrage_raw, """\
					"""race1 as hhldrrace_raw from hhld_sample_temp left """\
                                        """join person_sample using(serialno) where relate = 1""",

                                """create table hhld_sample select hhld_sample1.*, hhld_esr_2_sum.esr_sum_bmc, """\
                                    """hhld_esr_2_sum.esr_sum_bmc as esr_sum_r_bmc from hhld_sample1 left join """\
                                   """hhld_esr_2_sum using(serialno)""", 

                                "alter table hhld_sample add index(serialno)",

                                "update hhld_sample set esr_sum_bmc = 0 where esr_sum_bmc IS NULL",
                                "update hhld_sample set esr_sum_r_bmc = esr_sum_r_bmc + 1 where esr_sum_r_bmc >= 1 ",
                                "update hhld_sample set esr_sum_r_bmc = 1 where esr_sum_r_bmc IS NULL",
                                "update hhld_sample set esr_sum_r_bmc = 4 where esr_sum_r_bmc >= 4 ",


                                "update hhld_sample set hhldrage_bmc = 1 where hhldrage_bmc <= 4 ",
                                "update hhld_sample set hhldrage_bmc = 2 where hhldrage_bmc = 5 or hhldrage_bmc = 6",
                                "update hhld_sample set hhldrage_bmc = 3 where hhldrage_bmc = 7 ",
                                "update hhld_sample set hhldrage_bmc = 4 where hhldrage_bmc > 7",
                                "drop table hhld_sample1",
                                "drop table hhld_esr_2_sum",
                                "drop table hhld_sample_temp"]

DEFAULT_PERSON_PUMSACS_QUERIES = ["alter table person_pums add column person_tot_bmc bigint",
                                  "alter table person_pums add column agep_bmc bigint",
                                  "alter table person_pums add column sex_bmc bigint",                                    
                                  "alter table person_pums add column esr_bmc bigint",

                                  "alter table person_pums change st state bigint",
                                  "alter table person_pums change puma pumano bigint",
                                  "alter table person_pums change sporder pnum bigint",


                                  "update person_pums set agep_bmc = 1 where agep < 5",
                                  "update person_pums set agep_bmc = 2 where agep >= 5 and agep < 15",
                                  "update person_pums set agep_bmc = 3 where agep >= 15 and agep < 25",
                                  "update person_pums set agep_bmc = 4 where agep >= 25 and agep < 35",
                                  "update person_pums set agep_bmc = 5 where agep >= 35 and agep < 45",
                                  "update person_pums set agep_bmc = 6 where agep >= 45 and agep < 55",
                                  "update person_pums set agep_bmc = 7 where agep >= 55 and agep < 65",
                                  "update person_pums set agep_bmc = 8 where agep >= 65 and agep < 75",
                                  "update person_pums set agep_bmc = 9 where agep >= 75 and agep < 85",
                                  "update person_pums set agep_bmc = 10 where agep >= 85",

                                  "update person_pums set sex_bmc = sex",

                                  "update person_pums set esr_bmc = 1 where esr = 0",
                                  "update person_pums set esr_bmc = 2 where esr = 1 or esr = 2 or esr = 4 or esr = 5",
                                  "update person_pums set esr_bmc = 3 where esr = 3",
                                  "update person_pums set esr_bmc = 4 where esr = 6",


                                  "alter table person_pums add index(serialno)",

                                   "create table person_pums1 select person_pums.*, hhid from person_pums left join serialcorr using(serialno)",
                                  "update person_pums1 set serialno = hhid",

                                  "drop table person_sample",



                                  """create table person_sample select state, pumano, hhid, serialno, pnum, """\
                                      """person_tot_bmc, agep_bmc, sex_bmc, esr_bmc, rel, pernp, jwtr, """\
                                      """agep, rac1p, esr, sex, occp, cow, indp, sch, schl from person_pums1""",
                                  "alter table person_sample add index(serialno, pnum)",
                                  "drop table person_pums1",

                                "alter table hhld_sample drop column hhldrage_bmc",
                                "alter table hhld_sample drop column hhldrrace_bmc",
                                "alter table hhld_sample drop column hhldrage_raw",
                                "alter table hhld_sample drop column hhldrrace_raw",
                                "alter table hhld_sample drop column esr_sum_bmc",
                                "alter table hhld_sample drop column esr_sum_r_bmc",
                                   
                                "drop table hhld_sample_temp",
                                "alter table hhld_sample rename to hhld_sample_temp",

                                "drop table hhld_sample",
                                "drop table hhld_sample1",
                                "drop table hhld_esr_2_sum",
                                  
                                """create table hhld_esr_2_sum select serialno, count(*) as esr_sum_bmc from person_sample where esr_bmc = 2 """\
                                        """group by serialno""",
                                "alter table hhld_esr_2_sum add index(serialno)",


                                  
                                  """create table hhld_sample1 select hhld_sample_temp.*, agep_bmc as hhldrage_bmc, agep as hhldrage_raw, """\
                                      """rac1p as hhldrrace_raw from hhld_sample_temp left join person_sample using(serialno) where rel = 0""",

                                """create table hhld_sample select hhld_sample1.*, hhld_esr_2_sum.esr_sum_bmc, """\
                                    """hhld_esr_2_sum.esr_sum_bmc as esr_sum_r_bmc from hhld_sample1 left join """\
                                   """hhld_esr_2_sum using(serialno)""", 

                                  "alter table hhld_sample add index(serialno)",

                                "update hhld_sample set esr_sum_bmc = 0 where esr_sum_bmc IS NULL",
                                "update hhld_sample set esr_sum_r_bmc = esr_sum_r_bmc + 1 where esr_sum_r_bmc >= 1 ",
                                "update hhld_sample set esr_sum_r_bmc = 1 where esr_sum_r_bmc IS NULL",
                                "update hhld_sample set esr_sum_r_bmc = 4 where esr_sum_r_bmc >= 4 ",

                                "update hhld_sample set hhldrage_bmc = 1 where hhldrage_bmc <= 4 ",
                                "update hhld_sample set hhldrage_bmc = 2 where hhldrage_bmc = 5 or hhldrage_bmc = 6",
                                "update hhld_sample set hhldrage_bmc = 3 where hhldrage_bmc = 7 ",
                                "update hhld_sample set hhldrage_bmc = 4 where hhldrage_bmc > 7",
                                "drop table hhld_sample1",
                                "drop table hhld_esr_2_sum",
                                "drop table hhld_sample_temp",
                                "drop table hhld_sample_temp"                                  
                                  ]


DEFAULT_HOUSING_PUMS2000_QUERIES = ["alter table housing_pums add index(serialno)",

                                    "alter table housing_pums add column persons_bmc bigint",
                                    "alter table housing_pums add column hinc_bmc bigint",                                    
                                    "alter table housing_pums add column wif_bmc bigint",                                    
                                    "alter table housing_pums add column bldgsz_bmc bigint",
                                    "alter table housing_pums add column gq bigint",
                                    
                                    "update housing_pums set persons_bmc = persons where persons < 5",
                                    "update housing_pums set persons_bmc = 5 where persons >= 5",
                                    "update housing_pums set persons_bmc = -99 where hht = 0",                          
                                    
                                    "update housing_pums set hinc_bmc = 1 where hinc <11800",
                                    "update housing_pums set hinc_bmc = 2 where hinc >= 11800 and hinc < 26000",
                                    "update housing_pums set hinc_bmc = 3 where hinc >= 26000 and hinc < 44200",
                                    "update housing_pums set hinc_bmc = 4 where hinc >= 44200",
                                    "update housing_pums set hinc_bmc = -99 where hht = 0",                          

                                    "update housing_pums set wif_bmc = 1 where wif = 0",
                                    "update housing_pums set wif_bmc = 2 where wif = 1",
                                    "update housing_pums set wif_bmc = 3 where wif = 2",
                                    "update housing_pums set wif_bmc = 4 where wif >= 3",

                                    "update housing_pums set bldgsz_bmc = 1 where bldgsz = 2 or bldgsz = 3 ",
                                    "update housing_pums set bldgsz_bmc = 2 where bldgsz >= 4 and bldgsz <= 9",
                                    "update housing_pums set bldgsz_bmc = 3 where bldgsz = 10 or bldgsz = 1",

                                    "update housing_pums set gq = unittype where unittype >0",
                                    "update housing_pums set gq = -99 where unittype =0",
                                
                                    "delete from housing_pums where persons = 0",
                                    "drop table hhld_sample",
                                    "drop table gq_sample",
                                    """create table hhld_sample select state, pumano, hhid, serialno, """\
                                        """persons_bmc, hinc_bmc, wif_bmc, bldgsz_bmc, tenure, grent, """\
                                        """value, yrbuilt, persons, hinc, wif, hht, unittype, """\
                                        """vehicl, noc, bldgsz, yrmoved """\
					"""from housing_pums where unittype = 0""",
                                    """create table gq_sample select state, pumano, hhid, serialno, """\
                                        """gq from housing_pums where unittype = 1 or unittype = 2""",
                                    "alter table hhld_sample add index(serialno)",
                                    "alter table gq_sample add index(serialno)"]


DEFAULT_HOUSING_PUMSACS_QUERIES = ["alter table housing_pums add index(serialno)",
                                   "alter table housing_pums change st state bigint",
                                   "alter table housing_pums change puma pumano bigint",

                                   "alter table housing_pums add column np_bmc bigint",
                                   "alter table housing_pums add column hincp_bmc bigint",                                    
                                   "alter table housing_pums add column wif_bmc bigint",                                    
                                   "alter table housing_pums add column bld_bmc bigint",
                                   "alter table housing_pums add column gq bigint",

                                   "update housing_pums set np_bmc = np where np < 5",
                                   "update housing_pums set np_bmc = 5 where np >= 5",
                                   "update housing_pums set np_bmc = -99 where hht = 0",                          

                                   "update housing_pums set hincp_bmc = 1 where hincp <11800",
                                   "update housing_pums set hincp_bmc = 2 where hincp >= 11800 and hincp < 26000",
                                   "update housing_pums set hincp_bmc = 3 where hincp >= 26000 and hincp < 44200",
                                   "update housing_pums set hincp_bmc = 4 where hincp >= 44200",
                                   "update housing_pums set hincp_bmc = -99 where hht = 0",                          

                                   "update housing_pums set wif_bmc = 1 where wif = 0",
                                   "update housing_pums set wif_bmc = 2 where wif = 1",
                                   "update housing_pums set wif_bmc = 3 where wif = 2",
                                   "update housing_pums set wif_bmc = 4 where wif = 3",

                                   "update housing_pums set bld_bmc = 1 where bld = 2 or bld = 3 ",
                                   "update housing_pums set bld_bmc = 2 where bld >= 4 and bld <= 9",
                                   "update housing_pums set bld_bmc = 3 where bld = 10 or bld = 1",

                                   "update housing_pums set gq = 1 where type >1",

                                   "delete from housing_pums where np = 0",
                                   "drop table serialcorr",
                                   "create table serialcorr select state, pumano, serialno from housing_pums group by serialno",
                                   "alter table serialcorr add column hhid bigint primary key auto_increment not null",
                                   "alter table serialcorr add index(serialno)",
                                   
                                   
                                   "drop table hhld_sample",
                                   "drop table gq_sample",

                                   "alter table housing_pums add index(serialno)",

                                   "create table housing_pums1 select housing_pums.*, hhid from housing_pums left join serialcorr using(serialno)",
                                   "update housing_pums1 set serialno = hhid",

                                   """create table hhld_sample select state, pumano, hhid, """\
                                       """serialno, np_bmc, hincp_bmc, wif_bmc, bld_bmc, ten, grntp, val, ybl, np, """\
                                       """ hincp, wif, hht, type, veh, noc, bld, fmvyp from housing_pums1 where type = 1""",
                                   "create table gq_sample select state, pumano, hhid, serialno, gq from housing_pums1 where type = 2 or type = 3",

                                   "alter table hhld_sample add index(serialno)",
                                   "alter table gq_sample add index(serialno)",
                                   "drop table housing_pums1"]

DEFAULT_SF2000_QUERIES = ["alter table %s add column hhperson1 bigint",
                          "alter table %s add column hhperson2 bigint",
                          "alter table %s add column hhperson3 bigint",
                          "alter table %s add column hhperson4 bigint",
                          "alter table %s add column hhperson5 bigint",
                          "alter table %s add column wif0 bigint",
                          "alter table %s add column wif1 bigint",
                          "alter table %s add column wif2 bigint",
                          "alter table %s add column wif3 bigint",
                          "alter table %s add column hhldrage1 bigint",
                          "alter table %s add column hhldrage2 bigint",
                          "alter table %s add column hhldrage3 bigint",
                          "alter table %s add column hhldrage4 bigint",
                          "alter table %s add column bldgsz1 bigint",
                          "alter table %s add column bldgsz2 bigint",
                          "alter table %s add column bldgsz3 bigint",

                          "alter table %s add column persontotal bigint",
                          "alter table %s add column employment1 bigint",
                          "alter table %s add column employment2 bigint",
                          "alter table %s add column employment3 bigint",
                          "alter table %s add column employment4 bigint",
                          "alter table %s add column age1 bigint",
                          "alter table %s add column age2 bigint",
                          "alter table %s add column age3 bigint",
                          "alter table %s add column age4 bigint",
                          "alter table %s add column age5 bigint",
                          "alter table %s add column age6 bigint",
                          "alter table %s add column age7 bigint",
                          "alter table %s add column age8 bigint",
                          "alter table %s add column age9 bigint",
                          "alter table %s add column age10 bigint",
                          "alter table %s add column occcen1 bigint",
                          "alter table %s add column occcen2 bigint",
                          "alter table %s add column occcen3 bigint",
                          "alter table %s add column occcen4 bigint",
                          "alter table %s add column occcen5 bigint",
                          "alter table %s add column occcen6 bigint",
                          "alter table %s add column occcen7 bigint",
                          "alter table %s add column occcen8 bigint",
                          "alter table %s add column sex1 bigint",
                          "alter table %s add column sex2 bigint",

                          "alter table %s add column igq bigint",
                          "alter table %s add column nigq bigint",                          

                          "update %s set hhperson1 = P014010 ",
                          "update %s set hhperson2 = P014003+P014011 ",
                          "update %s set hhperson3 = P014004+P014012 ",
                          "update %s set hhperson4 = P014005+P014013 ",
                          "update %s set hhperson5 = P014006+P014014  + P014007+P014015 + P014008+P014016 ",
                          "update %s set wif0 = P010017 + P010002",
                          "update %s set wif1 = P048003 + P048013 + P048018",
                          "update %s set wif2 = P048004 + P048014 + P048019 ",
                          "update %s set wif3 = P048005 + P048015 + P048020 + P048008 + P048016 + P048021 ",
                          "update %s set hhldrage1 = P013003 + P013004 + P013012 + P013013",
                          "update %s set hhldrage2 = P013005 + P013006 + P013014 + P013015",
                          "update %s set hhldrage3 = P013007 + P013016 ",
                          "update %s set hhldrage4 = P013008 + P013009 + P013010 + P013017 + P013018 + P013019",
                          "update %s set bldgsz1 = H030002 + H030003",
                          "update %s set bldgsz2 = H030004 + H030005 + H030006 + H030007 + H030008 + H030009",
                          "update %s set bldgsz3 = H030010 + H030011",

                          
                          """update %s set age1 = (P008003+P008004+P008005+P008006+P008007) """\
                              """+ (P008042+P008043+P008044+P008045+P008046)""",
                          """update %s set age2 = (P008008+P008009+P008010+P008011+P008012+"""\
                              """P008013+P008014+P008015+P008016+P008017 ) + """\
                              """(P008047+P008048+P008049+P008050+P008051+P008052+P008053+"""\
                              """P008054+P008055+P008056)""",
                          """update %s set age3 = (P008018+P008019+P008020+P008021+P008022"""\
                              """+P008023+P008024+P008025 ) + (P008057+P008058+P008059+P008060"""\
                              """+P008061+P008062+P008063+P008064)""",
                          "update %s set age4 = (P008026+P008027) + (P008065+P008066)",
                          "update %s set age5 = (P008028+P008029) + (P008067+P008068)",
                          "update %s set age6 = (P008030+P008031) + (P008069+P008070)",
                          "update %s set age7 = (P008032+P008033+P008034) + (P008071+P008072+P008073)",
                          "update %s set age8 = (P008035+P008036+P008037) + (P008074+P008075+P008076)",
                          "update %s set age9 = (P008038+P008039) + (P008077+P008078)",
                          "update %s set age10 = (P008040) + (P008079)",
                          "update %s set employment1 = age1+age2+P008018+P008057",
                          "update %s set employment2 = P043004+P043006+P043011+P043013",
                          "update %s set employment3 = P043007+P043014",
                          "update %s set employment4 = P043008+P043015",                          
			  "update %s set occcen1 = P050004 + P050051",
			  "update %s set occcen2 = P050010 + P050057",
			  "update %s set occcen3 = P050023 + P050070",
			  "update %s set occcen4 = P050031 + P050078",
			  "update %s set occcen5 = P050034 + P050081",
			  "update %s set occcen6 = P050035 + P050082",
			  "update %s set occcen7 = P050041 + P050088",
			  "update %s set occcen8 = (age1+age2+P008018+P008057) + (P043007+P043014) + (P043008+P043015) + (P043004+P043011)",
							# under 16                 Unemployed          Not in labor force  in military
                          "update %s set sex1 = P008002", 
                          "update %s set sex2 = P008041", 
                          "update %s set persontotal = sex1 + sex2", 


                          "update %s set igq = P009026",
                          "update %s set nigq = P009027",

                          "alter table %s add column hhperson_tot_chk bigint",
                          "alter table %s add column wif_tot_chk bigint",
                          "alter table %s add column hhldrage_tot_chk bigint",
                          "alter table %s add column bldgsz_tot_chk bigint",                          
                          "alter table %s add column employment_tot_chk bigint",                          
                          "alter table %s add column age_tot_chk bigint",                          
                          "alter table %s add column occcen_tot_chk bigint",                          
                          "alter table %s add column gq_tot_chk bigint",                          
                          
                          "update %s set hhperson_tot_chk = hhperson1 + hhperson2 + hhperson3 + hhperson4 + hhperson5",
                          "update %s set wif_tot_chk = wif0 + wif1 + wif2 + wif3",
                          "update %s set hhldrage_tot_chk = hhldrage1 + hhldrage2 + hhldrage3 + hhldrage4",
                          "update %s set bldgsz_tot_chk = bldgsz1 + bldgsz2 + bldgsz3",

                          "update %s set employment_tot_chk = employment1 + employment2 + employment3 + employment4",
                          "update %s set age_tot_chk = age1 + age2 + age3 + age4 + age5 + age6 + age7 + age8 + age9 + age10",
                          "update %s set occcen_tot_chk = occcen1 + occcen2 + occcen3 + occcen4 + occcen5 + occcen6 + occcen7 + occcen8 ",

                          "update %s set gq_tot_chk = igq + nigq",
                          
                          "drop table hhld_marginals",
                          "drop table gq_marginals",
                          "drop table person_marginals",

                          """create table hhld_marginals select state, county, tract, bg, """\
                              """hhperson1, hhperson2, hhperson3, hhperson4, hhperson5, """\
                              """wif0, wif1, wif2, wif3, """\
                              """hhldrage1, hhldrage2, hhldrage3, hhldrage4, """\
                              """bldgsz1, bldgsz2, bldgsz3, """\
                              """hhperson_tot_chk, wif_tot_chk, hhldrage_tot_chk, bldgsz_tot_chk """\
                              """from %s""",

                          """create table gq_marginals select state, county, tract, bg, """\
                              """igq, nigq, gq_tot_chk from %s""",

                          """create table person_marginals select state, county, tract, bg, """\
                              """persontotal, employment1, employment2, employment3, employment4, """\
                              """age1, age2, age3, age4, age5, """\
                              """age6, age7, age8, age9, age10, """\
                              """occcen1, occcen2, occcen3, occcen4, occcen5, """\
                              """occcen6, occcen7, occcen8, """\
                              """sex1, sex2, """\
                              """employment_tot_chk, age_tot_chk, occcen_tot_chk """\
                              """from %s"""]


DEFAULT_SFACS_QUERIES = ["alter table %s add column hhperson1 bigint",
                          "alter table %s add column hhperson2 bigint",
                          "alter table %s add column hhperson3 bigint",
                          "alter table %s add column hhperson4 bigint",
                          "alter table %s add column hhperson5 bigint",
                          "alter table %s add column hhldrage1 bigint",
                          "alter table %s add column hhldrage2 bigint",
                          "alter table %s add column hhldrage3 bigint",
                          "alter table %s add column hhldrage4 bigint",
                          #"alter table %s add column bldgsz1 bigint",
                          #"alter table %s add column bldgsz2 bigint",
                          #"alter table %s add column bldgsz3 bigint",

                          "alter table %s add column persontotal bigint",
                          "alter table %s add column employment1 bigint",
                          "alter table %s add column employment2 bigint",
                          "alter table %s add column employment3 bigint",
                          "alter table %s add column employment4 bigint",
                          "alter table %s add column age1 bigint",
                          "alter table %s add column age2 bigint",
                          "alter table %s add column age3 bigint",
                          "alter table %s add column age4 bigint",
                          "alter table %s add column age5 bigint",
                          "alter table %s add column age6 bigint",
                          "alter table %s add column age7 bigint",
                          "alter table %s add column age8 bigint",
                          "alter table %s add column age9 bigint",
                          "alter table %s add column age10 bigint",
                          "alter table %s add column sex1 bigint",
                          "alter table %s add column sex2 bigint",

                          "alter table %s add column gq bigint",

                         "update %s set hhperson1 = B25009000003+B25009000011",
                         "update %s set hhperson2 = B25009000004+B25009000012",
                         "update %s set hhperson3 = B25009000005+B25009000013",
                         "update %s set hhperson4 = B25009000006+B25009000014",
                         "update %s set hhperson5 = B25009000007+B25009000015 + B25009000008+B25009000016 + B25009000009+B25009000017",

                         """update %s set hhldrage1 = (B25007000003+B25007000004+B25007000013+B25007000014)""", 
                         """update %s set hhldrage2 = (B25007000005+B25007000006+B25007000015+B25007000016)""", 
                         """update %s set hhldrage3 = (B25007000007+B25007000008+B25007000017+B25007000018)""", 
                         """update %s set hhldrage4 = (B25007000009+ B25007000010+B25007000011)+(B25007000019+ B25007000020+B25007000021)""",

                          #"update %s set bldgsz1 = B25024000002 + B25024000003",
                          #"update %s set bldgsz2 = B25024000004 + B25024000005 + B25024000006 + B25024000007 + B25024000008 + B25024000009",
                          #"update %s set bldgsz3 = B25024000010 + B25024000011",



                         "update %s set age1 = (B01001000003)+(B01001000027)",
                         "update %s set age2 = (B01001000004+B01001000005) + (B01001000028+B01001000029)",
                         "update %s set age3 = (B01001000006+B01001000007+B01001000008+B01001000009+B01001000010) + (B01001000030+B01001000031+B01001000032+B01001000033+B01001000034)",
                         "update %s set age4 = (B01001000011+B01001000012) + (B01001000035+B01001000036)",
                         "update %s set age5 = (B01001000013+B01001000014) + (B01001000037+B01001000038)",
                         "update %s set age6 = (B01001000015+B01001000016) + (B01001000039+B01001000040)",
                         "update %s set age7 = (B01001000017+B01001000018+B01001000019) + (B01001000041+B01001000042+B01001000043)",
                         "update %s set age8 = (B01001000020+B01001000021+B01001000022) + (B01001000044+B01001000045+B01001000046)",
                         "update %s set age9 = (B01001000023+B01001000024) + (B01001000047+B01001000048)",
                         "update %s set age10 = (B01001000025) + (B01001000049)",
                         
                         "update %s set sex1 = B01001000002",
                         "update %s set sex2 = B01001000026",
                         
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

                         "update %s set persontotal = sex1 + sex2",
                         "update %s set employment1 = sex1 + sex2 - employment2 - employment3 - employment4",

                         "update %s set gq = B26001000001",



                          "alter table %s add column hhperson_tot_chk bigint",
                          "alter table %s add column hhldrage_tot_chk bigint",
                          #"alter table %s add column bldgsz_tot_chk bigint",                          
                          "alter table %s add column employment_tot_chk bigint",                          
                          "alter table %s add column age_tot_chk bigint",                          
                          
                          "update %s set hhperson_tot_chk = hhperson1 + hhperson2 + hhperson3 + hhperson4 + hhperson5",
                          "update %s set hhldrage_tot_chk = hhldrage1 + hhldrage2 + hhldrage3 + hhldrage4",
                          #"update %s set bldgsz_tot_chk = bldgsz1 + bldgsz2 + bldgsz3",

                          "update %s set employment_tot_chk = employment1 + employment2 + employment3 + employment4",
                          "update %s set age_tot_chk = age1 + age2 + age3 + age4 + age5 + age6 + age7 + age8 + age9 + age10",

                        
                          "drop table hhld_marginals",
                          "drop table gq_marginals",
                          "drop table person_marginals",

                          """create table hhld_marginals select state, county, tract, bg, """\
                              """hhperson1, hhperson2, hhperson3, hhperson4, hhperson5, """\
                              """hhldrage1, hhldrage2, hhldrage3, hhldrage4, """\
                              #"""bldgsz1, bldgsz2, bldgsz3, """\
                              """hhperson_tot_chk, hhldrage_tot_chk """\
                              """from %s""",

                          """create table gq_marginals select state, county, tract, bg, """\
                              """gq from %s""",

                          """create table person_marginals select state, county, tract, bg, """\
                              """persontotal, employment1, employment2, employment3, employment4, """\
                              """age1, age2, age3, age4, age5, """\
                              """age6, age7, age8, age9, age10, """\
                              """sex1, sex2, """\
                              """employment_tot_chk, age_tot_chk """\
                              """from %s"""]


                   

                   
 



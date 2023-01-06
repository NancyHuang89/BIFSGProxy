import requests
import pandas as pd

class OneLine_BIFSG_Proxy():
    def __init__(self,FirstName, LastName, HouseNumberStreetName, City, State, ZipCode):
        print("Use BIFSG Package For Research Purpose")
        self.FirstName = FirstName.upper()
        self.LastName = LastName.upper()
        self.address = HouseNumberStreetName
        self.City = City
        self.State = State
        self.Zipcode = ZipCode

        payload = {'street':self.address,'city':self.City,'state':self.State,'zip':self.Zipcode,'benchmark':'Public_AR_Census2020','vintage':'Census2020_Census2020'}
        req = requests.get('https://geocoding.geo.census.gov/geocoder/geographies/address',params=payload)
        self.req_text = req.text
    
    def Surname(self):
        #immport Surname
        Surname = pd.read_csv('Inputs/Names_2010Census.csv')
        Surname.columns =['Surname','Rank','Count','Proportion_Per100k','Cum_Proportion','Perc_NHWhite_S','Perc_NHBlack_S','Perc_NPAAPI_S',
                          'Perc_NPAIAN_S','Perc_Multi_S','Perc_Hispanic_S']
        Surname.Perc_NHBlack_S = pd.to_numeric(Surname.Perc_NHBlack_S,errors='coerce')
        Surname.Perc_NPAIAN_S = pd.to_numeric(Surname.Perc_NPAIAN_S,errors='coerce')
        Surname.Perc_NHWhite_S = pd.to_numeric(Surname.Perc_NHWhite_S,errors='coerce')
        Surname.Perc_NPAAPI_S = pd.to_numeric(Surname.Perc_NPAAPI_S,errors='coerce')
        Surname.Perc_Multi_S = pd.to_numeric(Surname.Perc_Multi_S,errors='coerce')
        Surname.Perc_Hispanic_S = pd.to_numeric(Surname.Perc_Hispanic_S,errors='coerce')
        Surname = Surname.fillna(0)
        try:
            Surname_Prob = Surname[Surname['Surname']==self.LastName]
            S=Surname_Prob.to_dict('records')[0]
        except:
            Surname_Prob = Surname[Surname['Surname']=='ALL OTHER NAMES']
            S=Surname_Prob.to_dict('records')[0]
            print('Surname Cannot Be Found')
        return S

    def Firstname(self):
        Firstname = pd.read_excel('Inputs/firstnames.xlsx',sheet_name = 'Data')
        Firstname['total'] = Firstname['obs'].sum()
        Firstname['p_hispanic_f'] = Firstname.obs * Firstname.pcthispanic/sum(Firstname.obs * Firstname.pcthispanic)
        Firstname['p_white_f'] = Firstname.obs * Firstname.pctwhite/sum(Firstname.obs * Firstname.pctwhite)
        Firstname['p_black_f'] = Firstname.obs * Firstname.pctblack/sum(Firstname.obs * Firstname.pctblack)
        Firstname['p_api_f'] = Firstname.obs * Firstname.pctapi/sum(Firstname.obs * Firstname.pctapi)
        Firstname['p_aian_f'] = Firstname.obs * Firstname.pctaian/sum(Firstname.obs * Firstname.pctaian)
        Firstname['p_mrace_f'] = Firstname.obs * Firstname.pct2prace/sum(Firstname.obs * Firstname.pct2prace)
        try:
            Firstname_Prob = Firstname[Firstname['firstname']==self.FirstName]
            F=Firstname_Prob.to_dict('records')[0]
        except:
            Firstname_Prob = Firstname[Firstname['firstname']=='ALL OTHER FIRST NAMES']
            F=Firstname_Prob.to_dict('records')[0]
            print('Firstname Cannot Be Found')
        return F

    def Address(self):
        census =  pd.read_csv('Inputs/CensusFlatFile2020_slim.csv',header=0,low_memory=False)
        census['TotalAAPI'] = census['TotalAsian'] + census['TotalPI']
        census['Other_Multi'] = census['TotalOther'] + census['TotalMulti']

        census['PERC_Population_US'] = census.TotalPop/census.TotalPop.sum()
        census['PERC_HISPANIC_US'] = census.TotalHispanic/census.TotalHispanic.sum()
        census['PERC_NP_WHITE_US'] = census.TotalWhite/census.TotalWhite.sum()
        census['PERC_NP_BLACK_US'] = census.TotalBlackAfricanAmerican/census.TotalBlackAfricanAmerican.sum()
        census['PERC_NP_AAPI_US'] = census.TotalAAPI/census.TotalAAPI.sum()
        census['PERC_NP_AIAN_US'] = census.TotalAIAN/census.TotalAIAN.sum()
        census['PERC_OTHER_MULTI_US'] = census.Other_Multi/census.Other_Multi.sum()
        census_Prob = census[(census['FIPS_State_Code']==1)&(census['FIPS_County_Code']==1)&(census['Census_Tract']==20100)]
        C=census_Prob.to_dict('records')[0]
        return C
    
    def GetStateCode(self):
        subtext1 = self.req_text[self.req_text.find('STATE CODE')::]
        subtext2 = subtext1[subtext1.find('</span>')::]
        subtext3 = subtext2[subtext2.find('>')+1:subtext2.find('<br>')]
        return int(subtext3)

    def GetCountyCode(self):
        subtext1 = self.req_text[self.req_text.find('COUNTY CODE')::]
        subtext2 = subtext1[subtext1.find('</span>')::]
        subtext3 = subtext2[subtext2.find('>')+1:subtext2.find('<br>')]
        return int(subtext3)
        
    def GetTractCode(self):
        subtext1 = self.req_text[self.req_text.find('TRACT CODE')::]
        subtext2 = subtext1[subtext1.find('</span>')::]
        subtext3 = subtext2[subtext2.find('>')+1:subtext2.find('<br>')]
        return int(subtext3)
    
    def BIFSG_Proxy(self):
        S = self.Surname()
        F = self.Firstname()
        C = self.Address()
        #BIFSG Proxy
        BIFSG_NHWhite = S['Perc_NHWhite_S']*F['p_white_f']*C['PERC_NP_WHITE_US']/(S['Perc_NHWhite_S']*F['p_white_f']*C['PERC_NP_WHITE_US']+
                                                                                             S['Perc_Hispanic_S']*F['p_hispanic_f']*C['PERC_HISPANIC_US']+
                                                                                             S['Perc_NHBlack_S']*F['p_black_f']*C['PERC_NP_BLACK_US']+
                                                                                             S['Perc_NPAAPI_S']*F['p_api_f']*C['PERC_NP_AAPI_US']+
                                                                                             S['Perc_NPAIAN_S']*F['p_aian_f']*C['PERC_NP_AIAN_US']+
                                                                                             S['Perc_Multi_S']*F['p_mrace_f']*C['PERC_OTHER_MULTI_US'])

        BIFSG_Hispanic = S['Perc_Hispanic_S']*F['p_hispanic_f']*C['PERC_HISPANIC_US']/(S['Perc_NHWhite_S']*F['p_white_f']*C['PERC_NP_WHITE_US']+
                                                                                             S['Perc_Hispanic_S']*F['p_hispanic_f']*C['PERC_HISPANIC_US']+
                                                                                             S['Perc_NHBlack_S']*F['p_black_f']*C['PERC_NP_BLACK_US']+
                                                                                             S['Perc_NPAAPI_S']*F['p_api_f']*C['PERC_NP_AAPI_US']+
                                                                                             S['Perc_NPAIAN_S']*F['p_aian_f']*C['PERC_NP_AIAN_US']+
                                                                                             S['Perc_Multi_S']*F['p_mrace_f']*C['PERC_OTHER_MULTI_US'])

        BIFSG_NHBlack = S['Perc_NHBlack_S']*F['p_black_f']*C['PERC_NP_BLACK_US']/(S['Perc_NHWhite_S']*F['p_white_f']*C['PERC_NP_WHITE_US']+
                                                                                             S['Perc_Hispanic_S']*F['p_hispanic_f']*C['PERC_HISPANIC_US']+
                                                                                             S['Perc_NHBlack_S']*F['p_black_f']*C['PERC_NP_BLACK_US']+
                                                                                             S['Perc_NPAAPI_S']*F['p_api_f']*C['PERC_NP_AAPI_US']+
                                                                                             S['Perc_NPAIAN_S']*F['p_aian_f']*C['PERC_NP_AIAN_US']+
                                                                                             S['Perc_Multi_S']*F['p_mrace_f']*C['PERC_OTHER_MULTI_US'])

        BIFSG_NHAAPI = S['Perc_NPAAPI_S']*F['p_api_f']*C['PERC_NP_AAPI_US']/(S['Perc_NHWhite_S']*F['p_white_f']*C['PERC_NP_WHITE_US']+
                                                                                             S['Perc_Hispanic_S']*F['p_hispanic_f']*C['PERC_HISPANIC_US']+
                                                                                             S['Perc_NHBlack_S']*F['p_black_f']*C['PERC_NP_BLACK_US']+
                                                                                             S['Perc_NPAAPI_S']*F['p_api_f']*C['PERC_NP_AAPI_US']+
                                                                                             S['Perc_NPAIAN_S']*F['p_aian_f']*C['PERC_NP_AIAN_US']+
                                                                                             S['Perc_Multi_S']*F['p_mrace_f']*C['PERC_OTHER_MULTI_US'])

        BIFSG_NHAIAN = S['Perc_NPAIAN_S']*F['p_aian_f']*C['PERC_NP_AIAN_US']/(S['Perc_NHWhite_S']*F['p_white_f']*C['PERC_NP_WHITE_US']+
                                                                                             S['Perc_Hispanic_S']*F['p_hispanic_f']*C['PERC_HISPANIC_US']+
                                                                                             S['Perc_NHBlack_S']*F['p_black_f']*C['PERC_NP_BLACK_US']+
                                                                                             S['Perc_NPAAPI_S']*F['p_api_f']*C['PERC_NP_AAPI_US']+
                                                                                             S['Perc_NPAIAN_S']*F['p_aian_f']*C['PERC_NP_AIAN_US']+
                                                                                             S['Perc_Multi_S']*F['p_mrace_f']*C['PERC_OTHER_MULTI_US'])

        BIFSG_NHMulti = S['Perc_Multi_S']*F['p_mrace_f']*C['PERC_OTHER_MULTI_US']/(S['Perc_NHWhite_S']*F['p_white_f']*C['PERC_NP_WHITE_US']+
                                                                                             S['Perc_Hispanic_S']*F['p_hispanic_f']*C['PERC_HISPANIC_US']+
                                                                                             S['Perc_NHBlack_S']*F['p_black_f']*C['PERC_NP_BLACK_US']+
                                                                                             S['Perc_NPAAPI_S']*F['p_api_f']*C['PERC_NP_AAPI_US']+
                                                                                             S['Perc_NPAIAN_S']*F['p_aian_f']*C['PERC_NP_AIAN_US']+
                                                                                             S['Perc_Multi_S']*F['p_mrace_f']*C['PERC_OTHER_MULTI_US'])
        return {'White':BIFSG_NHWhite,
               'Hispanic':BIFSG_Hispanic,
               'Black':BIFSG_NHBlack,
               'Asian':BIFSG_NHAAPI,
               'AIAN':BIFSG_NHAIAN,
               'Multi-Race':BIFSG_NHMulti}
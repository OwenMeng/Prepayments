
# coding: utf-8

# # Loading Package

# In[1]:


# Load Packages
import numpy as np
import pandas as pd
import scipy as sc
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as pyplot
import time
import timeit


# In[2]:


import tensorflow as tf


# In[13]:


df_CDR= pd.read_csv('U:/Ratio/Deal1058/df_CDR_Deal1058_Bucket_cumdefault.csv',header=0,parse_dates=[0],index_col=0)
df_CDR = df_CDR.apply(pd.to_numeric).fillna(0)


# In[14]:


df_CDR_sum = 1-df_CDR
df_CDR_sum = df_CDR_sum.sort_index(ascending=True)
df_CDR_out = 1-df_CDR_sum.cumprod()
df_CDR_out = df_CDR_out.sort_index(ascending=False)
df_CDR_out


# # Function Lists

# In[23]:


def cleandata(df):
    for i in range(len(df.columns)):
        j=df.columns[i]
        df.loc[df.iloc[:,i].isin(['-']),df.columns[i]]=''
        df[[j]] = df[[j]].apply(pd.to_numeric)
    return df

def summarizeMonth(df):
    g = df.groupby(pd.TimeGrouper("M"))
    grouped = g.sum()
    grouped_final = grouped.sort_index(ascending=False)
    return grouped_final

def Mapping(df_main,deal_level,group_level,DealMap):
    dfcopy = df_main.copy(deep=True)
    #dfcopy = df_main
    for i in range(len(df_main.columns)):
        #print(df_main.columns[i])
        dfcopy.columns.values[i] = list(set(DealMap.loc[DealMap[deal_level] == dfcopy.columns[i], group_level]))[0]
    dfout = dfcopy.groupby(lambda x:x, axis=1).sum()
    return dfout

def CalculatingCPR(df):
    dfcopy = df.copy(deep=True)
    for i in range(len(df.columns)):
        #print(i)
        if(np.count_nonzero(df.iloc[:,i])==0):
            tempdf = df.iloc[0:len(df.iloc[:,i]),i]
        else:
            if(len(df.iloc[:,i])-1 > np.amax(np.nonzero(df.iloc[:,i]))):
                tempdf = df.iloc[0:len(df.iloc[:np.amax(np.nonzero(df.iloc[:,i]))]),i]
            else:
                tempdf = df.iloc[0:len(df.iloc[:,i]),i]
        SMM = tempdf.diff(periods=-1)*-1/tempdf
        CPR = 1-((1-SMM)**12)
        dfcopy.iloc[:,i] = CPR
        dfcopy.loc[dfcopy.iloc[:,i]<=0,dfcopy.columns[i]] = ''
    return dfcopy

    
def CalculatingCDR(df_defaults,df_ActiveUPB):
    dfcopy = df_ActiveUPB.copy(deep=True)
    for i in range(len(df_ActiveUPB.columns)):
        #print(i)
        if (df_ActiveUPB.columns[i] not in df_defaults.columns.values):
            print(df_ActiveUPB.columns[i])
            dfcopy.iloc[:,i] = 0.0
        else: #Default accurs
            j = list(df_defaults.columns).index(df_ActiveUPB.columns[i])
            tempdf = df_defaults.loc[:,df_ActiveUPB.columns[i]]
#             if(np.count_nonzero(tempdf)!=0):
#                 if(len(tempdf)-1 > np.amax(np.nonzero(tempdf))):
#                     tempdf = df_defaults.iloc[0:len(df_defaults.iloc[:np.amax(np.nonzero(tempdf))]),j]
#                 else:
#                     tempdf = df_defaults.iloc[0:len(tempdf),j]
            MDR = pd.Series.diff(tempdf,periods=-1)*-1/pd.Series.shift(df_ActiveUPB[df_ActiveUPB.columns[i]],periods=-1)
            CDR = 1-((1-MDR)**12)
            dfcopy.iloc[:,i] = CDR
        dfcopy.loc[dfcopy.iloc[:,i]<0,dfcopy.columns[i]] = 0
    return dfcopy


def CalculatingCDR_Deal(df_UPB_defaulted,df_UPBCurrent,df_PrincipalACR,CalcOption='CDR'):
    print(CalcOption)
    dfcopy = df_UPBCurrent.copy(deep=True)
    df_UPBCurrent2 = df_UPBCurrent.shift(periods=-1)
    for i in range(len(df_UPBCurrent.columns)):
        #print(i)
        if (df_UPBCurrent.columns[i] not in df_UPB_defaulted.columns.values):
            #print(df_ActiveUPB.columns[i])
            dfcopy.iloc[:,i] = 0.0
        else: #Default accurs
            j = list(df_UPB_defaulted.columns).index(df_UPBCurrent.columns[i])
            tempdf = df_UPB_defaulted.loc[:,df_UPBCurrent.columns[i]]
            #UPBCurrent = pd.Series.shift(df_UPBCurrent[df_UPBCurrent.columns[i]],periods=-1)
            a = df_UPBCurrent2[df_UPBCurrent.columns[i]].subtract(df_PrincipalACR[df_PrincipalACR.columns[i]],fill_value=0)
            a = a.sort_index(ascending=False)
            MDR = tempdf/a
            #subtract(df_PrincipalACR[df_PrincipalACR.columns[0]],fill_value=0)
            CDR = 1-((1-MDR)**12)
            if(CalcOption=='CDR'):
                dfcopy.iloc[:,i] = CDR
            elif(CalcOption=='MDR'):
                dfcopy.iloc[:,i] = MDR               
        dfcopy.loc[dfcopy.iloc[:,i]<0,dfcopy.columns[i]] = 0
        dfcopy.loc[dfcopy.iloc[:,i]>1,dfcopy.columns[i]] = 1 
    if(CalcOption=='CumDefault'):
    {
        df_CDR_new = dfcopy.copy(deep=True)
        df_CDR_new2 = 1-df_CDR_new
        df_CDR_new3 = df_CDR_new2.sort_index(ascending=True)
        df_CDR_out1 = 1-df_CDR_new3.cumprod()
        df_CDR_out2 = df_CDR_out1.sort_index(ascending=False) 
        return df_CDR_out2
    }
    else:
        return dfcopy


def CalculatingCDR_Deal2(df_UPB_defaulted,df_UPBCurrent):
    dfcopy = df_UPB_defaulted.copy(deep=True)
    for i in range(len(df_UPB_defaulted.columns)):
        #print(i)
        if (df_UPB_defaulted.columns[i] not in df_UPBCurrent.columns.values):
            #print(df_ActiveUPB.columns[i])
            dfcopy.iloc[:,i] = 0.0
        else: #Default accurs
            #j = list(df_UPB_defaulted.columns).index(df_UPBCurrent.columns[i])
            tempdf = df_UPB_defaulted.loc[:,df_UPB_defaulted.columns[i]]
            MDR = tempdf/pd.Series.shift(df_UPBCurrent[df_UPB_defaulted.columns[i]],periods=-1)
            #CDR = 1-((1-MDR)**12)
            dfcopy.iloc[:,i] = MDR
        dfcopy.loc[dfcopy.iloc[:,i]<0,dfcopy.columns[i]] = 0
        dfcopy.loc[dfcopy.iloc[:,i]>1,dfcopy.columns[i]] = 1
    return dfcopy

def CalculatingSeverity_NOTUSE(df_Defaults, df_LiqandPIF, df_LossMitProceed):
    dfcopy = df_Defaults.copy(deep=True)
    #pifnames = df_LiqandPIF.columns
    LossProceeds = df_LossMitProceed.columns

    for i in range(len(df_Defaults.columns)):
        #print(i)
        tempdf = df_Liquidated.iloc[:,i]
        if(df_Liquidated.columns[i] in pifnames):
            tempdf = tempdf - df_LiqandPIF.loc[:,df_Liquidated.columns[i]]
            if(df_Liquidated.columns[i] in LossProceeds):
                tempdf = tempdf - df_LossMitProceed.loc[:,df_Liquidated.columns[i]]
        elif(df_Liquidated.columns[i] in LossProceeds):
            tempdf = tempdf - df_LossMitProceed.loc[:,df_Liquidated.columns[i]]    
        Severity = tempdf/df_Liquidated.iloc[:,i]
        #CDR = 1-((1-MDR)**12)
        dfcopy.iloc[:,i] = Severity
        dfcopy.loc[dfcopy.iloc[:,i]<0,dfcopy.columns[i]] = 0
    return dfcopy

def CalculatingSeverity(df_Defaults, df_LossMitProceed):
    dfcopy = df_Defaults.copy(deep=True)    
    LossProceeds = df_LossMitProceed.columns
    for i in range(len(df_Defaults.columns)):
        if(df_Defaults.columns[i] in LossProceeds):
            tempdf = df_LossMitProceed.loc[:,df_Defaults.columns[i]]
            Recovery = tempdf/pd.Series.shift(df_Defaults[df_Defaults.columns[i]],periods=-1)
        else:
            tempdf = 0
            #tempdf = pd.Series.diff(df_Defaults.iloc[:,i],periods=-1)*-1
            Recovery = 1
        dfcopy.iloc[:,i] = 1-Recovery
        dfcopy.loc[dfcopy.iloc[:,i]<0,dfcopy.columns[i]] = ''
    return dfcopy


# # Grouping by Sector, Deal, and Risk Bucket

# In[ ]:


#Create Mapping Table#


# In[3]:


DealMap = pd.read_csv('U:/Ratio/DealMapping.csv',header=0)
DealMap = DealMap.replace('-','Unknown')
set(DealMap['Loan Sector'])


# In[4]:


LoanMap = pd.read_csv('U:/Ratio/LoanMapping.csv',header=0)
LoanMap = LoanMap.replace('-','Unknown')
set(LoanMap['WAM ID'])


# In[5]:


RiskMap = pd.read_csv('U:/Ratio/Deal 1058 RiskBucketMapping.csv',header=0)
#DealMap = DealMap.replace('-','Unknown')
set(RiskMap['Risk Bucket'])
RiskMap = RiskMap.astype(str)


# In[7]:


#Remove Reverse# 
Dropgroups = ['Reverse','Unknown']
Dropdeals = ['6001 - Reverse Aurora','6002 - Reverse Merrill','6003 - Lehman RE Ltd. (In Liquidation)','6006 - Reverse Nationstar','6501 - Irish Reverse','6004 - AAG']
DropID = ['600610055','600610067']


# df = pd.read_csv('U:/Ratio/UPB_Real.csv',header=0,parse_dates=[0],index_col=0)
# df = Mapping(df,'Deal Name & Moniker','Loan Sector',DealMap)

# # Calculate CPR

# In[92]:


df_UPBFull = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_Real_byDeal.csv',header=0,parse_dates=[0],index_col=0)

df_UPBFull_cleaned = cleandata(df_UPBFull)
df_CPR = CalculatingCPR(df_UPBFull_cleaned)
df_CPR.to_csv('U:/Ratio/CPR_byDeal.csv')


# In[70]:


df_UPBFull = pd.read_csv('U:/Ratio/UPB_Real_byWAMID.csv',header=0,parse_dates=[0],index_col=0)
df_UPBFull_cleaned = cleandata(df_UPBFull)
df_CPR = CalculatingCPR(df_UPBFull_cleaned)
df_CPR.to_csv('U:/Ratio/CPR_byWAMID.csv')


# In[93]:


#df2 = pd.read_csv('U:/Ratio/CPR.csv',header=0,parse_dates=[0],index_col=0)
fig = pyplot.figure()
ax = pyplot.gca()
ax.plot(df_CPR)

ax.relim()      # make sure all the data fits
ax.autoscale()
#handles, labels = ax.get_legend_handles_labels()
#ax.legend(handles, labels)


# In[158]:


df_UPBFull = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_Real_byDeal.csv',header=0,parse_dates=[0],index_col=0)
df_UPBFull_dropped = df_UPBFull.drop([col for col in df_UPBFull.columns if any(x in col for x in Dropdeals)],axis=1)
df_UPBFull_cleaned = cleandata(df_UPBFull_dropped)
df_UPBFull_cleaned = df_UPBFull_cleaned.fillna(method='ffill')


# In[144]:


df_UPBFull_cleaned.to_csv('U:/Ratio/DataIntegrity/UPB_Real_byDeal_cleaned.csv')


# In[159]:


#df_UPBFull = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_Real_byDeal.csv',header=0,parse_dates=[0],index_col=0)
#df_UPBFull = df_UPBFull.drop([col for col in df_UPBFull.columns if any(x in col for x in Dropdeals)],axis=1)
#df_UPBFull_cleaned = cleandata(df_UPBFull)
df_UPBFull_cleaned = Mapping(df_UPBFull_cleaned,'Deal Name & Moniker','Loan Sector',DealMap)

#df_cleaned_bygroup = df2.drop([col for col in df2.columns if any(x in col for x in Dropgroups)],axis=1)
df_CPRgroup = CalculatingCPR(df_UPBFull_cleaned)
df_CPRgroup.to_csv('U:/Ratio/WAMCAM_Upload/CPR_bygroup_final.csv')


# In[387]:


##############################Calculation Starts########################################
#pif+current UPB#

###Remove Historical Liquidated Pool without a loss mit###
## Active Only Summary ##
df_UPBFull = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_AllexPIF_byWAMID_Residential.csv',header=0,parse_dates=[0],index_col=0)
df_UPBFull = df_UPBFull.drop([col for col in df_UPBFull.columns if any(x in col for x in DropID)],axis=1)
df_UPBFull.replace(to_replace = '-', value = '', inplace = True)
df_UPBFull = df_UPBFull.apply(pd.to_numeric)
df_UPBFull_exPIF = df_UPBFull.loc[:, ~(df_UPBFull.iloc[0]==0)]
df_UPBFull_exPIF


# In[415]:


df_UPBFull = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_AllexPIF_byWAMID_Residential.csv',header=0,parse_dates=[0],index_col=0)
df_UPBFull = df_UPBFull.drop([col for col in df_UPBFull.columns if any(x in col for x in DropID)],axis=1)
df_UPBFull.replace(to_replace = '-', value = '', inplace = True)
df_UPBFull = df_UPBFull.apply(pd.to_numeric)
df_UPBFull_issues = df_UPBFull.loc[:, (df_UPBFull.iloc[0]==0)]
df_UPBFull_issues.to_csv('U:/Ratio/DataIntegrity/Loans_liquidated_without_type.csv')


# In[318]:


## PIF Only Summary ##
df_UPBPIF = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_PIFOnly_byWAMID_Residential.csv',header=0,parse_dates=[0],index_col=0)
df_UPBPIF = df_UPBPIF.drop([col for col in df_UPBFull.columns if any(x in col for x in DropID)],axis=1)
df_UPBPIF.replace(to_replace = '-', value = '', inplace = True)
df_UPBPIF = df_UPBPIF.apply(pd.to_numeric)
#df_UPBPIF = df_UPBPIF.loc[:, ~(df_UPBFull.iloc[0]==0)]
df_UPBPIF


# In[337]:


df_UPBFull_Curent = pd.merge(df_UPBFull_exPIF, df_UPBPIF,how='outer',left_index=True,right_index=True)
df_UPBFull_Curent = df_UPBFull_Curent.fillna(method='ffill')
df_UPBFull_cleaned = summarizeMonth(df_UPBFull_Curent)
df_UPBFull_cleaned = df_UPBFull_cleaned.replace(0,pd.np.nan).ffill()
df_UPBFull_cleaned = df_UPBFull_cleaned.fillna(0)


# In[ ]:


#####################################Calculate For Deals#########################################


# In[44]:


df_UPBFull = pd.read_csv('U:/Ratio/Deal1058/UPB Active.csv',header=0,parse_dates=[0],index_col=0)
df_UPBFull = df_UPBFull.apply(pd.to_numeric)
df_UPBFull_cleaned = df_UPBFull.fillna(0)
df_UPBFull_cleaned


# In[45]:


df_NetLossProceeds_PIF = pd.read_csv('U:/Ratio/Deal1058/LossMitPIF_Deal1058.csv',header=0,parse_dates=[0],index_col=0)
df_NetLossProceeds_PIF = df_NetLossProceeds_PIF.apply(pd.to_numeric)
df_NetLossProceeds_PIF = df_NetLossProceeds_PIF.fillna(0)
df_NetLossProceeds_PIF_cleaned  = summarizeMonth(df_NetLossProceeds_PIF)
df_NetLossProceeds_PIF_cleaned
#Combined & Clean#
df_NetLossProceeds_PIF_cleaned  = summarizeMonth(df_NetLossProceeds_PIF_cleaned)


# In[46]:


#df_NetLossProceeds_PIF_cleaned
df_combined = df_UPBFull_cleaned.add(df_NetLossProceeds_PIF_cleaned).fillna(df_UPBFull_cleaned)
df_combined = df_combined.sort_index(ascending=False)


# In[47]:


####Calculate CPR for All by Deal #####
df_combined_cleaned = Mapping(df_combined,'WAM ID','Deal Name & Moniker',LoanMap)
df_CPR_Deal = CalculatingCPR(df_combined_cleaned)
df_CPR_Deal.to_csv('U:/Ratio/Deal1058/CPR_Deal_1058.csv')


# In[43]:


####Calculate CPR for All by Bucket #####
df_combined_cleaned = Mapping(df_combined,'WAM ID','Risk Bucket',RiskMap)
df_CPR_Deal = CalculatingCPR(df_combined_cleaned)
df_CPR_Deal.to_csv('U:/Ratio/Deal1058/CPR_byRiskBucket_1058.csv')


# In[326]:


#Clean PIF Table#--Add to UPB Table to avoid missing loss mit
df_NetLossProceeds_PIF = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_PaidInFull_byWAMID_Resi.csv',header=0,parse_dates=[0],index_col=0)
for i in range(len(df_NetLossProceeds_PIF.columns)):
    j=df_NetLossProceeds_PIF.columns[i]
    df_NetLossProceeds_PIF.loc[df_NetLossProceeds_PIF.iloc[:,i].isin(['-']),df_NetLossProceeds_PIF.columns[i]]=0
    df_NetLossProceeds_PIF[[j]] = df_NetLossProceeds_PIF[[j]].apply(pd.to_numeric)

# Summarized by Month End according to the liquidation date #
df_NetLossProceeds_PIF  = summarizeMonth(df_NetLossProceeds_PIF)
df_NetLossProceeds_PIF


# In[334]:


## UPB Summary ##
#df_UPBFull = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_FullCurrent_byWAMID_Resi.csv',header=0,parse_dates=[0],index_col=0)
#df_UPBFull_cleaned = cleandata(df_UPBFull)
#df_UPBFull_Curent = df_UPBFull_Curent.fillna(method='ffill')
#df_UPBFull_cleaned = summarizeMonth(df_UPBFull_Curent)


# In[355]:


#Combined & Clean#
df_combined = df_UPBFull_cleaned.add(df_NetLossProceeds_PIF).fillna(df_UPBFull_cleaned)
df_combined = df_combined.sort_index(ascending=False)
df_combined_dropped = df_combined.drop([col for col in df_combined.columns if any(x in col for x in DropID)],axis=1)


# In[361]:


####Calculate CPR for Agg#####
df_byDeal = Mapping(df_combined_dropped,'WAM ID','Deal Name & Moniker',LoanMap)
df_byDeal.to_csv('U:/Ratio/DataIntegrity/UPB_byDeal_Resi.csv')
df_CPR_Deal = CalculatingCPR(df_byDeal)
df_CPR_Deal.to_csv('U:/Ratio/WAMCAM_Upload/df_CPR_byDeal_Resi_Agg.csv')


# In[388]:


##Prepare Data for All ex-PIF##
df_UPBFull_exPIF = df_UPBFull_exPIF.fillna(method='ffill')
df_UPBFull_exPIF_cleaned = summarizeMonth(df_UPBFull_exPIF)
df_UPBFull_exPIF_cleaned = df_UPBFull_exPIF_cleaned.replace(0,pd.np.nan).ffill()
df_UPBFull_exPIF_cleaned = df_UPBFull_exPIF_cleaned.fillna(0)
df_UPBFull_exPIF_cleaned



# In[389]:


####Calculate CPR for All ex-PIF#####
df_UPBFull_exPIF_cleaned = Mapping(df_UPBFull_exPIF_cleaned,'WAM ID','Deal Name & Moniker',LoanMap)
df_UPBFull_exPIF_cleaned.to_csv('U:/Ratio/DataIntegrity/Active_exPIF_UPB_byDeal_Resi.csv')
df_CPR_Deal_All_exPIF = CalculatingCPR(df_UPBFull_exPIF_cleaned)
df_CPR_Deal_All_exPIF = df_CPR_Deal_All_exPIF.fillna('')
df_CPR_Deal_All_exPIF = df_CPR_Deal_All_exPIF.apply(pd.to_numeric)
df_CPR_Deal_All_exPIF.to_csv('U:/Ratio/WAMCAM_Upload/df_CPR_byDeal_Resi_AllexPIF.csv')


# In[391]:


##Prepare Data for PIF Only##
df_PIF_combined = df_UPBPIF.add(df_NetLossProceeds_PIF).fillna(df_UPBPIF)
df_PIF_combined = df_PIF_combined.sort_index(ascending=False)
df_PIF_combined_dropped = df_PIF_combined.drop([col for col in df_PIF_combined.columns if any(x in col for x in DropID)],axis=1)


# In[394]:


####Calculate CPR for PIF Only #####
df_PIF_combined_dropped_cleaned = Mapping(df_PIF_combined_dropped,'WAM ID','Deal Name & Moniker',LoanMap)
df_PIF_combined_dropped_cleaned.to_csv('U:/Ratio/DataIntegrity/PIFonly_UPB_byDeal_Resi.csv')
df_CPR_Deal_PIF_Only = CalculatingCPR(df_PIF_combined_dropped_cleaned)
df_CPR_Deal_PIF_Only = df_CPR_Deal_PIF_Only.fillna('')
df_CPR_Deal_PIF_Only = df_CPR_Deal_PIF_Only.apply(pd.to_numeric)
df_CPR_Deal_PIF_Only.to_csv('U:/Ratio/WAMCAM_Upload/df_CPR_byDeal_Resi_PIF_Only.csv')


# In[204]:


df_bySector = Mapping(df_combined_dropped,'WAM ID','Loan Sector',LoanMap)
df_bySector.to_csv('U:/Ratio/DataIntegrity/UPB_bygroup_Resi.csv')
df_CPRgroup = CalculatingCPR(df_bySector)
df_CPRgroup.to_csv('U:/Ratio/WAMCAM_Upload/df_CPR_bySector_Resi.csv')


# In[382]:


df_CPR_Deal_All_exPIF = df_CPR_Deal_All_exPIF.apply(pd.to_numeric)


# In[395]:


fig = pyplot.figure()
ax = df_CPR_Deal_PIF_Only.plot()
ax.grid()


# In[76]:


df_UPBFull_cleaned = cleandata(df_UPBFull)
df2 = Mapping(df_UPBFull_cleaned,'WAM ID','Loan Sector',LoanMap)
df_cleaned_bygroup = df2.drop([col for col in df2.columns if any(x in col for x in Dropgroups)],axis=1)
df_CPRgroup = CalculatingCPR(df_cleaned_bygroup)
df_CPRgroup.to_csv('U:/Ratio/CPR_bygroup.csv')


# In[119]:


df_cleaned_bygroup.to_csv('U:/Ratio/DataIntegrity/UPB_bygroup.csv')


# In[95]:


fig = pyplot.figure()
ax = df_CPRgroup.plot()
ax.grid()


# In[72]:


#By Groups#
df_UPBFull = pd.read_csv('U:/Ratio/UPB_Real_byWAMID.csv',header=0,parse_dates=[0],index_col=0)
df_UPBFull_cleaned = cleandata(df_UPBFull)
df2 = Mapping(df_UPBFull_cleaned,'WAM ID','Loan Sector',LoanMap)
df_cleaned_bygroup = df2.drop([col for col in df2.columns if any(x in col for x in Dropgroups)],axis=1)

df_CPRgroup = CalculatingCPR(df_cleaned_bygroup)
df_CPRgroup.to_csv('U:/Ratio/CPR_bygroup.csv')

fig = pyplot.figure()
ax = df_CPRgroup.plot()
ax.grid()
#df.CPR.plot(kind='bar')
#pyplot.gca()

#ax.relim()      # make sure all the data fits
#ax.autoscale()


# # Calculation CDR

# In[ ]:


#Read Defaults Data#


# In[ ]:


#Combined & Clean#
df_combined = df_UPBFull_cleaned.add(df_NetLossProceeds_PIF).fillna(df_UPBFull_cleaned)
df_combined_dropped = df_combined.drop([col for col in df_combined.columns if any(x in col for x in DropID)],axis=1)


# In[146]:


#Defaults = All Liq UPB - [liquidated & Paid-In-Full] UPB#
#CDR = Defaults / Active UPB @ (t-1)
df2 = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_FullDefaulted_byWAMID_Resi.csv',header=0,parse_dates=[0],index_col=0)
df2 = df2.drop([col for col in df2.columns if any(x in col for x in DropID)],axis=1)

df_ActiveUPB = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_FullCurrent_byWAMID_Resi.csv',header=0,parse_dates=[0],index_col=0)
df_ActiveUPB = df_ActiveUPB.drop([col for col in df_ActiveUPB.columns if any(x in col for x in DropID)],axis=1)

df_defaults = cleandata(df2)
df_ActiveUPB = cleandata(df_ActiveUPB)

df_defaults = df_defaults.fillna(method='ffill')


# In[227]:


##################Calculation Start - Resi Loan###################

#Defaults = All Liq UPB - [liquidated & Paid-In-Full] UPB#
#CDR = Defaults / Active UPB @ (t-1)
df2 = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_FullDefaulted_byWAMID_Resi.csv',header=0,parse_dates=[0],index_col=0)
df2 = df2.drop([col for col in df2.columns if any(x in col for x in DropID)],axis=1)

df_ActiveUPB = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_FullCurrent_byWAMID_Resi.csv',header=0,parse_dates=[0],index_col=0)
df_ActiveUPB = df_ActiveUPB.drop([col for col in df_ActiveUPB.columns if any(x in col for x in DropID)],axis=1)
#Need Improvements#
df_defaults = cleandata(df2)
df_ActiveUPB = cleandata(df_ActiveUPB)

df_defaults = Mapping(df_defaults,'WAM ID','Deal Name & Moniker',LoanMap)
df_ActiveUPB = Mapping(df_ActiveUPB,'WAM ID','Deal Name & Moniker',LoanMap)



# In[381]:


##################Calculation Start - Resi Single Loan###################

#CDR = Defaults @ t / Current UPB @ (t-1)
file_name = '1058_Citi_2nd_NoteSaleCur'
file_name2 = '1058_Citi_2nd_TrueCur'
df_single = pd.read_csv('U:/Ratio/WAMCAM_Download/'+file_name+'.csv')
df_single2 = pd.read_csv('U:/Ratio/WAMCAM_Download/'+file_name2+'.csv')
df_single.replace(to_replace = '-', value = '', inplace = True)
df_single['Date'] = df_single['Date'].astype('object')

df_single2.replace(to_replace = '-', value = '', inplace = True)
df_single2['Date'] = df_single2['Date'].astype('object')



# In[5]:


file_name = 'UPB Data for CPR'
#file_name2 = '1058_Citi_2nd_TrueCur'
df_single = pd.read_csv('U:/Ratio/Deal1058/'+file_name+'.csv')
#df_single2 = pd.read_csv('U:/Ratio/WAMCAM_Download/'+file_name2+'.csv')
#df_single.replace(to_replace = '-', value = '', inplace = True)
df_single['Date'] = df_single['Date'].astype('object')

#df_single2.replace(to_replace = '-', value = '', inplace = True)
#df_single2['Date'] = df_single2['Date'].astype('object')


# In[7]:


dfnew = df_single.groupby('Status Checks')
df_current = dfnew2.get_group('ActiveBalance')
df_PIF = dfnew.get_group('Defaulted')


# In[6]:


##################Calculation for Deal 1058 ###################
#%timeit 
df_ActiveUPB = pd.read_csv('U:/Ratio/Deal1058/ActiveUPB.csv',header=0,parse_dates=[0],index_col=0)
df_DefaultUPB = pd.read_csv('U:/Ratio/Deal1058/DefaultsUPB.csv',header=0,parse_dates=[0],index_col=0)
df_PrincipalACR= pd.read_csv('U:/Ratio/Deal1058/PrincipalACR.csv',header=0,parse_dates=[0],index_col=0)
df_ActiveUPB = df_ActiveUPB.apply(pd.to_numeric).fillna(0)
df_DefaultUPB = df_DefaultUPB.apply(pd.to_numeric).fillna(0)
df_PrincipalACR = df_PrincipalACR.apply(pd.to_numeric).fillna(0)


# In[7]:


####Clean Default Data####
#df_DefaultUPB = df_default.apply(pd.to_numeric).fillna(0)
Logic = 'New'
if (Logic == 'current'):
    ##Current Logic##
    for i in df_DefaultUPB.columns:
        df_DefaultUPB[i] = df_DefaultUPB[i].diff(periods=-1)
    df_DefaultUPB[df_DefaultUPB<0]=0
else:
    ###New Logic###
    for i in range(len(df_DefaultUPB.columns)):
        j = df_DefaultUPB.columns[i]
        if df_DefaultUPB[df_DefaultUPB.columns[i]].nonzero()[0].size != 0:
            df_DefaultUPB.loc[df_DefaultUPB.iloc[:,i].index != df_DefaultUPB[df_DefaultUPB.columns[i]].index[df_DefaultUPB[df_DefaultUPB.columns[i]].nonzero()[0][-1]],df_DefaultUPB.columns[i]] = 0
        #df_default[i] = df_default[i].diff(periods=-1)
#######
#df_DefaultUPB = Mapping(df_DefaultUPB,'WAM ID','Risk Bucket',RiskMap)


# In[8]:


### Clean the Active UPB ####
for i in range(len(df_DefaultUPB.columns)):
    #j = df_ActiveUPB.columns.get_loc(df_DefaultUPB.columns[i])
    if df_DefaultUPB[df_DefaultUPB.columns[i]].nonzero()[0].size != 0:
        j=df_DefaultUPB[df_DefaultUPB.columns[i]].nonzero()[0][0]
        #df_DefaultUPB.columns[i].nonzero()[0][-1]
        df_ActiveUPB.loc[0:j-1,df_DefaultUPB.columns[i]] = 0


# In[588]:


#df_DefaultUPB['105810037'].nonzero()[0][0]


# In[590]:


#df_ActiveUPB


# In[9]:


### Clean the ACR Principal ####
for i in df_PrincipalACR.columns:
    idx1 = df_ActiveUPB[i].index[df_ActiveUPB[i]==0]
    idx2 = df_PrincipalACR[i].index
    df_PrincipalACR[i][idx1.intersection(idx2)] = 0


# In[562]:


#a= df_ActiveUPB[df_PrincipalACR.columns[0]].subtract(df_PrincipalACR[df_PrincipalACR.columns[0]],fill_value=0)
#a.sort_index(ascending=False)
#df.index[df['BoolCol'] == True].tolist()


# In[563]:


#df_PrincipalACR.shift(periods=-1)


# In[564]:


#df_ActiveUPB[df_PrincipalACR.columns[0]]


# In[542]:


#df_PrincipalACR['105810001']==0


# idx1 = df_ActiveUPB['105810001'].index[df_ActiveUPB['105810001']==0]
# idx2 = df_PrincipalACR['105810001'].index
# 
# df_PrincipalACR['105810001'][idx1.intersection(idx2)] = 0

# df_PrincipalACR['105810001']

# any(df_PrincipalACR['105810001'].index in df_PrincipalACR['105810001'].index[np.nonzero(df_PrincipalACR['105810001'])])

# In[592]:


df_ActiveUPB.to_csv('U:/Ratio/Deal1058/df_current_Deal1058_cleaned.csv')
df_DefaultUPB.to_csv('U:/Ratio/Deal1058/df_defaults_Deal1058_cleaned.csv')
df_PrincipalACR.to_csv('U:/Ratio/Deal1058/df_acrprin_Deal1058_cleaned.csv')


# In[10]:


df_DefaultUPB = Mapping(df_DefaultUPB,'WAM ID','Risk Bucket',RiskMap)
df_ActiveUPB = Mapping(df_ActiveUPB,'WAM ID','Risk Bucket',RiskMap)
df_PrincipalACR = Mapping(df_PrincipalACR,'WAM ID','Risk Bucket',RiskMap)


# In[11]:


#RiskMap


# In[24]:


dfCDR = CalculatingCDR_Deal(df_DefaultUPB,df_ActiveUPB,df_PrincipalACR,'CumDefault')
dfCDR.to_csv('U:/Ratio/Deal1058/df_CDR_Deal1058_Bucket_cumdefault_auto2.csv')
dfCDR.index = pd.to_datetime(dfCDR.index)


# In[382]:


dfnew = df_single.groupby('Default Checks')
dfnew2 = df_single2.groupby('Default Checks')
#df_single = df_UPBFull.apply(pd.to_numeric)
df_current = dfnew2.get_group('Current')
df_default = dfnew.get_group('Defaulted')


# In[367]:


#df_default


# In[383]:


df_current = df_current.drop(columns=['Default Checks'])
df_current = df_current.set_index('Date').T

df_default = df_default.drop(columns=['Default Checks'])
df_default = df_default.set_index('Date').T


# In[384]:


df_current.columns = df_current.columns.astype(str)
df_default.columns = df_default.columns.astype(str)


# In[385]:


####Clean Current Data####
df_current = df_current.apply(pd.to_numeric).fillna(0)
df_current = Mapping(df_current,'WAM ID','Risk Bucket',RiskMap)

####Clean Default Data####
df_default = df_default.apply(pd.to_numeric).fillna(0)
Logic = 'current'
if (Logic == 'current'):
    ##Current Logic##
    for i in df_default.columns:
        df_default[i] = df_default[i].diff(periods=-1)
    df_default[df_default<0]=0
else:
    ###New Logic###
    for i in range(len(df_default.columns)):
        j = df_default.columns[i]
        if df_default[df_default.columns[i]].nonzero()[0].size != 0:
            df_default.loc[df_default.iloc[:,i].index != df_default[df_default.columns[i]].index[df_default[df_default.columns[i]].nonzero()[0][-1]],df_default.columns[i]] = 0
        #df_default[i] = df_default[i].diff(periods=-1)
#######
df_default = Mapping(df_default,'WAM ID','Risk Bucket',RiskMap)


# df_default = df_default.apply(pd.to_numeric).fillna(0)

# for i in range(len(df_default.columns)):
#     j = df_default.columns[i]
#     print(j)
#     df_default.loc[df_default.iloc[:,i].index != df_default[df_default.columns[i]].index[df_default[df_default.columns[i]].nonzero()[0][-1]],df_default.columns[i]] = 0
#     #df_default[j] = df_default[j].diff(periods=-1)

# In[386]:


#MDR = pd.Series.diff(tempdf,periods=-1)/pd.Series.shift(df_ActiveUPB[df_ActiveUPB.columns[i]],periods=-1)


# In[387]:


#Plot Default Rate by deal
dfCDR = CalculatingCDR_Deal(df_default,df_current)
dfCDR.to_csv('U:/Ratio/WAMCAM_Upload/df_CDR_Deal1058_NoteSaleCur_bybucket_Cur_valid.csv')
dfCDR.index = pd.to_datetime(dfCDR.index)


# In[388]:


dfCDR


# In[389]:


### Plotting ###
# dfCDR.plot()
fig = pyplot.figure()
ax = dfCDR.plot()
ax.set_title('CDR by Risk Bucket Deal 1058')


# In[ ]:


#######################################################################################


# In[147]:


df_defaults_bygroup = Mapping(df_defaults,'Deal Name & Moniker','Loan Sector',DealMap)


# In[148]:


#df_defaults_bygroup = Mapping(df_defaults,'Deal Name & Moniker','Loan Sector',DealMap)
df2_cleaned_bygroup = df_defaults_bygroup.drop([col for col in df_defaults_bygroup.columns if any(x in col for x in Dropgroups)],axis=1)
#df2_cleaned_bygroup


# In[66]:


df_defaults_bygroup.to_csv('U:/Ratio/WAMCAM_Upload/Defaults_bySector_final.csv')


# In[149]:


df_ActiveUPB_bygroup = Mapping(df_ActiveUPB,'Deal Name & Moniker','Loan Sector',DealMap)
df_ActiveUPB_cleaned_bygroup = df_ActiveUPB_bygroup.drop([col for col in df_ActiveUPB_bygroup.columns if any(x in col for x in Dropgroups)],axis=1)
#df_ActiveUPB_cleaned_bygroup


# In[150]:


#Plot Default Rate by Loan Sector
dfCDR = CalculatingCDR(df2_cleaned_bygroup,df_ActiveUPB_cleaned_bygroup)
dfCDR.to_csv('U:/Ratio/WAMCAM_Upload/CDR_byGroup_final.csv')
ax = dfCDR.plot()
ax.grid()


# In[ ]:


fig = pyplot.figure()
ax = pyplot.gca()
ax.plot(dfCDR)
ax.relim()      # make sure all the data fits
ax.autoscale()


# # Calculate Severity

# In[257]:


#Loss Severity:
#Monthly Loss Amount(<=> (Defaults - Loss Mit Proceeds) / Whole Liquidated UPB


# In[113]:


#Read in the Full Liquidated UPB#
df_Liq_UPB = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_GoesDefault.csv',header=0,parse_dates=[0],index_col=0)
#df_Liq_UPB = df_Liq_UPB.drop([col for col in df_Liq_UPB.columns if any(x in col for x in Dropgroups)],axis=1)
df_Liq_UPB = cleandata(df_Liq_UPB)


# #Read in the Full Liquidated UPB#
# df_Liq_UPB = pd.read_csv('U:/Ratio/Liq_UPB.csv',header=0,parse_dates=[0],index_col=0)
# #df_Liq_UPB = df_Liq_UPB.drop([col for col in df_Liq_UPB.columns if any(x in col for x in Dropgroups)],axis=1)
# df_Liq_UPB = cleandata(df_Liq_UPB)
# 

# In[ ]:


#df_Liq_UPB.columns


# In[114]:


#Read in the Liquidated & Paid In Full UPB#
df_LiqPIF_UPB = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_PIF.csv',header=0,parse_dates=[0],index_col=0)
#df_LiqPIF_UPB = df_LiqPIF_UPB.drop([col for col in df_LiqPIF_UPB.columns if any(x in col for x in Dropgroups)],axis=1)
df_LiqPIF_UPB = cleandata(df_LiqPIF_UPB)


# In[274]:


##################Calculation Starts#################
##Step 1 - Load the Loans that has defaulted##
df_defaults = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_FullDefaulted_byWAMID_Resi.csv',header=0,parse_dates=[0],index_col=0)
df_defaults = df_defaults.drop([col for col in df2.columns if any(x in col for x in DropID)],axis=1)
df_defaults.replace(to_replace = '-', value = '', inplace = True)
df_defaults = df_defaults.apply(pd.to_numeric)
df_defaults = df_defaults.loc[:, ~(df_defaults.iloc[0]>0)]


# In[275]:


df_defaults.columns


# In[276]:


##Step 2 - Loss Mit Proceeds##
df_CompletedLossMit = pd.read_csv('U:/Ratio/WAMCAM_Download/UPB_CompletedLossMitProceeds_byWAMID_Resi.csv',header=0,parse_dates=[0],index_col=0)
df_CompletedLossMit = df_CompletedLossMit.drop([col for col in df2.columns if any(x in col for x in DropID)],axis=1)
df_CompletedLossMit.replace(to_replace = '-', value = '', inplace = True)
df_CompletedLossMit = df_CompletedLossMit.apply(pd.to_numeric)
g = df_CompletedLossMit.groupby(pd.TimeGrouper("M"))
grouped = g.sum()
df_CompletedLossMit_grouped = grouped.sort_index(ascending=False)
#df_defaults = df_defaults.loc[:, ~(df_defaults.iloc[0]>0)]


# In[279]:


#df_CompletedLossMit_grouped
df_defaults = Mapping(df_defaults,'WAM ID','Deal Name & Moniker',LoanMap)
df_CompletedLossMit_grouped = Mapping(df_CompletedLossMit_grouped,'WAM ID','Deal Name & Moniker',LoanMap)


# In[283]:


df_CompletedLossMit_grouped


# In[306]:


dfSeverity = CalculatingSeverity(df_defaults,df_CompletedLossMit_grouped)
dfSeverity = dfSeverity.replace(1,'')
dfSeverity.to_csv('U:/Ratio/WAMCAM_Upload/df_Severity_byDeal_Resi.csv')
dfSeverity
#ax = marker='o'


# In[308]:


dfSeverity.plot(marker='o')


# In[115]:


#Reading in the Loss Mit Proceeds#
df_NetLossProceeds = pd.read_csv('U:/Ratio/LossNetProceeds.csv',header=0,parse_dates=[0],index_col=0)
#df_NetLossProceeds = df_NetLossProceeds.drop([col for col in df_NetLossProceeds.columns if any(x in col for x in Dropgroups)],axis=1)

for i in range(len(df_NetLossProceeds.columns)):
    j=df_NetLossProceeds.columns[i]
    df_NetLossProceeds.loc[df_NetLossProceeds.iloc[:,i].isin(['-']),df_NetLossProceeds.columns[i]]=0
    df_NetLossProceeds[[j]] = df_NetLossProceeds[[j]].apply(pd.to_numeric)

# Summarized by Month End according to the liquidation date #
g = df_NetLossProceeds.groupby(pd.TimeGrouper("M"))
grouped = g.sum()
grouped_final = grouped.sort_index(ascending=False)
#grouped.set_index('Date')

df_NetLossProceeds_final = grouped_final


# In[ ]:


#df_NetLossProceeds_final
#df_NetLossProceeds_final.to_csv('U:/Ratio/LossNetProceeds_grouped.csv')


# In[ ]:


#df_LiqPIF_UPB.columns
#df_Liq_UPB.to_csv('U:/Ratio/df_Liq_UPB_output.csv')


# In[ ]:


#Calculate the severity ratio using actual net loss / liqBalance ex-PIF


# In[116]:


dfSeverity = CalculatingSeverity(df_Liq_UPB,df_LiqPIF_UPB,df_NetLossProceeds_final)

dfSeverity.to_csv('U:/Ratio/Severity_byDeal.csv')


# In[117]:


#Calculate Severity by Groups#
df_Liq_UPB_grouped = Mapping(df_Liq_UPB,'Deal Name & Moniker','Loan Sector',DealMap)
df_LiqPIF_UPB_grouped = Mapping(df_LiqPIF_UPB,'Deal Name & Moniker','Loan Sector',DealMap)
df_NetLossProceeds_grouped = Mapping(df_NetLossProceeds_final,'Deal Name & Moniker','Loan Sector',DealMap)
dfSeverity = CalculatingSeverity(df_Liq_UPB_grouped,df_LiqPIF_UPB_grouped,df_NetLossProceeds_grouped)
dfSeverity.to_csv('U:/Ratio/Severity_byGroup.csv')


# In[ ]:


dfSeverity = CalculatingSeverity(df_Liq_UPB,df_LiqPIF_UPB,df_NetLossProceeds_final)


# In[ ]:


fig = pyplot.figure()
ax = pyplot.gca()
ax.plot(dfSeverity)
ax.relim()      # make sure all the data fits
ax.autoscale()


# In[607]:


#dfSeverity.plot()


# # Data Aggregation - [For Uploading to WAMCAM]

# In[47]:


df_CPR = pd.read_csv('U:/Ratio/CPR_byDeal.csv',header=0,parse_dates=[0],index_col=0)
df_CDR = pd.read_csv('U:/Ratio/CDR_byDeal.csv',header=0,parse_dates=[0],index_col=0)
df_Severity = pd.read_csv('U:/Ratio/Severity_byDeal.csv',header=0,parse_dates=[0],index_col=0)


# df3 = df_CPR.unstack()
# 

# In[48]:


df_CPR = df_CPR.reset_index()
df_CDR = df_CDR.reset_index()
df_Severity = df_CPR.reset_index()


# In[49]:


df_CPR_output = pd.melt(df_CPR, id_vars=["Date"], 
                  var_name=["Deal_ID - Monikar", value_name="CPR")

df_CDR_output = pd.melt(df_CDR, id_vars=["Date"], 
                  var_name="Deal_ID - Monikar", value_name="CDR")

df_Severity_output = pd.melt(df_Severity, id_vars=["Date"], 
                  var_name="Deal_ID - Monikar", value_name="Severity")


# In[253]:


df_CPR_single = pd.read_csv('U:/Ratio/WAMCAM_Upload/CPR-106810771080Deal.csv',header=0,parse_dates=[0],index_col=0)
df_CPR = df_CPR_single.reset_index()
df_CPR_output = pd.melt(df_CPR, id_vars=["Date","Deal Name & Moniker"], 
                  var_name="CPR Type", value_name="CPR")
df_CPR_output


# In[404]:


df_CPR_Agg = pd.read_csv('U:/Ratio/WAMCAM_Upload/df_CPR_byDeal_Resi_Agg.csv',header=0,parse_dates=[0],index_col=0)
df_CPR = df_CPR_Agg.reset_index()
df_CPR_output_agg = pd.melt(df_CPR, id_vars=["Date"], 
                  var_name="Deal Name & Moniker", value_name="CPR")
df_CPR_output_agg['CPR Type'] = 'Agg'


# In[405]:


df_CPR_Agg = pd.read_csv('U:/Ratio/WAMCAM_Upload/df_CPR_byDeal_Resi_AllexPIF.csv',header=0,parse_dates=[0],index_col=0)
df_CPR = df_CPR_Agg.reset_index()
df_CPR_output_allexpif = pd.melt(df_CPR, id_vars=["Date"], 
                  var_name="Deal Name & Moniker", value_name="CPR")
df_CPR_output_allexpif['CPR Type'] = 'All ex-PIF'


# In[406]:


df_CPR_Agg = pd.read_csv('U:/Ratio/WAMCAM_Upload/df_CPR_byDeal_Resi_PIF_Only.csv',header=0,parse_dates=[0],index_col=0)
df_CPR = df_CPR_Agg.reset_index()
df_CPR_pif = pd.melt(df_CPR, id_vars=["Date"], 
                  var_name="Deal Name & Moniker", value_name="CPR")
df_CPR_pif['CPR Type'] = 'Paid in Full'


# In[407]:


df_CPR_upload = pd.concat([df_CPR_output_agg,df_CPR_output_allexpif,df_CPR_pif])


# In[413]:


df_CPR_upload.to_csv("X:/Waterfall\\Bond Surveillance\\Qlik\\WAMCAM_Loan_Data\\df_CPR_upload.csv",index=False)


# In[255]:


df_CPR_byDeal = pd.read_csv('X:\Waterfall\Bond Surveillance\Qlik\WAMCAM_Loan_Data/df_CPR_byDeal_Resi.csv',header=0,parse_dates=[0],index_col=0)
df_CPR = df_CPR_byDeal.reset_index()
df_CPR_output = pd.melt(df_CPR, id_vars=["Date"], 
                  var_name="Deal Name & Moniker", value_name="CPR")
df_CPR_output


# In[309]:


df_Severity_byDeal = pd.read_csv('U:/Ratio/WAMCAM_Upload/df_Severity_byDeal_Resi.csv',header=0,parse_dates=[0],index_col=0)
df_Severity_byDeal = df_Severity_byDeal.reset_index()
df_Severity_byDeal = pd.melt(df_Severity_byDeal, id_vars=["Date"], 
                  var_name="Deal Name & Moniker", value_name="Severity")
df_Severity_byDeal


# In[ ]:


df_CDR_byDeal = pd.read_csv('U:/Ratio/WAMCAM_Upload/df_CDR_byDeal_Resi.csv',header=0,parse_dates=[0],index_col=0)
df_CDR = df_CDR_byDeal.reset_index()
df_CDR_output = pd.melt(df_CDR, id_vars=["Date"], 
                  var_name="Deal Name & Moniker", value_name="CDR")
df_CDR_output


# In[ ]:


###############################Upload to Qlik folder in X:/ drive##############################


# In[310]:


#df_CPR_output.to_csv('U:/Ratio/WAMCAM_Upload/df_CPR-106810771080Deal_upload.csv',index=False)
#df_CDR_output.to_csv('X:/Waterfall/Bond Surveillance/Qlik/WAMCAM_Loan_Data/df_CDR_byDeal_Resi.csv',index=False)
#df_CPR_output.to_csv('X:/Waterfall/Bond Surveillance/Qlik/WAMCAM_Loan_Data/WAMCAM_CPR_byDeal_Resi.csv',index=False)
df_Severity_byDeal.to_csv('X:/Waterfall/Bond Surveillance/Qlik/WAMCAM_Loan_Data/WAMCAM_Severity_byDeal_Resi.csv',index=False)


# In[50]:


dfs = [df_CPR_output, df_CDR_output, df_Severity_output]
for i in dfs:
    i.to_csv("U:\Ratio\WAMCAM_Upload_"+str(i)+".csv")


# In[55]:


df_CPR_output.to_csv("U:\Ratio\WAMCAM_Upload\df_CPR_output.csv",index=False)
df_CDR_output.to_csv("U:\Ratio\WAMCAM_Upload\df_CDR_output.csv",index=False)
df_Severity_output.to_csv("U:\Ratio\WAMCAM_Upload\df_Severity_output.csv",index=False)


# In[42]:


from functools import reduce
#df_final = reduce(lambda left,right: pd.merge(left,right,on='Date'), dfs)


# In[87]:


df_CPR_byGroup = pd.read_csv('U:/Ratio/WAMCAM_Upload/df_CPR_by_sector.csv',header=0,parse_dates=[0],index_col=0)
df_CPR_byGroup = df_CPR_byGroup.reset_index()


# In[88]:


df_CPR_byGroup


# In[90]:


df_CPR_byGroup_WAMCAM = pd.melt(df_CPR_byGroup, id_vars=["Date"], 
                  var_name="Loan Sector", value_name="CPR")


# In[91]:


df_CPR_byGroup_WAMCAM.to_csv("U:\Ratio\WAMCAM_Upload\df_CPR_byGroup_output.csv",index=False)


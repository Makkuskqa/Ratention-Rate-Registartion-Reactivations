from numpy import datetime64, unique
import pandas as pd
import pathlib as Path
import os



file_path = "D:/Windows/Folder"  #RR+REGS+REACT
files = os.listdir(file_path)
df = pd.DataFrame()

for file in files:
    df_temp = pd.read_csv(file_path+"/"+file)
    df_temp['filename'] = file
    df  = df.append(df_temp)


all_players_df = df.groupby(['filename','Partner','Месяц'])['ID игрока'].agg(['count'])
all_players_df = all_players_df.reset_index()
all_players_df.rename(columns = {'count':'Активные'}, inplace = True)
#print(all_players_df)       # FIND ALL NUMBER OF PLAYERS PER MONTH




def RR_Retention():
    global all_players_df
    result_RR_RETENTION = pd.DataFrame()

    data = df['Месяц']
    a = pd.Series(unique(data).tolist())

    N = len(unique(df['Месяц']))
    b = range(1,N+1)

    dictionary = dict(zip(b,a))
    

    for i in range(1, N+1):
        players = df.loc[(df['Месяц'] == dictionary.get(i)) | (df['Месяц'] == dictionary.get(i+1))]

        players_repeat = players.groupby(['filename','Partner', 'ID игрока']).count()
        players_repeat = players_repeat.reset_index()

        players_repeat = players_repeat.loc[(players_repeat['Кол-во игроков'] >1)]

        players_repeat = players_repeat.groupby(['filename', 'Partner']).count()
        players_repeat = players_repeat.reset_index()
        players_repeat['month'] = dictionary.get(i+1)
        players_repeat = players_repeat[['filename','Partner','Кол-во игроков','month']]
        players_repeat.rename(columns = {'Кол-во игроков':'Удержанные', 'month':'Месяц'}, inplace = True)
        result_RR_RETENTION = result_RR_RETENTION.append(players_repeat)
        
    #print(result_RR_RETENTION)    # FIND ALL RETENIAN PLAYERS PER ACTIVE MONTH
    
    merging_result = pd.merge(all_players_df, result_RR_RETENTION, how="left",  on=["filename", "Partner", "Месяц"])
    #print(merging_result)          # MERGING TWO DATAFRAMES


    merging_result['%Retention'] = 1

    for num in range(0, (len(merging_result['filename'])-1)):
        merging_result['%Retention'].iloc[num+1] = (merging_result['Удержанные'].iloc[num+1] / merging_result['Активные'].iloc[num]) *100
    #print(merging_result)           # FIND PERCENT RETENTION
        

    merging_result = merging_result.dropna(subset=['Удержанные'])
    merging_result['%Retention'] = merging_result['%Retention'].map('{:,.2f}%'.format)
    #print(merging_result)



    Regs = df.groupby(['filename','Partner','Месяц', 'Месяц регистрации'])['ID игрока'].agg(['count'])
    Regs = Regs.reset_index()
    Regs.rename(columns = {'count':'REGS'}, inplace = True)
    Regs = Regs.loc[(Regs['Месяц'] == Regs['Месяц регистрации'])]
    Regs = Regs[['filename','Partner','Месяц','REGS']]
    #print(Regs)                       # FIND REGS TO ACTIVE MONTH



    Regs_Merging = pd.merge(merging_result, Regs, how="left",  on=["filename", "Partner", "Месяц"])
    #print(Regs_Merging)

    Regs_Merging['Удержанные'] = Regs_Merging['Удержанные'].astype('int')
    Regs_Merging['React'] = Regs_Merging['Активные'] - (Regs_Merging['Удержанные']+Regs_Merging['REGS'])
    
    #print(Regs_Merging)


    return Regs_Merging.to_excel("D:/Windows/Folder/File.xlsx", engine='xlsxwriter', index=False)

RR_Retention()


